#!/usr/bin/python
'''
Created on 26-Oct-2017

@author: aprateek


MessageType = CALL
MessageTypeNumber = 2
Direction Client to Server

This is a response to server initiated action.
The status is usually Accepted, Rejected, Scheduled or Unknown

'''


from datetime import datetime, timedelta
import json
import ast
import uuid
import pathlib
import sys

dir_path = str(pathlib.Path(__file__).resolve().parent.parent)
sys.path.append(dir_path + '/common/')

import datastore

class ClientReply:
    config = None
    CONFIG = "get_from_config"
    TIMESTAMP = "get_current_timestamp"
    
    def __init__(self):
        self.config = datastore.Datastore()
        
        
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
    