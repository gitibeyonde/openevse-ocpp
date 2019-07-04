#!/usr/bin/env python

from pprint import pprint
from datetime import datetime, timedelta
from dateutil import parser
import websocket
import _thread
import time
import os
import sys
import logging
import traceback
import json
import ast
import client_call
import request_registry
import client_call
import client_reply
import server_call
import server_reply
import pathlib
import platform
import threading
import traceback
dir_path = str(pathlib.Path(__file__).resolve().parent.parent)
sys.path.append(dir_path + '/common/')
sys.path.append(dir_path + '/openevse/')

import datastore
import utils
import openevse
from async_com import AsyncCom 
from state_machine import StateMachine


logging.getLogger().setLevel(logging.DEBUG)
platform = platform.system()  # Linux, Darwin, Windows

pid_file = dir_path + '/ocpp.pid'
log_file_name = dir_path + '/http/slave/ocpp.html'
uuid = None
req = None
registry = None
conf = None
ws = None
SIP = os.popen('cat ../system.properties | grep ocpp_server  | cut -d"=" -f 2').read()

ocpp_cmd = AsyncCom(AsyncCom.OCPP_CMD_FILE)
ocpp_resp = AsyncCom(AsyncCom.OCPP_RESP_FILE)

sm = StateMachine()

def on_message(ws, message):
    global registry
    global server_resp
    global client_cmd
    global conf
    
    try:
        logging.info("on_message=" + message)
        with open(log_file_name, 'a') as f: f.write('>>' + message + '</br>\n')
        mv = ast.literal_eval(message)
        muuid = mv[1]
        if mv[0] == 2: 
            print("Received server_resp " + str(mv[1]) + str(mv[2]))  
            if mv[2] == 'ReserveNow':
                # [2,"77cacf94-72f2-4e47-a4c7-380dec56b889","ReserveNow",{"connectorId":1,"expiryDate":"2017-10-31T17:09:00.000Z","idTag":"1234","reservationId":6}]
                cmd = server_reply.ServerReply(mv[1], mv[2], mv[3])
                logging.info("Reservation Id " + str(cmd.getReservationId()))
                logging.info("Reservation Expiry " + str(cmd.getReservationExpiry().utcnow()))
                logging.info("Connector Id " + str(cmd.getReservationConnectorId()))
                logging.info("Id Tag " + cmd.getReservationIdTag())
                
                conf.setReservation(cmd.getReservationId(), cmd.getReservationConnectorId(), cmd.getReservationIdTag(), utils.timestamp(cmd.getReservationExpiry()), utils.timestamp(datetime.utcnow()))
        
                sendReply(ws, server_resp.getStatus(mv[1], "Accepted"))
            elif mv[2] == 'CancelReservation':
                # [2,"54762587-30c9-4cbd-b1be-aa3458e089db","CancelReservation",{"reservationId":6}]
                cmd = server_resp.ServerReply(mv[1], mv[2], mv[3])
                logging.info("Reservation Id " + str(cmd.getReservationId()))
                datastore.cancelReservation(cmd.getReservationId())
                sendReply(ws, server_resp.getStatus(mv[1], "Accepted"))
            elif mv[2] == 'ClearCache':
                sendReply(ws, server_resp.getStatus(mv[1], "Accepted"))
            elif mv[2] == 'GetConfiguration':
                sendReply(ws, server_resp.getStatus(mv[1], "Accepted"))
        elif mv[0] == 3:
            logging.info("Received server_resp " + str(mv[2]))
            cmd = registry.get(muuid)
            cmd_name = cmd[2]
            logging.info ("For server_resp name = " + cmd[2])
            resp = server_reply.ServerReply(muuid, message)
            if cmd_name == "BootNotification":
                logging.info ("BootNotification=" + resp.getBootNotficationStatus())
                logging.info ("HB Interval=" + str(resp.getHeartbeatInterval()))
            elif cmd_name == "Heartbeat":
                logging.info ("HB received Server time = " + str(resp.getCurrentTime()))
            elif cmd_name == "StatusNotification":
                logging.info ("StatusNotification received....")
            elif cmd_name == "Authorize":
                logging.info ("StatusNotification received...." + str(resp.getAuthorize()))
                ocpp_resp.write(cmd_name, str(resp.getAuthorize()))
                if resp.getAuthorize() != "Accepted": sm.reset()
            elif cmd_name == "StartTransaction":
                logging.info ("StatusNotification received...." + str(resp.getStatus()) + str(resp.getStartTransactionId()))
                ocpp_resp.write(cmd_name, str(resp.getStartTransactionId()))
                sm.startCharging(resp.getStartTransactionId())
            elif cmd_name == "StopTransaction":
                logging.info ("StopNotification received...." + str(resp.getStatus()))
                ocpp_resp.write(cmd_name, str(resp.getStatus()))
            else:
                logging.info ("Unknown server_resp " + cmd_name)
        elif mv[0] == 4:
            cmd = registry.get(muuid)
            cmd_name = cmd[2]
            logging.info("FATAL  Error for server_resp " + cmd_name + ":" + str(mv[2]) + " == " + str(mv[3]))
            if cmd_name == "BootNotification":
                logging.warn ("Boot Notification Failed")
            elif cmd_name == "Heartbeat":
                logging.warn ("HB failed")
            elif cmd_name == "StatusNotification":
                logging.warn ("StatusNotification Failed")
            elif cmd_name == "Authorize":
                logging.warn ("Authorization Failed")
                ocpp_resp.write(cmd_name, "Failed")
                sm.reset()
            elif cmd_name == "StartTransaction":
                logging.warn ("StartTransaction Failed")
                ocpp_resp.write(cmd_name, "Failed")
            elif cmd_name == "StopTransaction":
                logging.warn ("StopNotification Failed")
                ocpp_resp.write(cmd_name, "Failed")
            else:
                logging.info ("Unknown server_resp " + cmd_name)
    except:
        logging.warn ("Bad server_resp ")
        traceback.print_exc()
    

