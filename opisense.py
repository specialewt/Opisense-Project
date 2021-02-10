# Standard Library
import time
import sched
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


class Opisense:
    
1    def __init__(self):
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
        
        self._readSched = sched.scheduler(time.time, time.sleep)

    def find_devices(self):
        """Search for nearby BITalino devices and return the MAC address of those found."""
        localBITalinoMACs = [device[0] for device in bitalino.find() if 'BITalino' in device[1]]
        return localBITalinoMACs
    
    def __connect_bitalino(self):
        """Attempt to establish a connection w/ the BITalion hardware."""
        
        try:
            self._device = BITalino(macAddress = '98:D3:41:FD:4F:D9')
            #self._device = BITalino(macAddress=self._macAddress)
            return True
        except:
            print('Error in establishing device connection. Trying again.')
            return False
        
    
    def __start(self):
        """Start data collection by the device using the defined parameters."""
        self.device.start(
            SamplingRate = self._samplingRate,
            analogChannels = self._acqChannels
        )
    
    def __stop(self):
        """Stops data collection by the device."""
        self.device.stop()
    
    def record(self,duration):
        """Record device data for the provided duration (seconds)."""
        self.__stop()
        self.__start()
        self.__reset()
        
        # Enter the first read into the scheduler.
        self._readSched.enter(5,1,read_function,kwargs = {'duration':duration})
        # Run the scheduler.
        self._readSched.run()

    def __reset(self):
        """Initialize the instance variables for data recording."""
        self._readData = pd.DataFrame(columns = ['tpm','resp','pulse','eda'])
        self._recordingTime = 0
    
    def __read_data(self,duration):
        data = self._device.read(5000)[:,5:8]
        tempRec = pd.DataFrame(data,columns = ['tpm','resp','pulse','eda'])
        self._readData = self._readData.append(tempRec)
        # Determine if there is time remaing to record.
        if self._recordingTime<duration:
            # There is time remaing; continue to record.
            print('Reading data.')
            self._readSched.enter(5,1,read_function,kwargs = {'duration':duration})
            self._recordingTime += 5
        else:
            # There is no time remaing; stop recording and save the recorded data.
            print('Finished reading, saving date.')
            self._record.to_csv('OpisenseData_'+time.strftime("%d_%b_%Y_%H:%M:%S", time.gmtime())+'.csv')
