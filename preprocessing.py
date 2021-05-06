import pandas as pd
import numpy as np
import heartpy as hp
import sys
import os

#Opisense Alg
from opisense_alg import OpisenseAlg

def get_data_from_file(fileName:str):
    """Reads and strips the designated raw data file."""
    # Use only the middle 4:30 mins (trim the first 30s and stop @ 5 mins)
    print(f'Data loaded from:\n{fileName}')
    return np.loadtxt(fileName)[1000*30:1000*60*5,5:9]

def heart_rate_extraction(rawHR:np.ndarray)->float:
    """Calculates the heart rate for the given pulse data."""
    try:
        #print(np.mean(rawHR))
        filtHR = hp.filter_signal(rawHR,3,1000)
        filtHR = hp.enhance_peaks(filtHR)
        filtHR = hp.scale_data(filtHR,0,1)
        wd,m = hp.process(filtHR,1000)
        return int(m['bpm']),int(float(m['breathingrate'])*60)
    except:
        print(f'\nUnable to find HR; ({np.mean(rawHR)})')
        return 0.0,0.0
    
def windowed_reduction(rawData:np.ndarray)->pd.DataFrame:
    """Reduces the passed data."""
    winRawData = pd.DataFrame()
    # Reduce using 1s window.
    # Temp, PZT, and EDA use avg.
    #print(rawData[:,0])
    #print(np.mean(rawData[:,0]))
    winRawData['TMP'] = [np.mean(rawData[:,0])]
    winRawData['PZT'] = [np.mean(rawData[:,1])]
    winRawData['EDA'] = [np.mean(rawData[:,3])]
    #winRawData['HR'] = heart_rate_extraction(rawData[:,2])
    #print(winRawData.head())
    return winRawData

def NTCconv(x):
    """Temperature conversion."""
    ntc_v = x*3/2**10
    ntc_o = (10**4 * ntc_v)/(3-ntc_v)
    a0 = 1.12764514*10**-3
    a1 = 2.34282709*10**-4
    a2 = 8.77303013*10**-8
    tmp_k = (a0+a1*np.log(ntc_o)+a2*(np.log(ntc_o)**3))**-1
    tmp_c = tmp_k - 273.15
    return tmp_c
    
def process_raw_data(rawData:np.ndarray)->pd.DataFrame:
    """Processes the raw data using the appropriate functions."""
    processedData = pd.DataFrame()
    # Reduce data.
    lenRaw = len(rawData)
    x = 1000
    y = 10000
    while x<lenRaw:
        wrData = windowed_reduction(rawData[:x,:])
        hre = heart_rate_extraction(rawData[(y-10000):y,2])
        wrData['HR'] = hre[0]
        wrData['RESP'] = hre[1]
        processedData = processedData.append(wrData)
        print(f'\r [{x/lenRaw*100}%]', end='')
        sys.stdout.flush()
        x +=1000
        if (x%y==0): y += 10000
        if y > len(rawData): y = len(rawData)
        #break
    processedData.TMP = processedData.TMP.apply(NTCconv)
    processedData.PZT = processedData.PZT.apply(lambda x: ((x/(2**10 -1))-0.5)*100)
    processedData.EDA = processedData.EDA.apply(lambda x: ((3.3*x/(2**10))/0.132))
    #print(processedData.head())
    return processedData
        
def get_labels(fileName:str)->dict:
    """Extracts labels from filename."""
    print('\n')
    #print(fileName)
    tempLabels = fileName.split('_')
    #print(tempLabels)
    finalLabels = {'subject':tempLabels[0],'state':tempLabels[1].replace('.txt','')}
    #print(finalLabels)
    return finalLabels

def get_filenames(folderPath:str)->list:
    """Extracts filenames from target folder."""
    dirList = os.listdir(folderPath)
    fileList = []
    for fileName in dirList:
        if 'converted' in fileName:
            continue
        elif '.txt' in fileName:
            fileList.append(fileName)
    #print(fileList)
    return fileList

def make_processed_filename(fileName:str)->str:
    """Creates the processed filename from the original."""
    comps = fileName.split('.')
    proFN = comps[0]+'_processed.csv'
    #print(proFN)
    return proFN

def setup_processed_directory(rawDataPath)->None:
    """File management."""
    os.chdir(rawDataPath)
    os.makedirs("Processed Data", exist_ok = True)
    os.chdir(os.path.join(rawDataPath,"Processed Data"))

def preprocessing_main(rawDataPath:str)->None:
    fileNames = get_filenames(rawDataPath)
    setup_processed_directory(rawDataPath)
    for fileName in fileNames:
        # TODO process the data.
        rawData = get_data_from_file(os.path.join(rawDataPath,fileName))
        proData = process_raw_data(rawData)
        # Make processed filename.
        proFileName = make_processed_filename(fileName)
        # Add labels to the processed data.
        proData['alg_state'] = proData.apply(OpisenseAlg().determine_state,axis=1)
        labels = get_labels(fileName)
        proData['subject'] = labels['subject']
        proData['state'] = labels['state']
        # Save the processed data to file.
        proData.to_csv(proFileName)

if __name__ == '__main__':
    RAW_DATA_PATH = 'C:/Users/wtspe/Documents/OpenSignals (r)evolution/files/test_data'
    TEST_FILE_PATH = 'C:/Users/wtspe/OneDrive - Saint Louis University/Year 4/Semester VIII/Senior Project II/Opisense-Project/data/will_rest.txt'    
    preprocessing_main(RAW_DATA_PATH)
        
