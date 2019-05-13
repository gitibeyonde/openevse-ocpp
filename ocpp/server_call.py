#!/usr/bin/python
'''
Created on 26-Oct-2017

@author: aprateek
'''


from datetime import datetime, timedelta
from dateutil import parser
import json
import ast
import uuid


""" Change Configuration, Clear Cache, Data Transfer, Get Diagnostics, Get Local List Version, 
Remote Start Transaction, Remote Stop Transaction,  Reset, Send Local List, Unlock Connector and Update Firmware. """

class ServerCall:
    uuid = None
    body = None
    command = None
    
    
    
    def __init__(self, uuid, command, body):
        self.uuid = uuid
        self.command = command
        self.body = body
        
        
    def getUuid(self):
        return self.uuid
    
    def getCommand(self):
        return self.command
    
    """[2,"3205abf6-5d9d-41b5-9bcb-cdc87befc417","ChangeAvailability",{"connectorId":0,"type":"Operative"}]"""
             
    def getChangeAvailability(self):
        return self.body['connectorId'], self.body['type']
    
    """ReserveNowRequest: {  connectorId: 0,  expiryDate: "2013-02-01T15:09:18Z", idTag: "044943121F1D80",  parentIdTag: "", reservationId: 0  } """
    
    def getReservationId(self):
        return self.body['reservationId']
    
    def getReservationExpiry(self):
        return parser.parse(self.body["expiryDate"])
    
    def getReservationConnectorId(self):
        return self.body["connectorId"]
    
    def getReservationIdTag(self):
        return self.body["idTag"]
    
    """CancelReservationRequest: {reservationId: 0 },"""
    
    
    """ GetConfigurationRequest: { key: ['KVCBX_PROFILE'] }"""
    
    def getConfigurationKey(self):
        return self.body["key"]
    
    
if __name__ == "__main__":
    print("Test")
    
    r = ServerCall('c19023d3', '[3,"c19023d3",{"transactionId":6,"idTagInfo":{"status":"Accepted","expiryDate":"2017-10-23T06:38:05.554Z"}}]')
    print(r.getStartTransactionId())
    print(r.getExpiry())
    print(r.getStatus())
    
    