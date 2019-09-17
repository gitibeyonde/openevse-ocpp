#!/usr/bin/python
'''
Created on 26-Oct-2017

@author: aprateek

MessageType = CALL
MessageTypeNumber = 2
Direction Client to Server


[<MessageTypeId>, "<UniqueId>", "<Action>", {<Payload>}]

Initiated by the charge point: Authorize, Boot Notification, Data Transfer, Diagnostics Status Notification, 
    Firmware Status Notification, Heartbeat, Meter Values, Start Transaction, Status Notification and Stop Transaction.
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


class ClientCall:
    config = None
    CONFIG = "get_from_config"
    type = None  # None, CmdLine, Serial, WebCmd
    
    def __init__(self):
        self.config = datastore.Datastore()
     
    def getBootNotification(self, registrationStatus=None):  # Pending, Accepted
        body = { 
                "chargePointVendor" : self.CONFIG,
                "chargePointModel" :  self.CONFIG,
                "chargePointSerialNumber" : self.CONFIG,
                "chargeBoxSerialNumber" : self.CONFIG,
                "firmwareVersion" : self.CONFIG,
                "iccid" : self.CONFIG,
                "imsi" : self.CONFIG,
                "meterType" : self.CONFIG,
                "meterSerialNumber" : self.CONFIG
                }
        return self.getText("BootNotification", body)
    
    def getChangeConfiguration(self):
        # athorization_key
        return
    
    def getHeartbeat(self):
        body = {}
        return self.getText("Heartbeat", body)
    
    def getAuthorize(self, idTag):
        body = {
            "idTag" : idTag
        }
        return self.getText("Authorize", body)
    
    def getStartTransaction(self, idTag, conenctorId=0, reservationId="-1"):
        body = {
            "connectorId": conenctorId,
            "idTag": str(idTag),
            "timestamp": str(datetime.now().isoformat()),
            "meterStart": 0,
            "reservationId": reservationId
            }
        return self.getText("StartTransaction", body)
     
     # {"transactionId", "idTag", "timestamp", "meterStop", "reason", "transactionData" : 
     # [{"timestamp", "sampledValue": {"value", "context", "format", "measurand", "phase", "location", "unit"}}, {"timestamp", "sampledValue"}]})
    def getStopTransaction(self, idTag, transactionId, meterStop):
        body = {
                "transactionId": str(transactionId),
                "idTag": str(idTag),
                "timestamp": str(datetime.now().isoformat()),
                "meterStop": str(meterStop)
            }
        return self.getText("StopTransaction", body)
    
    # [2, id, "MeterValues", {"connectorId": 1, "transactionId": ssid, "meterValue": [{"timestamp": formatDate(new Date()), "sampledValue": [{"value": val}]}]}]);
    def getMeterValue(self, idTag, transactionId, connectorId, meterStop):
        body = {
            "connectorId" :  connectorId,
            "transactionId": str(transactionId),
            "idTag": str(idTag),
            "timestamp": str(datetime.now().isoformat()),
            "meterStop": str(meterStop),
            "transactionData": [
              {
                "timestamp": str(datetime.now().isoformat()),
                "values": [
                  {
                    "value": "0",
                    "unit": "Wh",
                    "measurand": "Energy.Active.Import.Register" 
                  },
                  {
                    "value": "0",
                    "unit": "varh",
                    "measurand": "Energy.Reactive.Import.Register" 
                  }
                ]
              }
            ]
          }
        return self.getText("MeterValue", body)
    
    def getFirmwareStatusNotification(self, status):
        body = {
            "status":  status  # 'DownloadFailed'
        }
        return self.getText("FirmwareStatusNotification", body)
    
    def getDiagnosticsStatusNotification(self, status):
        body = {
            "status" : status  # 'Uploaded'
        }
        return self.getText("DiagnosticsStatusNotification", body)
                                               
    def getDataTransfer(self, function, data):
        body = { 
            "vendorId": self.CONFIG,
            "messageId": str(function),
            "data": str(data)
            } 
        return self.getText("DataTransfer", body)
   
    def getStatusNotification(self, connectorId, status, errorCode, info, vendorErrorCode):
        body = {
            "connectorId": connectorId,
            "status":  status,  # 'Available',
            "errorCode": errorCode,  # 'NoError',
            "info": info,
            "timestamp": str(datetime.now().isoformat()),
            "vendorId": self.CONFIG,
            "vendorErrorCode": vendorErrorCode
            }
        return self.getText("StatusNotification", body)
                                               
    def getText(self, command, body):
        guid = str(uuid.uuid4())
        for name in body:
            if body[name] == self.CONFIG:
                body[name] = self.config.getValue(name)
        cmdv = []
        cmdv.append(2)
        cmdv.append(guid)
        cmdv.append(command)
        cmdv.append(body)
        return guid, cmdv
   
            
if __name__ == "__main__":
    r = ClientCall()
    print (r.getBootNotification())
    print (r.getHeartbeat())
    print (r.getStatusNotification(1, "Available", "NoError", "wtf", "1256"))
    
