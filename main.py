<<<<<<< HEAD
from opisense import Opisense
import asyncio
import os
import time
import pandas as pd
import numpy as np
import opisense

async def get_heart_rate(rawData:pd.Series)->pd.Series:
    # Extracting HR from pulse data. 
    #scaled_pulse = hp.preprocessing.scale_data(rawData[:,2])
    #scaled_pulse = hp.preprocessing.interpolate_clipping(scaled_pulse,1000)
    #filtered_pulse = hp.filter_signal(scaled_pulse, cutoff=5, sample_rate=1000.0, order=3)
    #enhanced_pulse = hp.enhance_peaks(filtered_pulse)
    #wd,m = hp.process(enhanced_pulse,1000)
    pass


async def process_data_main(rawData: pd.DataFrame)->pd.DataFrame:
    df = pd.DataFrame()
    rule = '1S'
    f = rawData.time.floor(rule)
    def NTCconv(x):
        ntc_v = x*3/2**10
        ntc_o = (10**4 * ntc_v)/(3-ntc_v)
        a0 = 1.12764514*10**-3
        a1 = 2.34282709*10**-4
        a2 = 8.77303013*10**-8
        
        tmp_k = (a0+a1*np.log(ntc_o)+a2*(np.log(ntc_o)**3))**-1
        tmp_c = tmp_k - 273.15
        
        return tmp_c
    
    # TODO need to extract respiration rate from PZT.
    df['channel_1_TMP_C'] = rawData.channel_1_raw.mean()
    df['channel_1_TMP_C'] = rawData.channel_1_TMP_C.apply(NTCconv)
    #df['channel_1_TMP_F'] = rawData.channel_1_TMP_C.apply(lambda x: 1.8*x + 32)
    df['channel_2_PZT'] = rawData.channel_2_raw.mean()
    df['channel_2_PZT'] = rawData.channel_2_PZT.apply(lambda x: ((x/(2**10 -1))-0.5)*100)
    # EDA is measured in micro siemens
    df['channel_4_EDA'] = rawData.channel_4_raw.mean()
    df['channel_4_EDA'] = rawData.channel_4_EDA.apply(lambda x: ((3.3*x/(2**10))/0.132))
    # TODO Heart Rate Stuff
    df['channel_3_HeartRate'] = 75
    return df


async def produce_data(device: Opisense, q: asyncio.Queue, endTime: int=time.time()+120):
    while time.time()<endTime:
        await asyncio.sleep(5)
        data = device.read_data()
        await q.put(data)
        print(f'Data added to the queue @ {time.time()}.')

async def consume_data(q: asyncio.Queue):
    sessionName = f'session_end{int(time.time())}.csv'
    while True:
        data = await q.get()
        q.task_done()
    finally:
        pass
        #TODO process data, save to file, send to page
        print(f'Session Complete: {int(time.time())}') 
    
async def main(device: Opisense)->None:
    myQueue = asyncio.Queue()
    # Make producer and consumers.
    producer = asyncio.create_task(produce_data(device,myQueue))
    consumer = asyncio.create_task(consume_data(myQueue))
    await asyncio.gather(producer)
    await myQueue.join()
    consumer.cancel()


if __name__ == '__main__':
    exOpi = Opisense()
    exOpi.start()
    asyncio.run(main(exOpi))
    exOpi.stop()
=======
from opisense import Opisense
import asyncio
import os
import time
import pandas as pd
import numpy as np
import opisense

async def get_heart_rate(rawData:pd.Series)->pd.Series:
    # Extracting HR from pulse data. 
    #scaled_pulse = hp.preprocessing.scale_data(rawData[:,2])
    #scaled_pulse = hp.preprocessing.interpolate_clipping(scaled_pulse,1000)
    #filtered_pulse = hp.filter_signal(scaled_pulse, cutoff=5, sample_rate=1000.0, order=3)
    #enhanced_pulse = hp.enhance_peaks(filtered_pulse)
    #wd,m = hp.process(enhanced_pulse,1000)
    pass


async def process_data_main(rawData: pd.DataFrame)->pd.DataFrame:
    df = pd.DataFrame()
    rule = '1S'
    f = rawData.time.floor(rule)
    def NTCconv(x):
        ntc_v = x*3/2**10
        ntc_o = (10**4 * ntc_v)/(3-ntc_v)
        a0 = 1.12764514*10**-3
        a1 = 2.34282709*10**-4
        a2 = 8.77303013*10**-8
        
        tmp_k = (a0+a1*np.log(ntc_o)+a2*(np.log(ntc_o)**3))**-1
        tmp_c = tmp_k - 273.15
        
        return tmp_c
    
    # TODO need to extract respiration rate from PZT.
    df['channel_1_TMP_C'] = rawData.channel_1_raw.mean()
    df['channel_1_TMP_C'] = rawData.channel_1_TMP_C.apply(NTCconv)
    #df['channel_1_TMP_F'] = rawData.channel_1_TMP_C.apply(lambda x: 1.8*x + 32)
    df['channel_2_PZT'] = rawData.channel_2_raw.mean()
    df['channel_2_PZT'] = rawData.channel_2_PZT.apply(lambda x: ((x/(2**10 -1))-0.5)*100)
    # EDA is measured in micro siemens
    df['channel_4_EDA'] = rawData.channel_4_raw.mean()
    df['channel_4_EDA'] = rawData.channel_4_EDA.apply(lambda x: ((3.3*x/(2**10))/0.132))
    # TODO Heart Rate Stuff
    df['channel_3_HeartRate'] = 75
    return df


async def produce_data(device: Opisense, q: asyncio.Queue, endTime: int=time.time()+120):
    while time.time()<endTime:
        await asyncio.sleep(5)
        data = device.read_data()
        await q.put(data)
        print(f'Data added to the queue @ {time.time()}.')

async def consume_data(q: asyncio.Queue):
    sessionName = f'session_end{int(time.time())}.csv'
    while True:
        data = await q.get()
        q.task_done()
    finally:
        pass
        #TODO process data, save to file, send to page
        print(f'Session Complete: {int(time.time())}') 
    
async def main(device: Opisense)->None:
    myQueue = asyncio.Queue()
    # Make producer and consumers.
    producer = asyncio.create_task(produce_data(device,myQueue))
    consumer = asyncio.create_task(consume_data(myQueue))
    await asyncio.gather(producer)
    await myQueue.join()
    consumer.cancel()


if __name__ == '__main__':
    exOpi = Opisense()
    exOpi.start()
    asyncio.run(main(exOpi))
    exOpi.stop()
>>>>>>> d5b426a1f5adc4c1d725809bcb098e80bb330a64
