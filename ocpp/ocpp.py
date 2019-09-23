#!/usr/bin/env python

from pprint import pprint
from datetime import datetime, timedelta
from dateutil import parser
import websocket
import thread
import time
import os
import sys
import logging
import traceback
import json
import ast
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

logging.getLogger().setLevel(logging.INFO)
platform = platform.system()  # Linux, Darwin, Windows

pid_file = dir_path + '/ocpp.pid'
log_file_name = dir_path + '/http/slave/ocpp.html'
uuid = None
req = None
registry = request_registry.RequestRegistry()
conf = None
ws = None
openevse_serial = None

SIP = os.popen('cat ../system.properties | grep ocpp_server  | cut -d"=" -f 2').read()
SSL = os.popen('cat ../system.properties | grep ssl_enabled  | cut -d"=" -f 2').read()

ocpp_cmd = AsyncCom(AsyncCom.OCPP_CMD_FILE)
ocpp_resp = AsyncCom(AsyncCom.OCPP_RESP_FILE)
clientReply = client_reply.ClientReply()

sm = StateMachine()


def on_message(ws, message):
    global registry
    global clientReply
    global conf
    
    try:
        logging.info("on_message=" + message)
        with open(log_file_name, 'a') as f: f.write('>>' + message + '</br>\n')
        mv = ast.literal_eval(message)
        cmd_number = int(mv[0])
        if cmd_number == 2:  #### CALLS FROM SERVER #######
           processServerCall(mv)
        elif cmd_number == 3:  #### SERVER RESPONSES ######
            processServerResponse(mv)
        elif cmd_number == 4:  ### ERRORS ####
            processServerErrorResponse(mv)
        else:
            logging.fatal("Unknown cmd_number %d" %(cmd_number))
    except:
        logging.warn ("Bad server_resp ")
        traceback.print_exc()

"""
Process commands that are initiated from the server. Currently these are mainly stubs.
Extend these as per the functionality required.
"""
def processServerCall(message_array):
    assert message_array[0] == 2
    
    muuid = message_array[1]
    cmd_name = message_array[2]
    body = message_array[3]
    
    print("Received server_Call " + str(cmd_name) + str(body))
    if cmd_name == 'ReserveNow':
        # [2,"77cacf94-72f2-4e47-a4c7-380dec56b889","ReserveNow",{"connectorId":1,"expiryDate":"2017-10-31T17:09:00.000Z","idTag":"1234","reservationId":6}]
        serverCall = server_call.ServerCall(muuid, cmd_name, body)
        logging.info("Reservation Id " + str(serverCall.getReservationId()))
        logging.info("Reservation Expiry " + str(serverCall.getReservationExpiry().utcnow()))
        logging.info("Connector Id " + str(serverCall.getReservationConnectorId()))
        logging.info("Id Tag " + serverCall.getReservationIdTag())
        conf.setReservation(serverCall.getReservationId(), serverCall.getReservationConnectorId(), serverCall.getReservationIdTag(), utils.timestamp(cmd.getReservationExpiry()), utils.timestamp(datetime.utcnow()))
        sendReply(ws, clientReply.getStatus(muuid, "Accepted"))
    elif cmd_name == 'CancelReservation':
        # [2,"54762587-30c9-4cbd-b1be-aa3458e089db","CancelReservation",{"reservationId":6}]
        serverCall = server_call.ServerCall(muuid, cmd_name, body)
        logging.info("Reservation Id " + str(serverCall.getReservationId()))
        datastore.cancelReservation(serverCall.getReservationId())
        sendReply(ws, clientReply.getStatus(muuid, "Accepted"))
    elif cmd_name == 'ClearCache':
        sendReply(ws, clientReply.getStatus(muuid, "Accepted"))
    elif cmd_name == 'GetConfiguration':
        sendReply(ws, clientReply.getStatus(muuid, "Accepted"))
    elif cmd_name == 'ChangeAvailability':
        serverCall = server_call.ServerCall(muuid, cmd_name, body)
        connectorId, type = serverCall.getChangeAvailability()
        # ignoring connector id, as with OpenEVSE there is only one connector
        if type == "Operative":
            result = openevse_serial.status('enable')
            logging.info("OpenEVSE response = %s" % result)
            if "connect" in result:
                sendReply(ws, clientReply.getStatus(muuid, "Accepted"))
        elif type == "Inoperative":
            result = openevse_serial.status('disable')
            logging.info("OpenEVSE response = %s" % result)
            if result == "disabled":
                sendReply(ws, clientReply.getStatus(muuid, "Accepted"))

"""
Process replies that come from the server in response to chargepoint actions. Currently these are mainly stubs.
Extend these as per the functionality required.
"""
def processServerResponse(message_array):
    #[3,"uuid",{body}]
    global registry
    
    assert message_array[0] == 3
    
    muuid = message_array[1]
    body = message_array[2]
    
    print("Received server_response %s" %str(body))
    client_cmd = str(registry.getClientCallCommand(muuid)) # get the initiating client command from the registry
    logging.info("Response from server %s for client call %s"%(str(body), client_cmd))
    serverReply = server_reply.ServerReply(message_array)
    if client_cmd == "BootNotification":
        logging.info ("BootNotification=" + serverReply.getBootNotficationStatus())
        logging.info ("HB Interval=" + str(serverReply.getHeartbeatInterval()))
    elif client_cmd == "Heartbeat":
        logging.info ("HB received Server time = " + str(serverReply.getCurrentTime()))
    elif client_cmd == "StatusNotification":
        logging.info ("StatusNotification received....")
    elif client_cmd == "Authorize":
        logging.info ("StatusNotification received...." + str(serverReply.getAuthorize()))
        ocpp_resp.write(client_cmd, str(serverReply.getAuthorize()))
        if serverReply.getAuthorize() != "Accepted": sm.reset()
    elif client_cmd == "StartTransaction":
        logging.info ("StatusNotification received...." + str(serverReply.getStatus()) + str(serverReply.getStartTransactionId()))
        ocpp_resp.write(client_cmd, str(serverReply.getStartTransactionId()))
        sm.startCharging(serverReply.getStartTransactionId())
    elif client_cmd == "StopTransaction":
        logging.info ("StopNotification received...." + str(serverReply.getStatus()))
        ocpp_resp.write(client_cmd, str(serverReply.getStatus()))
    else:
        logging.info ("Unknown server_resp " + client_cmd)
     

