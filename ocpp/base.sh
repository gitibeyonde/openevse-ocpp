#!/bin/bash

set -x

source ${SCDIR}/_BASH_INIT_

echo 'source ${SCDIR}/_BASH_INIT_' >> /root/.bashrc

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

if [ -f /root/.db.db ]; then
    echo "DB exists"
else
    #create config table and populate
    touch /root/.db.db
fi

chown www-data /root/.db.db
chgrp www-data /root/.db.db
chmod 776 /root/.db.db

chown -R www-data:www-data /root/evdevice
chmod -R 775 /root/evdevice
usermod -a -G www-data root

${SQLDB} "CREATE TABLE IF NOT EXISTS config ( name TEXT PRIMARY KEY, value TEXT, type TEXT, desc TEXT, created_at INTEGER);"
${SQLDB} "CREATE TABLE IF NOT EXISTS reservation ( id INTEGER PRIMARY KEY, connector INTEGER, idtag TEXT, status TEXT, expiry INTEGER, created INTEGER);"
${SQLDB} "INSERT INTO config VALUES('heartbeatInterval', 120, 'INTEGER', '', datetime());"

hostname=`${SQLDB} "SELECT value FROM config where name='hostname';"`
if [ -n "$hostname" ]; then
    echo "Hostname is set"
    logger `date`,$0, "Hostname is good"
else
    ${SCDIR}/_RESET_UUID_
fi

if dpkg-query -Wf'${db:Status-abbrev}' "lighttpd" | grep -q '^i'; then
    echo "Lighttpd is installed, skipping..."
else
     /root/evdevice/base/lighttpd/install.sh
fi

if dpkg-query -Wf'${db:Status-abbrev}' "hostapd" | grep -q '^i'; then
    echo "hostapd is installed, skipping..."
else    
    apt-get -y -q remove nano
    apt-get -y -q remove ifplugd
    #apt-get -y -q install autossh
    apt-get -y -q install hostapd dnsmasq

    systemctl stop dnsmasq
    systemctl stop hostapd
fi


#set permisison on hostname
chmod 777 /etc/hostname
chown nobody /etc/hostname
chgrp nogroup /etc/hostname


localedef -i en_US -f UTF-8 en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale-gen en_US.UTF-8
dpkg-reconfigure locales

apt-get -y -q autoremove
apt-get clean

${SCDIR}/_SERVICES_RESET_
