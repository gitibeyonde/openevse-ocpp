#!/usr/bin/python
'''
Created on 26-Oct-2017

@author: aprateek
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
        
        
