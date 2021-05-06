# Standard Library
import time
import json
import bluetooth
import socket
import sys
#import sudo

# 3rd Party General
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd

from bitalino import BITalino
from bitalino import find

class Opisense:
    def __init__(self):
        #TODO Implement a failure to connect condition.
        
        #sudo hciconfig hci0 reset
        failCounter = 0
        print(time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        
        """MAC Address for test device."""
        self._macAddress = '98:D3:41:FD:4F:D9'
        
        while not(self.__connect_bitalino()):
            failCounter += 1
            if failCounter>5:
                sys.exit('Unable to connect: Exiting.')
                break
            pass
        
        """Sampling rate of the device in Hz (samples per second)."""
        self._sampleRate = 1000
    
        """Channels to acquire data from."""
        self._acqChannels = [0,1,2,3]
        
        """Initialize read status."""
        self._canRead = False

    def find_devices(self)->list:
        """Search for nearby BITalino devices and return the MAC address of those found."""
        localBITalinoMACs = [device[0] for device in find() if 'BITalino' in device[1]]
        return localBITalinoMACs
    
    def __connect_bitalino(self)->bool:
        """Attempt to establish a connection w/ the BITalion hardware."""
        try:
            self._device = BITalino(macAddress = '98:D3:41:FD:4F:D9')
            #self._device = BITalino(macAddress=self._macAddress)
            return True
        except:
            print('Error in establishing device connection. Trying again.')
            return False
        
    def start(self)->None:
        """Start data collection by the device using the defined parameters."""
        self._canRead = True
        self._device.start(
            SamplingRate = self._sampleRate,
            analogChannels = self._acqChannels
        )
    
    def stop(self)->None:
        """Stops data collection by the device."""
        self._canRead = False
        self._device.stop()

    def __reset(self):
        """Initialize the instance variables for data recording."""
        pass
    
    def read_data(self)->pd.DataFrame:
        """Reads data off of the device in 5.0s windows and casts it as a dataframe."""
        if self._canRead:
            rawData = self._device.read(5000)
            rawCol = ['channel_1_raw','channel_2_raw','channel_3_raw','channel_4_raw']
            df= pd.DataFrame(columns = rawCol)
            df.channel_1_raw = rawData[:,5]
            df.channel_2_raw = rawData[:,6]
            df.channel_3_raw = rawData[:,7]
            df.channel_4_raw = rawData[:,8]
            #print(time.strftime("%H:%M:%S", time.localtime()))
            df['time'] = time.strftime("%H:%M:%S", time.localtime())
            #df.set_index('time',inplace=True)
            #print(df.head())
            return df
        else:
            print(f'Device must be started.')
            
if __name__ == '__main__':
    exOpi = Opisense()
    print(f'Nearby devices: {exOpi.find_devices()}')
    print(f'Beginning recording...\n')
    exOpi.start()
    time.sleep(5)
    exOpi.read_data()
    time.sleep(10)
    exOpi.read_data()
    print(f'Ending recording...\n')
    exOpi.stop()
