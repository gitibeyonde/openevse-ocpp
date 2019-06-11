# evdevice 0.1 Alpha

This code emulates the serial communication between OpenEVSE and OCPP module. To run this on debian or any other flavour of linux you need to satisfy following dependencies. The isntructions will be for debian for centOS/RedHat you will need similar commands specific to that os:


Step 1

Install pre-requisite packages.

apt-get update
apt-get -y -q upgrade
locale-gen en_US.UTF-8

apt-get install lsb-release apt-transport-https ca-certificates
wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg
echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/php7.3.list
apt-get update
	
apt-get -y install php php-cgi php-sqlite3 php7.0-fpm php-pear sqlite3 lighttpd python-pip git
pip install serial pathlib python-dateutil websocket-client

lighty-enable-mod fastcgi
lighty-enable-mod fastcgi-php
service lighttpd force-reload

apt-get -y -q autoremove
apt-get clean

Step 2

Clone this repo, preferably in root folder. Instructions will assume that the git repo resides in '/root/'.

git clone https://github.com/gitibeyonde/openevse-ocpp.git evdevice

chown -R www-data:www-data /root/evdevice
chmod -R 775 /root/evdevice
usermod -a -G www-data root


Step 3

Setup sqlite DBs. You need to setup two databases one for items that will presist on the sd-card, the other one ephemeral that lives in shared memory and is retained till the information is is sent and acknowledged by the server.

a. Config DB

touch /root/.db.db

chown www-data /root/.db.db
chgrp www-data /root/.db.db
chmod 776 /root/.db.db

sqlite3 /root/.db.db "CREATE TABLE IF NOT EXISTS config ( name TEXT PRIMARY KEY, value TEXT, type TEXT, desc TEXT, created_at INTEGER);"
sqlite3 /root/.db.db "CREATE TABLE IF NOT EXISTS reservation ( id INTEGER PRIMARY KEY, connector INTEGER, idtag TEXT, status TEXT, expiry INTEGER, created INTEGER);"
sqlite3 /root/.db.db "INSERT INTO config VALUES('heartbeatInterval', 120, 'INTEGER', '', datetime());"


b. Ephemeral DB

touch /root/evdevice/http/slave/motion/.db.db  # Map /root/evdevice/http/slave/motion to shared memory

sqlite3 /root/evdevice/http/slave/motion/.db.dbb "CREATE TABLE IF NOT EXISTS config ( name TEXT PRIMARY KEY, value TEXT, type TEXT, desc TEXT, created_at INTEGER);"
sqlite3 /root/evdevice/http/slave/motion/.db.db "CREATE TABLE IF NOT EXISTS reservation ( id INTEGER PRIMARY KEY, connector INTEGER, idtag TEXT, status TEXT, expiry INTEGER, created INTEGER);"
sqlite3 /root/evdevice/http/slave/motion/.db.db "INSERT INTO config VALUES('heartbeatInterval', 120, 'INTEGER', '', datetime());"

chown www-data /root/evdevice/http/slave/motion/.db.db
chgrp www-data /root/evdevice/http/slave/motion/.db.db
chmod 776 /root/evdevice/http/slave/motion/.db.db


Step 4

Setup OCPP Server (Steve) and the emulator device.

On the Steve add a device, by choosing a uuid.
Set this uuid in evdevice/.uuid file.

Step 5

Setup users in Steve. 

Step 6

Run occp.py in evdevice/ocpp folder. This will start the process that listens to status changes form OpenEVSE and contacts OCPP server to pass on information if required.

Step 5.

You can simulate openEVSE by running commands like "./cmdln.py rfid <id of user set in step 5>" in evdevice/ocpp folder. For exampole this command will send an Authorize request to OCPP 1.5J server implementation.

./cmdln.py connect
./cmdln.py start
./cmdln.py stop
./cmdln.py disconnect

The above commands will simulate typical openEVSE charging session.

