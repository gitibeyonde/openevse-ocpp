#!/bin/bash

set -x

export EVDEVICE_DIR="$(dirname `pwd`)"


#STEP 1

apt-get update
#apt-get -y -q upgrade
locale-gen en_US.UTF-8

apt-get install lsb-release apt-transport-https ca-certificates
apt-get -y install sqlite3 python-pip git python-dateutil
pip install pathlib python-dateutil websocket-client pyserial

apt-get -y -q autoremove
apt-get clean

#STEP 2

chown -R www-data:www-data ${EVDEVICE_DIR}
chmod -R 775 ${EVDEVICE_DIR}
usermod -a -G www-data root

#STEP3

if [ -f /root/.db.db ]; then
    echo "DB exists"
else
    #create config table and populate
    touch /root/.db.db
fi


chown www-data /root/.db.db
chgrp www-data /root/.db.db
chmod 776 /root/.db.db

sqlite3 /root/.db.db "CREATE TABLE IF NOT EXISTS config ( name TEXT PRIMARY KEY, value TEXT, type TEXT, desc TEXT, created_at INTEGER);"
sqlite3 /root/.db.db "CREATE TABLE IF NOT EXISTS reservation ( id INTEGER PRIMARY KEY, connector INTEGER, idtag TEXT, status TEXT, expiry INTEGER, created INTEGER);"
sqlite3 /root/.db.db "REPLACE INTO config VALUES('heartbeatInterval', 120, 'INTEGER', '', datetime());"


# Ephemeral DB

mkdir -p ${EVDEVICE_DIR}/http/slave/motion

if [ -f ${EVDEVICE_DIR}/http/slave/motion/.db.db  ]; then
    echo "DB exists"
else
    #create config table and populate
    touch ${EVDEVICE_DIR}/http/slave/motion/.db.db 
fi

 

sqlite3 ${EVDEVICE_DIR}/http/slave/motion/.db.db "CREATE TABLE IF NOT EXISTS config ( name TEXT PRIMARY KEY, value TEXT, type TEXT, desc TEXT, created_at INTEGER);"
sqlite3 ${EVDEVICE_DIR}/http/slave/motion/.db.db "CREATE TABLE IF NOT EXISTS reservation ( id INTEGER PRIMARY KEY, connector INTEGER, idtag TEXT, status TEXT, expiry INTEGER, created INTEGER);"
sqlite3 /root/evdevice/http/slave/motion/.db.db "REPLACE INTO config VALUES('heartbeatInterval', 120, 'INTEGER', '', datetime());"

chown www-data ${EVDEVICE_DIR}/http/slave/motion/.db.db
chgrp www-data ${EVDEVICE_DIR}/http/slave/motion/.db.db
chmod 776 ${EVDEVICE_DIR}/http/slave/motion/.db.db


#STEP 4

echo "opptitest" > ${EVDEVICE_DIR}/.uuid
