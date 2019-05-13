#!/usr/bin/python
'''
Created on 26-Oct-2017

@author: aprateek
'''


from datetime import datetime, timedelta
import json
import ast
import uuid


class ClientReply:
    config = None
    CONFIG = "get_from_config"
    TIMESTAMP = "get_current_timestamp"
    
    def __init__(self, config):
        self.config = config   
        
        
    """ ChangeAvailabilityResponse/ReserveNowResponse/CancelReservationRequest: { status: 'Accepted'}"""
    
    def getStatus(self, uuid, status):
        body = { 
                "status" : str(status)
                }
        return self.getText(uuid, body)
    
    
    def getText(self, guid, body):
        for name in body:
            if body[name] == self.CONFIG:
                body[name] = self.config.getValue(name)
            elif body[name] == self.TIMESTAMP:
                body[name] = str(datetime.now().isoformat())
        cmd = []
        cmd.append(3)
        cmd.append(guid)
        cmd.append(body)
        return cmd
    