# BITalino (r)evolution-to-web-api
The BITalino (r)evolution to web API provides a way to stream data from your device to a web page using your main Python distribution.

## Dependencies
* [Python > 3](https://www.python.org/downloads/) or [Anaconda](https://www.anaconda.com/distribution/)
* [Tornado](https://www.tornadoweb.org/en/stable/)
* [Numpy](https://pypi.org/project/numpy/)
* [pySerial](https://pypi.org/project/pyserial/)
* [Pybluez](https://pypi.org/project/PyBluez/) (Not needed for Mac Os)

## Installation
* Make sure you've successfully followed these steps to install Numpy, pySerial, Pybluez and BITalino dependencies https://github.com/BITalinoWorld/revolution-python-api

* **Tornado**
```
pip install tornado
```

## Examples
Don't forget to run your Python Script in an external console to prevent port comunication issues.
* **Python**
```python
from tornado import websocket, web, ioloop
import json
import threading
import numpy
from bitalino import *
import asyncio

device = "00:00:00:00:00:00"
labels = ["nSeq", "I1", "I2", "O1", "O2", "A1", "A2", "A3", "A4", "A5", "A6"]
sampling_rate = 100
channels = [0,1,2,3,4,5]

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
    
    try:
        device=BITalino(mac_addr)
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
```

* **HTML**
 This example will get the message sent by the Python client, change the opacity of your web object and plot a graph based on the number of bits returned from your BITalino.
```html
<!DOCTYPE html>
<html>
<head>
	<title>ClientServer</title>
	<script language="javascript" type="text/javascript" src="jquery.js"></script>
  	<script language="javascript" type="text/javascript" src="jquery.flot.js"></script>
	<script type="text/javascript">
	var ws = new WebSocket("ws://localhost:9000/"); 

        ws.onclose = function (e) {
          document.getElementsByClassName("heart")[0].style.animation=""
          console.log("Connection Closed")
        }
        ws.onmessage = function (e) {
            console.log("Acquisition has begun");

            data = JSON.parse(e.data);
            
            if (data.A1 != undefined) {
              a1Values = data.A1[0];

              document.getElementById("placeholder").setAttribute("value", a1Values);
              document.getElementsByClassName("heart")[0].style.opacity = (a1Values/1024) + "";

              ch1 = 'A1';
              var d1 = []
              for (var i = 0; i < data[ch1].length; i += 1){
                t = data[ch1][i];
                d1.push([i, t]);
              } 
            }

        	$.plot($("#graph"), [ d1 ], {yaxis: {min:0, max: 1024}});
        }
        window.onbeforeunload = function() {
            ws.onclose = function () {};
            ws.close()
	</script>
</head>
<body onload="loadGraph()">
    <div>
        <img src="heart.png" id="placeholder" class="heart" style="width: 20em; margin-left: 9em;"> 
    </div>
    <div id="graph" style="width:600px;height:200px;"></div>
</body>
</html>
```
## Documentation
[BITalino](http://bitalino.com/pyAPI/) - http://bitalino.com/pyAPI/
