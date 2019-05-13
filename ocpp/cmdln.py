#!/usr/bin/env python3

import sys
import logging
import pathlib

dir_path = str(pathlib.Path(__file__).resolve().parent.parent)
sys.path.append(dir_path + '/common/')

from async_com import AsyncCom

logging.getLogger().setLevel(logging.INFO)

cur_cmd = dir_path + '/http/slave/motion/cmd'
cur_resp = dir_path + '/http/slave/motion/resp'
serial_cmd = dir_path + '/http/slave/motion/scmd'
serial_resp = dir_path + '/http/slave/motion/sresp'

def help():
    print("Commands: RFID <name>; Start; Stop;")

   
ocpp_cmd = AsyncCom(AsyncCom.OCPP_CMD_FILE)
ocpp_resp = AsyncCom(AsyncCom.OCPP_RESP_FILE)
serial_cmd = AsyncCom(AsyncCom.SERIAL_CMD_FILE)
serial_resp = AsyncCom(AsyncCom.SERIAL_RESP_FILE)

# print('00VCNAiTP7zzzqsZLbT3', 'tIrBKzpACDpNc9il3Vbn', 'vvQkJf9kOhbTb2phnhvK', 'd6gsNICFc5UQq4mxwpnV', 'GboT0VGSWWKLcKxCoZaS', 'nyckV0qKPb0ldl5jCsD5', 'ZXao5yhT9Y73hsbFot5L')
if len(sys.argv) == 1:
    help()
else:
    cmdName = sys.argv[1]
    if cmdName.lower() == 'help':
        help()
    elif cmdName == 'connect':
        serial_cmd.write("Connect", [""])
        print("Connect send")
        print(ocpp_resp.read())
    elif cmdName == 'start':
        serial_cmd.write("StartCharging", [""])
        print("StartCharging charging sent")
        print(ocpp_resp.read())
    elif cmdName == 'stop':
        serial_cmd.write("StopCharging", [""])
        print("StopCharging charging sent")
        print(ocpp_resp.read())
    elif cmdName == 'disconnect':
        serial_cmd.write("Disconnect", [""])
        print("Disconnect sent")
        print(ocpp_resp.read())
    elif cmdName.startswith('rfid'):
        if len(sys.argv) < 3:
            logging.info("You need to provide the rfid value as $rfid <value>")
        else:
            ocpp_cmd.write("Authorize", [ sys.argv[2] ])
            response = ocpp_resp.read()
            if response is None:
                print("User %s authentication failed" % sys.argv[2])
            else: 
                print("User %s authenticated" % sys.argv[2])
    elif cmdName == 'quit' or cmdName == 'exit':
        print("EVSE reset")
        sys.exit()
    else:
        help()

