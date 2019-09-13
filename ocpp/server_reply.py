#!/usr/bin/python
'''
Created on 26-Oct-2017

@author: aprateek

CallResult type = 3 or 4
[<MessageTypeId>, "<UniqueId>", {<Payload>}]


Server responses for commands initiated from ChargePoint


MessageType = CALLRESULT
MessageTypeNumber = 3
Direction Server-to-client

MessageType = CALLERROR
MessageTypeNumber = 4
Direction Server-to-client
Initiated by the central system: 

    Cancel Reservation, Change Availability, Change Configuration, Clear Cache, Data Transfer, 
    Get Configuration, Get Diagnostics, Get Local List Version, Remote Start Transaction, Remote Stop Transaction, 
    Reserve Now, Reset, Send Local List, Unlock Connector and Update Firmware
'''


from datetime import datetime, timedelta
from dateutil import parser
import json
import ast
import uuid


class ServerReply:
    type = None
    uuid = None
    body = None
    error_name = None
    error_message = None
    
    
    
    def __init__(self, message_array):
        self.type = message_array[0]
        self.uuid = message_array[1]
        if self.type == 1:
            print ("Error: Not allowed")
        elif self.type == 2:
            print ("Error: Request not expected, only replies are")
        elif self.type == 3:
            # [3,"c19023d3",{"currentTime":"2017-10-22T11:06:04.477Z"}]
            self.body = message_array[2]
        elif self.type == 4:
            # [4,"c19023d3","InternalError","Internal services failed while processing of the payload","SQL [insert into `evc`.`connector_status` (`connector_pk`, `status_timestamp`, `status`, `error_code..."]
            self.error_name = message_array[2]
            self.error_message = message_array[3]
        else:
            self.type = -1
            
            
    def getUuid(self):
        return self.uuid
    
    def isError(self):
        return self.error_name != None
    
    def getError(self):
        return self.error_name, self.error_message
    
    """
      {status: 'Accepted', currentTime: '2013-02-01T15:09:18Z',heartbeatInterval: 1200 },"""
    """[3,"c19023d3",{"currentTime":"2017-10-22T11:06:04.477Z"}]"""
      
    def getBootNotficationStatus(self):
        return self.body["status"]
    
    def getAuthorize(self):
        print("Body =%s" %self.body)
        return self.body["idTagInfo"]["status"]
    
    def getCurrentTime(self):
        return parser.parse(self.body["currentTime"])
    
    def getHeartbeatInterval(self):
        return int(self.body["heartbeatInterval"])
    
    """Authorize [3,"c19023d3",{"idTagInfo":{"status":"Invalid"}}]
    [3,"c19023d3",{"transactionId":6,"idTagInfo":{"status":"Accepted","expiryDate":"2017-10-23T06:38:05.554Z"}}]
    """

    def getStatus(self):
        return self.body["idTagInfo"]["status"]
    
    def getExpiry(self):
        return parser.parse(self.body["idTagInfo"]["expiryDate"])
    
    """StartTransactionResponse{"transactionId":6,"idTagInfo":{"status":"Accepted","expiryDate":"2017-10-23T06:38:05.554Z"}"""
    
    def getStartTransactionId(self):
        return self.body["transactionId"]
    
    """StopTransaction {"idTagInfo":{"status":"Accepted","expiryDate":"2017-10-23T06:38:05.845Z"}} """
    
    
    """DataTransferResponse: { status: 'Accepted', data: '{"transactionId":1,"maxPower":3,"expiration":'+'"2013-01-31T15:00:00Z","userWarning":false}' },"""
    
    
    
    
if __name__ == "__main__":
    print("Test")
    
    r = ServerReply('c19023d3', '[3,"c19023d3",{"transactionId":6,"idTagInfo":{"status":"Accepted","expiryDate":"2017-10-23T06:38:05.554Z"}}]')
    print(r.getStartTransactionId())
    print(r.getExpiry())
    print(r.getStatus())
    
    
    