def on_error(ws, error):
    logging.info("on_error: Error received %s" % error)


def on_close(ws):
    logging.info ("on_close: ### closed ")


def on_open(ws):
    global uuid
    global client_cmd
    global conf
    
    try:
        sendRequest(ws, client_cmd.getBootNotification())
        sendRequest(ws, client_cmd.getStatusNotification(1, "Available", "NoError", "", ""))
        sendRequest(ws, client_cmd.getHeartbeat())
    
        def heartbeat(*args):
            while True:
                try:
                    time.sleep(int(conf.getValue("heartbeatInterval")))
                    sendRequest(ws, client_cmd.getHeartbeat()) 
                except:
                    traceback.print_exc()
                    sys.exit()    
    
        def processAuthCommand():
            while True:
                cmdv = ocpp_cmd.read()
                if cmdv is not None:
                    if cmdv[0] == 'Authorize':
                        logging.info("Authenticate %s %s" % (client_cmd.getAuthorize(cmdv[1])))
                        sendRequest(ws, client_cmd.getAuthorize(cmdv[1]))
                        sm.login(cmdv[1])
                    else:
                        logging.info("OCPP Unknown command %s" % cmdv)

        def checkOpenEvse():
            global tstore
            
            logging.info("created= openevse.SerialOpenEVSE()")
            openevse_serial = openevse.SerialOpenEVSE()
            while True:
                try:
                    time.sleep(1)
                    status = openevse_serial.get_status_change()
                    if status == "not connected":
                        logging.info("Status=%s" % status)
                        sm.disconnect()
                        ocpp_resp.write("Disconnect", "Success")
                    elif status == "connected":
                        logging.info("Status=%s" % status)
                        if sm.isCharging():
                            sendRequest(ws, client_cmd.getStopTransaction(sm.getUsername(), sm.getTransactionId(), 20))
                            sm.stopCharging()
                        else:
                            sm.connect()
                            ocpp_resp.write("Connected", "Success")
                    elif status == "charging":
                        logging.info("Status=%s" % status)
                        sendRequest(ws, client_cmd.getStartTransaction(sm.getUsername(), "0"))
                    elif status is not None:
                        logging.info("Status=%s" % status)
                    else:
                        pass
                except:
                    logging.error("Exception occurred", exc_info=True)
                    continue
                    
        #_thread.start_new_thread(heartbeat, ()) 
        _thread.start_new_thread(processAuthCommand, ()) 
        _thread.start_new_thread(checkOpenEvse, ()) 
    except:
        traceback.print_exc()
        sys.exit()    

def sendRequest(ws, uuid_message):
    global registry
    
    cuuid, cmd = uuid_message
    logging.info ("Sending Request " + json.dumps(cmd))
    with open(log_file_name, 'a') as f: f.write('<<' + json.dumps(cmd) + '</br>\n')
    registry.put(cuuid, cmd)
    ws.send(json.dumps(cmd))

    
def sendReply(ws, message):
    
    logging.info ("Sending Reply " + json.dumps(message))
    with open(log_file_name, 'a') as f: f.write('<<<' + json.dumps(message) + '</br>\n')
    ws.send(json.dumps(message))


def main():
    global uuid
    global client_cmd
    global conf
    global registry
    global resp
    global server_cmd
    global ws
    
    try:
        uuid = utils.getUuid()
        conf = datastore.Datastore()
        client_cmd = client_call.ClientCall(conf)
        registry = request_registry.RequestRegistry()
            
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://" + SIP + "/steve/websocket/CentralSystemService/" + uuid,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    header=[ "Sec-WebSocket-Protocol: ocpp1.5"])
        ws.on_open = on_open
        ws.run_forever()
    except:
        traceback.print_exc()
    
    
if os.path.exists(pid_file) and os.path.getsize(pid_file) > 0:
    pid = int(open(pid_file, 'r').read().rstrip('\n'))
    count = int(os.popen('ps -ef | grep "%i" | grep -v "grep" | grep "%s" | wc -l ' % (pid, __file__)).read())
    if count > 0:
        logging.info("Already Running as pid: %i" % pid)
        sys.exit(1)
# If we get here, we know that the app is not running so we can start a new one...




if __name__ == "__main__":
    try:
        pid = os.fork()
        if pid > 0:
            logging.info('PID: %d' % pid)
            os._exit(0)
        logging.info('PID: %d' % pid)
    except OSError:
        logging.error('Unable to fork.')
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            logging.info('PID: %d' % pid)
            os._exit(0)
        logging.info('pid 2 %d' % pid)
    except OSError:
        logging.error('Unable to fork.')
        sys.exit(1)

    pf = open(pid_file, 'w+')
    pf.write('%i\n' % os.getpid())
    pf.close()
    
    # prctl.set_name("ocpp")
    main()

