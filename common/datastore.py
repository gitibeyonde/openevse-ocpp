'''
Created on 26-Oct-2017

@author: aprateek
'''

from __future__ import with_statement
from contextlib import closing
import sqlite3
import os
import logging
import pathlib

logging.getLogger().setLevel(logging.DEBUG)
dir_path = str(pathlib.Path(__file__).resolve().parent.parent)
print(dir_path)
db_host = dir_path + '/../.db.db'
uuid_file = dir_path + '/.uuid'

if os.path.exists(uuid_file):
    uuid = open(uuid_file, 'r').read().rstrip('\n')
else:
    uuid = "unknown"

    
class Datastore:
    properties = { }
    
    def __init__(self):
        self.properties = {
                "uuid": uuid,
                "chargePointVendor": "Ibeyonde",
                "chargePointModel": "OpenEVSE",
                "chargePointSerialNumber": "openevse." + uuid,
                "chargeBoxSerialNumber": "openevse." + uuid,
                "firmwareVersion": "1.0.0",
                "iccid":  uuid,
                "imsi": "",
                "meterType": "DBT NQC-ACDC",
                "meterSerialNumber": "openevse." + uuid,
                "vendorId": "com.ibeyonde.ev"
            }
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("SELECT * FROM CONFIG")
                caps = cur.fetchall()
                for cap in caps:
                    self.properties[cap[0]] = cap[1]
                    
    def getValue(self, name):
        return self.properties[name]
        
    def setValue(self, name, value):
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                logging.debug("INSERT INTO CONFIG ( NAME, VALUE ) VALUES ( %s, %s)" % (name, value))
                cur.execute("INSERT INTO CONFIG ( NAME, VALUE ) VALUES ( %s, %s)" % (name, value))
        self.properties[name] = value
     
    def setReservation(self, resv_id, connector_id, idtag, expiry, created):
        logging.info (str(expiry) + "," + str(created))
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                logging.debug("INSERT INTO reservation ( id, connector, idtag, status, expiry, created ) VALUES ( %d, %d, '%s', 'active', %d, %d)" % (resv_id, connector_id, idtag, expiry, created))
                cur.execute("INSERT INTO reservation ( id, connector, idtag, status, expiry, created ) VALUES ( %d, %d, '%s', 'active', %d, %d)" % (resv_id, connector_id, idtag, expiry, created))
    
    def cancelReservation(self, resv_id):
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                logging.debug("delete from reservation where id=%d" % resv_id)
                cur.execute("delete from reservation where id=%d" % resv_id)
                