"""
Process errors that come from the server in response to chargepoint actions. Currently these are mainly stubs.
Extend these as per the functionality required.
"""
def processServerErrorResponse(message_array):
    global registry
    assert message_array[0] == 4
    
    muuid = message_array[1]
    body = message_array[2]
    
    print("Received server_Error %s" % str(body) )
    client_cmd = registry.getClientCallCommand(muuid) 
    logging.info("FATAL  Error %s for client_call %s "  %(body, client_cmd ))
    if client_cmd == "BootNotification":
        logging.warn ("Boot Notification Failed")
    elif client_cmd == "Heartbeat":
        logging.warn ("HB failed")
    elif client_cmd == "StatusNotification":
        logging.warn ("StatusNotification Failed")
    elif client_cmd == "Authorize":
        logging.warn ("Authorization Failed")
        ocpp_resp.write(client_cmd, "Failed")
        sm.reset()
    elif client_cmd == "StartTransaction":
        logging.warn ("StartTransaction Failed")
        ocpp_resp.write(client_cmd, "Failed")
    elif client_cmd == "StopTransaction":
        logging.warn ("StopNotification Failed")
        ocpp_resp.write(client_cmd, "Failed")
    else:
        logging.info ("Unknown server_resp %s" % client_cmd)
                
                
def on_error(ws, error):
    logging.info("on_error: Error received %s" % error)


def on_close(ws):
    logging.info ("on_close: ### closed ")


def on_open(ws):
    global uuid
    global clientCall
    global conf
    
    try:
        sendRequest(ws, clientCall.getBootNotification())
        sendRequest(ws, clientCall.getStatusNotification(1, "Available", "NoError", "", ""))
        sendRequest(ws, clientCall.getHeartbeat())
    
        def heartbeat(*args):
            while True:
                try:
                    time.sleep(int(conf.getValue("heartbeatInterval")))
                    sendRequest(ws, clientCall.getHeartbeat()) 
                except:
                    traceback.print_exc()
                    sys.exit()    
    
        def processAuthCommand():
            while True:
                cmdv = ocpp_cmd.read()
                if cmdv is not None:
                    if cmdv[0] == 'Authorize':
                        logging.info("Authenticate %s %s" % (clientCall.getAuthorize(cmdv[1])))
                        sendRequest(ws, clientCall.getAuthorize(cmdv[1]))
                        sm.login(cmdv[1])
                    else:
                        logging.info("OCPP Unknown command %s" % cmdv)

        def checkOpenEvse():
            global tstore
            global openevse
            
            logging.info("created= openevse.SerialOpenEVSE()")
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
                            sendRequest(ws, clientCall.getStopTransaction(sm.getUsername(), sm.getTransactionId(), 20))
                            sm.stopCharging()
                        else:
                            sm.connect()
                    elif status == "charging":
                        logging.info("Status=%s" % status)
                        sendRequest(ws, clientCall.getStartTransaction(sm.getUsername(), "0"))
                    elif status == "disabled":
                        sm.disconnect()
                        logging.info("Status=%s" % status)
                    elif status == "enable":
                        sm.connect()
                        logging.info("Status=%s" % status)
                    elif status is not None:
                        logging.info("Status=%s" % status)
                except:
                    logging.error("Exception occurred", exc_info=True)
                    continue
                    
        # thread.start_new_thread(heartbeat, ()) 
        thread.start_new_thread(processAuthCommand, ()) 
        thread.start_new_thread(checkOpenEvse, ()) 
    except:
        traceback.print_exc()
        sys.exit()    


def sendRequest(ws, uuid_message):
    global registry
    
    cuuid, cmdv = uuid_message
    logging.info ("Sending Request " + json.dumps(cmdv))
    with open(log_file_name, 'a') as f: f.write('<<' + json.dumps(cmdv) + '</br>\n')
    registry.put(cuuid, cmdv)
    ws.send(json.dumps(cmdv))

    
def sendReply(ws, message):
    
    logging.info ("Sending Reply " + json.dumps(message))
    with open(log_file_name, 'a') as f: f.write('<<<' + json.dumps(message) + '</br>\n')
    ws.send(json.dumps(message))


def main():
    global uuid
    global clientCall
    global ws
    global openevse_serial
    
    try:
        openevse_serial = openevse.SerialOpenEVSE()
        uuid = utils.getUuid()
        clientCall = client_call.ClientCall()
        
        if "yes" in SSL.lower():
            websocket.enableTrace(True)
            ws = websocket.WebSocketApp("wss://" + SIP + "/steve/websocket/CentralSystemService/" + uuid,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close,
                                        header=[ "Sec-WebSocket-Protocol: ocpp1.5"])
        else:
            websocket.enableTrace(True)
            ws = websocket.WebSocketApp("ws://" + SIP + "/steve/websocket/CentralSystemService/" + uuid,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close,
                                        header=[ "Sec-WebSocket-Protocol: ocpp1.5"])
        ws.on_open = on_open
        ws.run_forever()
        openevse_serial.lcd_backlight_color("teal")
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

