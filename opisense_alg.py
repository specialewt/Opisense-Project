import numpy as np
import pandas as pd
import sys
import os

class OpisenseAlg:   
    def __init__(self)->None:
        # Temperature Weights
        self.tmpW = [5,0,45]
        # Breaths per Min Weights
        self.respW = [10,15,20,50,55,60]
        # Heart Rate Weights
        self.hrW = [0,5,15,45,50,55]
        # EDA Weights  
        self.edaW = [2,2]
        
    def __tmp_decision(self,t)->int:       
        if t<31:
            return self.tmpW[0]
        elif t>37:
            return self.tmpW[2]
        else:
            return self.tmpW[1]

    def __resp_decision(self,r)->int:
        if r<8:
            return self.respW[2]
        elif r<10:
            return self.respW[1]
        elif r<13:
            return self.respW[0]
        elif r<17:
            return 0
        elif r<20:
            return self.respW[3]
        elif r<26:
            return self.respW[4]
        else:
            return self.respW[5]
        
    def __hr_decision(self,h)->int:
        if h<51:
            return self.hrW[2]
        elif h<66:
            return self.hrW[1]
        elif h<81:
            return self.hrW[0]
        elif h<100:
            return self.hrW[3]
        elif h<121:
            return self.hrW[4]        
        elif h>120:
            return self.hrW[5]
        
    def __eda_decision(self,e)->int:
        if e<2:
            return self.edaW[0]
        elif e<20:
            return 0
        else:
            return self.edaW[1]

    def __weight_decision(self,w)->str:
        if w<25:
            return 'normal'
        elif w<30:
            return 'warning--use'
        elif w<43:
            return 'emergency--use'
        elif w<100:
            return 'normal'
        elif w<151:
            return 'warning--withdrawal'
        elif w<163:
            return 'emergency--withdrawal'
        else:
            return 'device error'
    
    def determine_state(self,x)->str:
        tmp = self.__tmp_decision(x[0])
        resp = self.__resp_decision(x[4])
        hr = self.__hr_decision(x[3])
        eda = self.__eda_decision(x[2])
        weight = tmp + resp + hr + eda
        state = self.__weight_decision(weight)
        return state
        
if __name__ == '__main__':
    test = OpisenseAlg()
