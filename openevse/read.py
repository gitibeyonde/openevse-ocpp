#!/usr/bin/env python
          

import time
import serial


ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=3
)


while 1:
    x=ser.readline()
    if len(x)>1:
       print x
    time.sleep(2)
