import obspy
import numpy as np
from obspy import read, UTCDateTime
import os
from obspy.io.sac import attach_paz
from obspy.signal.invsim import corn_freq_2_paz
import glob 
import logging
# the file path
parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing'  
pzs_parent_dir = '/raid1/SM_data/TWSM2'
output_dir = '/raid1/SM_data/archive/2023/TW/remove_resp'
pzs_path = '/raid1/SM_data/TWSM2/SM01/SAC_PZs_TW_SM01_EPZ__2021.001.00.00.00.0000_2599.365.23.59.59.99999'
#pzs_data = glob.glob(pzs_path) # just denote one of the file ./raid1/SM_data/TWSM2/SM01/...EPZ

# def
def format_number(number):
    # Convert the number to a string
    number_str = str(number)
    
    # Determine the number of digits in the original number
    num_digits = len(number_str)
    
    # Calculate the number of leading zeros needed
    num_zeros = 3 - num_digits
    
    # Add the leading zeros and return the formatted number as a string
    formatted_number = '0' * num_zeros + number_str
    
    return formatted_number # we will transfer the 1 to 001

# Initialize the logging system
logging.basicConfig(filename='processing.log', level=logging.INFO, filemode='w')  # Create a log file
# filemode='w' is to write the logging
# variable
station_name = os.listdir(parent_dir)
azimuth_dir = os.listdir(os.path.join(parent_dir, 'SM01'))
day_range = np.arange(213, 244, 1)

# Create an output directory for processed data
os.makedirs(output_dir, exist_ok=True)

# trim settings
#trim_starttime = UTCDateTime("2023-07-09T22:06:33")
#trim_endtime = UTCDateTime("2023-07-09T22:16:33")

# instrument response settings
corner_freq = 5
pre_filt = (0.05, 0.1, 30, 40)
damping = 0.7

# loop for iterate data and create the process folder after removing instrument response
for name in station_name:
    logging.info(f"Processing station: {name}")  # Log station processing
    layer_1 = os.path.join(output_dir, name)
    os.makedirs(layer_1, exist_ok=True) # create ./remove_resp/SM01
    for azi in azimuth_dir:
        logging.info(f"Processing azimuth: {azi}")  # Log azimuth processing        
        sac_data_dir = os.path.join(parent_dir, name, azi) # ./preprocessing/SM01/EPZ.D
        # we want to remove it monthly, so we need to focus on specific number.
        for day in day_range:
            day_f = format_number(day)
            day_path = f"2023.{day_f}"
            search_pattern = os.path.join(sac_data_dir, f'*{day_path}*')
            try: 
               sac_data = glob.glob(search_pattern) 
            except Exception as e:
                logging.error(f"Error while searching for files in station {name}, azimuth {azi}: {str(e)}")
                continue  # Continue with the next azimuth
            for data in sac_data:
               try:
                  st = read(data) # copy() is no need to use here due to the file is already copy in last step.
                  #st.trim(starttime = trim_starttime, endtime = trim_endtime)
                  paz_1hz = corn_freq_2_paz(corner_freq, damp=damping)
                  paz_sts2 = {'poles': [-1.978100e+01+2.020270e+01j, -1.978100e+01-2.020270e+01j],
                  'zeros': [0j, 0j],
                  'gain': 546976,
                  'sensitivity': 546976.0}
                  st.simulate(paz_remove=paz_sts2, paz_simulate=paz_1hz)
                  #st.simulate(paz_remove=paz_1hz, pre_filt=pre_filt) # old one
                  # Save the preprocessed data in the output directory
                  processed_file = os.path.join(layer_1, os.path.basename(data).replace('.sac', '_processed.sac'))
                  # replace is a good way to do, but in this case our file did not end with .sac, so it will be ignored.
                  st.write(processed_file, format='SAC')
                  logging.info(f"Processed {data} and saved as {processed_file}")
               except Exception as e:
                   # handle the exception and log it
                   logging.error(f"Error processing {data}: {str(e)}")



# Check the file
#check_st = read('/raid1/SM_data/archive/2023/TW/remove_resp/SM01/TW.SM01.00.EPZ.D.2023.190')
#check_st.plot()

'''
----Memo----
1. maybe we don't need that much directory(for N, E, and Z), comparing to ILAN2022 to see if it's reasonable 
   --> reasonable! we can use glob.glob to find '*EPE*' for example.
2. instrument response same
   --> so we do not need to iterate the pzs file
3. some info for removing instrument response (see quicknote)
'''


