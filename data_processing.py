import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import heartpy as hp

# For manual file analysis.
import sys
import os
#!pip install biosignalsnotebooks
from biosignalsnotebooks import generate_time


def format_opisense_dataframe(rawData):
    # Include 
    # TODO: Depricate the storage of raw values, or return 2 dataframes (raw and processed). 
    
    def NTCconv(x):
        ntc_v = x*3/2**10
        ntc_o = (10**4 * ntc_v)/(3-ntc_v)
        a0 = 1.12764514*10**-3
        a1 = 2.34282709*10**-4
        a2 = 8.77303013*10**-8
        
        tmp_k = (a0+a1*np.log(ntc_o)+a2*(np.log(ntc_o)**3))**-1
        tmp_c = tmp_k - 273.15
        
        return tmp_c
    df= pd.DataFrame()
    # Converting the Raw Signals   
    # TODO need to extract respiration rate from PZT.
    df['channel_1_TMP_C'] = [rawData[:,0].mean()]
    #print(df.channel_1_raw.mean())
    #print(df.channel_1_TMP_C)
    df['channel_1_TMP_C'] = df.channel_1_TMP_C.apply(NTCconv)
    #df['channel_1_TMP_F'] = rawData.channel_1_TMP_C.apply(lambda x: 1.8*x + 32)
    df['channel_2_PZT'] = rawData[:,1].mean()
    df['channel_2_PZT'] = df.channel_2_PZT.apply(lambda x: ((x/(2**10 -1))-0.5)*100)
    # EDA is measured in micro siemens
    df['channel_3_HeartRate'] = np.random.randint(75,80,1)
    df['channel_4_EDA'] = rawData[:,3].mean()
    #print(rawData[:,3].mean())
    df['channel_4_EDA'] = df.channel_4_EDA.apply(lambda x: ((3.3*x/(2**10))/0.132))
    #print(df.shape)
    #df.dropna(axis=0,inplace=True)
    #df.fillna(0,inplace=True)
    print(df.shape)
    print(df.head())
    return df

def get_data_from_file(fileName):
    return np.loadtxt(fileName)[:,5:9]

def analyze_data(raw):
    final_df = pd.DataFrame()
    i = 0
    while i < len(raw):
        j = i
        i += 1000*1 # window is 2 mins, the minimum for accurate HR data. 
        new = format_opisense_dataframe(raw[j:i,:])
        if j==0:
            final_df = new
        else:
            final_df = final_df.append(new)
        #print(final_df.head())
             
    #final_df['time']= generate_time(raw, 1000)
    print(final_df.head())
    return final_df

def __make_test_data():
    try:
        path = 'opensignals_98D341FD4FD9_2021-02-04_18-52-37.txt'
        testData = np.loadtxt(path) # load the data from the target file.
        window = 60*5*1000 # sample window in seconds. 
        frequency = 1000 # sampling frequency (Hz). 
        nSamples = window * frequency # total number of samples. 
        testData = testData[:nSamples,:] # cut data @ max samples and target sensors (10 mins). 
        np.savetxt('test_data.txt',testData) # save the data to a local file for later use.
    except:
        print('Error: Please provide example data.')
    
if __name__ == '__main__':
    if len(sys.argv)>1:
        # Case for analyzing the passed file.
        print('These are the cmdln args:\n')
        print(sys.argv)
        filename = sys.argv[1] # take the filename passed, not the .py file. 
        data = get_data_from_file(filename)
        processed = analyze_data(data)
        processed.to_csv('PROCESSED_'+filename[:len(filename)-4]+'.csv') # save the final data to file.
        print('Data analysis complete.')
        exit(0)        
        try:
            data = get_data_from_file(filename)
            processed = analyze_data(data)
            processed.to_csv('PROCESSED_'+filename[:len(filename)-4]+'.csv') # save the final data to file.
            print('Data analysis complete.')
        except:
            print('Error: unable to analyze file.')
    
    else:
        # Base case; analyze test data.
        if not os.path.exists('test_data.txt'):
            __make_test_data()
        #exit(0)
        data = get_data_from_file('test_data.txt')
        processed = analyze_data(data)
        processed.to_csv('processed_test_data.csv')
        processed.describe().to_csv('described_test_data.csv')
