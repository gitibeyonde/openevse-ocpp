#!/usr/bin/python
'''
Created on 26-Oct-2017

@author: aprateek

Request Registry is used to store the client_call s.
These are retrived using uuid when the corresponding server_reply is received.

Example client call:
    [2, "02569eb7-7161-40aa-b881-58398e08cade", "Heartbeat", {}]
    
Example server_reply:
    [3,"02569eb7-7161-40aa-b881-58398e08cade",{"currentTime":"2019-09-13T09:59:55.805Z"}]
    
To process server reply, registry helps in linking it to the client call.

'''

from datetime import datetime, timedelta
import json


class RequestRegistry:
    reg = {}
        
    def put(self, uuid, cmd):
        self.reg[uuid] = cmd
        print ("adding value for " + uuid + "=" + json.dumps(cmd))
        
    def get(self, uuid):
        print (" Getting value for " + uuid)
        return self.reg.get(uuid)
    
    def pop(self, uuid):
        return self.reg.pop(uuid)
        
          
    def getClientCallCommand(self, uuid):
        print (" Getting value for " + uuid)
        cmdv = self.reg.get(uuid)
        return cmdv[2]   
