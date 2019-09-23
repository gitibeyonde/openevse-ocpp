#!/usr/bin/env python

import openevse
import time

def callback(states):
    print("State is %s"%states)


o = openevse.SerialOpenEVSE(status_callback=callback)


print (o.current_capacity())

print(o.get_status_change())


print(o.status())

print(o.current_capacity())

print(o.ammeter_settings())
