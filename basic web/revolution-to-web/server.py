# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 20:56:09 2020

@author: Diogo Alves
"""

from tornado import websocket, web, ioloop
import json
import threading
import numpy
from bitalino import *
import asyncio

# The macAddress variable on Windows can be "XX:XX:XX:XX:XX:XX" or "COMX"
# while on Mac OS can be "/dev/tty.BITalino-XX-XX-DevB" for devices ending with the last 4 digits of the MAC address or "/dev/tty.BITalino-DevB" for the remaining
device = "98:D3:41:FD:4F:D9"
labels = ["nSeq", "I1", "I2", "O1", "O2", "A1", "A2", "A3", "A4", "A5", "A6"]
sampling_rate = 1000
channels = [0,1,2,3,4,5]

#Converts `data` from its native data type to a JSON-compatible `str`.
def tostring(data):
    dtype=type(data).__name__
    if dtype=='ndarray':
        if numpy.shape(data)!=(): data=data.tolist()
        else: data='"'+data.tostring()+'"'
    elif dtype=='dict' or dtype=='tuple':
        try: data=json.dumps(data)
        except: pass
    elif dtype=='NoneType':
        data=''
    elif dtype=='str' or dtype=='unicode':
        data=json.dumps(data)
    
    return str(data)

cl = []

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
        print("CONNECTED")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
        print("DISCONNECTED")
        
def BITalino_handler(mac_addr,srate,ch_mask,labels):
    
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    device=BITalino(mac_addr)
    try:
        
        print(mac_addr)
        print(srate)
        print(ch_mask)
        print("START")
        device.start(SamplingRate=srate, analogChannels=ch_mask)
        data = []
        cols = numpy.arange(len(ch_mask)+5)
        
        while (1):
            data = device.read(25)
            res = "{"
            for i in cols:
                idx = i
                if (i>4): idx=ch_mask[i-5]+5
                res += '"'+labels[idx]+'":'+tostring(data[:,i])+','
            res = res[:-1]
            res+="}"
            if len(cl)>0: cl[-1].write_message(res)
        
    finally:
        device.stop()
        print("STOP")
        device.close()
        print("CLOSE")
        
app = web.Application([(r'/', SocketHandler)])        

if __name__ == '__main__':  
    
    print('LISTENING')
    port=9000
    app.listen(port)
    
    bit = threading.Thread(name='bitalino', target=BITalino_handler,args=(device,sampling_rate,channels,labels))
    bit.start()
    
    print('CONNECTING')
    
    mainLoop = ioloop.IOLoop.instance().start()
