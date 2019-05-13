#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from contextlib import closing

import socket
import time
import threading
import sqlite3
import atexit
import time
import sys, os
import prctl

PID_FILE = '/root/udps.pid'

def cleanup():
    server_socket.close()
    # print "cleanup--"


def main():
    address = ('', 6999)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(address)

    capability = os.popen('cat /root/system.properties | grep capability  | cut -d"=" -f 2').read()

    while True:
        try:
             recv_data, addr = server_socket.recvfrom(512)
             server_socket.sendto("[IBEYONDE]:" + socket.gethostname() + ":" + capability, addr)

        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            pass
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            pass


if os.path.exists(PID_FILE):
    pid = int(open(PID_FILE, 'rb').read().rstrip('\n'))
    count = int(os.popen('ps -ef | grep "%i" | grep -v "grep" | grep "%s" | wc -l ' % (pid, __file__)).read())
    if count > 0:
        print "Already Running as pid: %i" % pid
        sys.exit(1)
# If we get here, we know that the app is not running so we can start a new one...


if __name__ == "__main__":
    def createDaemon():
        try:
            pid = os.fork()
            if pid > 0:
                # print 'PID: %d' %pid
                os._exit(0)
        except OSError, error:
            # print 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror)
            sys.exit(1)

    os.chdir("/")
    # os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            # print 'PID: %d' %pid
            os._exit(0)
    except OSError, error:
        # print 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror)
        sys.exit(1)

    pf = open(PID_FILE, 'wb')
    pf.write('%i\n' % os.getpid())
    pf.close()
    
    
    prctl.set_name("udps")
    main()

