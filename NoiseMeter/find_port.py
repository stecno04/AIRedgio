import usb.core
import usb
import os
from datetime import datetime
import sys

 
info = usb.core.show_devices()
busses = usb.busses()
for bus in busses:
    devices = bus.devices
    for dev in devices:
        print(dev.idVendor, dev.idProduct)
 
 
