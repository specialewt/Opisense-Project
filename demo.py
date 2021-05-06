import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
# Custom Imports
from opisense import Opisense
from opisense_alg import OpisenseAlg
import data_analysis as da
import preprocessing as pp


def get_kenji_data()->pd.DataFrame:
    tempDB = da.load_make_database()
    print(tempDB.head())
    return tempDB[tempDB['subject']=='kenji']


def get_new_data()->pd.DataFrame:
    exOpi = Opisense()
    print(f'Nearby devices: {exOpi.find_devices()}')
    print(f'Beginning recording...\n')
    exOpi.start()
    newData = pd.DataFrame()
    i = 0 
    while i<10:
        newData = newData.append(exOpi.read_data())
        time.sleep(1)
        i += 1
    exOpi.stop()
    print(f'Ending recording...\n')
    newData.pop('time')
    make_time_plots(newData.to_numpy())
    return process_new_data(newData)

def process_new_data(newData:pd.DataFrame)->pd.DataFrame:
    #newData.pop('time')
    newData = pp.process_raw_data(newData.to_numpy())
    newData['subject'] = 'kenji'
    newData['state'] = 'rest'
    newData['alg_state'] = newData.apply(OpisenseAlg().determine_state,axis=1)
    return newData


def make_time_plots(newData:np.ndarray)->None:
    t = np.arange(0, len(newData))
    # TMP
    ax1 = plt.subplot(411)
    ax1.set_title('TMP')
    plt.plot(t, newData[:,0])
    plt.setp(ax1.get_xticklabels(), fontsize=6)
    
    # RESP
    ax2 = plt.subplot(412, sharex=ax1)    
    ax2.set_title('PZT')
    plt.plot(t, newData[:,1])
    # make these tick labels invisible
    plt.setp(ax2.get_xticklabels(), fontsize=6)
    
    # HR
    ax3 = plt.subplot(413, sharex=ax1)
    ax3.set_title('HR')
    plt.plot(t, newData[:,2])
    plt.setp(ax3.get_xticklabels(), fontsize=6)
    
    # EDA
    ax4 = plt.subplot(414, sharex=ax1)
    ax4.set_title('EDA')
    plt.plot(t, newData[:,3])
    plt.setp(ax4.get_xticklabels(), fontsize=6)
    
    plt.show()


if __name__ == '__main__':
    kenjiNew = get_new_data()
    #kenjiData = get_kenji_data()
    #print(kenjiData.head())
    #print(kenjiData.columns)
    #prepro,pipe = da.get_data_pipeline(kenjiData,dropLabels = False)
    #kenjiTrans = pd.DataFrame(prepro.fit_transform(kenjiData))
    #print(kenjiTrans.head())
    #da.alg_acc(kenjiData)
    make_time_plots(kenjiNew.drop(columns=['alg_state', 'subject', 'state'],axis=1).to_numpy())
    da.alg_acc(kenjiNew)    
    #kenjiData.hist()
    
    plt.show()
    #print(kenjiData.head())
