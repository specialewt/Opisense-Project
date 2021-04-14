# -*- coding: utf-8 -*-
from tornado import websocket, web, ioloop
import json
import sys
import threading
import numpy as np
import pandas as pd
from opisense import Opisense
import asyncio
import bitalino
from time import sleep
import time

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
        
def new_data()->pd.DataFrame:
    sleep(5)
    rawCol = ['channel_1_raw','channel_2_raw','channel_3_raw','channel_4_raw']
    df = pd.DataFrame(columns = rawCol)
    df.channel_1_raw = np.random.randint(500, size=10)
    df.channel_2_raw = np.random.randint(500, size=10)
    df.channel_3_raw = np.random.randint(500, size=10)
    df.channel_4_raw = np.random.randint(500, size=10)
    res = df.to_json()
    #print(f'Writting this to websocket:\n{res}')    
    return df
    
def NTCconv(x):
        ntc_v = x*3/2**10
        ntc_o = (10**4 * ntc_v)/(3-ntc_v)
        a0 = 1.12764514*10**-3
        a1 = 2.34282709*10**-4
        a2 = 8.77303013*10**-8
        tmp_k = (a0+a1*np.log(ntc_o)+a2*(np.log(ntc_o)**3))**-1
        tmp_c = tmp_k - 273.15
        
        return tmp_c

def main()->None:
    asyncio.set_event_loop(asyncio.new_event_loop())
    myDevice = Opisense()
    rawData = pd.DataFrame()
    try:
        print("START")
        myDevice.start()
        i = 0
        fileName = f'rawData_'+time.strftime("%d_%b_%H_%M", time.localtime())+'.csv'
        while True:
            sleep(5)
            newData = myDevice.read_data()
            rawData = rawData.append(newData)
            #Transform the data.
            newData.channel_1_raw = newData.channel_1_raw.apply(NTCconv)
            newData.channel_2_raw = newData.channel_2_raw.apply(lambda x: ((x/(2**10 -1))-0.5)*100)
            newData.channel_4_raw = newData.channel_4_raw.apply(lambda x: ((3.3*x/(2**10))/0.132))
            res = newData.to_json()
            if len(cl)>0: cl[-1].write_message(res)
            rawData.to_csv(fileName)
            i += 1
            print(i)
            rawData.append(newData)
            res = newData.to_json()
            #print(f'Writting this to websocket{res}')
            # writes JSON to the websocket
            #TODO replace 'res' with DF.JSON
            if len(cl)>0: cl[-1].write_message(res)
            rawData.to_csv(fileName)
    except KeyboardInterrupt:
        pass
    finally:
        #TODO Process  data.
        myDevice.stop()
        print("STOP")
        print("CLOSE")
        sys.exit(0)
        #myDevice.stop()
        print("STOP")
        #device.close()
        print("CLOSE")
        
app = web.Application([(r'/', SocketHandler)])        
if __name__ == '__main__':  
    print('LISTENING')
    port=9000
    app.listen(port)
    bit = threading.Thread(name='bitalino', target=main)
    bit.start() 
    print('CONNECTING')
    mainLoop = ioloop.IOLoop.instance().start()
    sys.exit("Recording Complete.")
