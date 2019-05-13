#!/usr/bin/env python


import time
import serial


ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=5
)


while 1:
    var = raw_input(">>: ")
    print "you entered", var.strip()
    ser.write("%s\r"%var)
    time.sleep(2)
