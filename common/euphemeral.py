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
db_host = dir_path + '/http/slave/motion/.db.db'
uuid_file = dir_path + '/.uuid'

if os.path.exists(uuid_file):
    uuid = open(uuid_file, 'r').read().rstrip('\n')
else:
    uuid = "unknown"

    
class Euphemeral:
    properties = { }
    
    def __init__(self):
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS config ( name TEXT PRIMARY KEY, value TEXT, type TEXT, desc TEXT, created_at INTEGER);")
                    
    def getValue(self, name):
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("SELECT * FROM CONFIG where name='%s'" % name)
                cap = cur.fetchone()
                if cap is not None:
                    value = cap[1]
                    return value
                else:
                    return None
        
    def setValue(self, name, value):
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                #logging.debug("REPLACE INTO CONFIG ( NAME, VALUE ) VALUES ( '%s', '%s') ;" % (name, value))
                cur.execute("REPLACE INTO CONFIG ( NAME, VALUE ) VALUES ( '%s', '%s')  ;" % (name, value))
        self.properties[name] = value
        
    def delValue(self, name):
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("DELETE FROM CONFIG where name='%s'" % name)
     
    def printAllKeys(self):
        with sqlite3.connect(db_host) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("SELECT * FROM CONFIG")
                caps = cur.fetchall()
                for cap in caps:
                    logging.info("Name=%s Value=%s"%(cap[0], cap[1]))