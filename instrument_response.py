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
logging.basicConfig(filename='response.log', level=logging.INFO, filemode='w')  # Create a log file
# filemode='w' is to write the logging
# variable
station_name = os.listdir(parent_dir)
azimuth_dir = ['EPZ.D','HLZ.D']
day_range = range(274, 305) # oct days of year
year = 2023
# Create an output directory for processed data
os.makedirs(output_dir, exist_ok=True)

# instrument response settings
corner_freq = 5
pre_filt = (0.05, 0.1, 50, 60)
damping = 0.7
paz_1hz = corn_freq_2_paz(corner_freq, damp=damping)
# loop for iterate data and create the process folder after removing instrument response
for name in station_name:
   logging.info(f"Processing station: {name}")  # Log station processing
   layer_1 = os.path.join(output_dir, name)
   os.makedirs(layer_1, exist_ok=True) # create ./remove_resp/SM01
   for azi in azimuth_dir:
      logging.info(f"Processing azimuth: {azi}")  # Log azimuth processing        
      sac_data_dir = os.path.join(parent_dir, name, azi) # ./preprocessing/SM01/EPZ.D
      # different pzs file to remove the instrument response
      if azi[:2] == 'EP':
         # EP
         paz_sts2 = {'poles': [-1.978100e+01+2.020270e+01j, -1.978100e+01-2.020270e+01j],
                     'zeros': [0j, 0j, 0j],
                     'gain': 27.7,
                     'sensitivity': 546976.0}
      else:
         # HL
         paz_sts2 = {'poles': [-9.770000e+02+3.280000e+02j, -9.770000e+02-3.280000e+02j,
                               -1.486000e+03+2.512000e+03j, -1.486000e+03-2.512000e+03j,
                               -5.736000e+03+4.946000e+03j, -5.736000e+03-4.946000e+03j],
                     'zeros': [0j, 0j, -515+0j],
                     'gain': 1.02,
                     'sensitivity': 408000.0}
      for day in day_range:
         day_f = format_number(day)
         day_path = f"{year}.{day_f}"
         search_pattern = os.path.join(sac_data_dir, f'*{day_path}*')
         try: 
            sac_data = glob.glob(search_pattern) 
         except Exception as e:
            logging.error(f"Error while searching for files in station {name}, azimuth {azi}: {str(e)}")
            continue  # Continue with the next azimuth
         for data in sac_data:
            try:
               st = read(data) # copy() is no need to use here due to the file is already copy in last step.
               st.simulate(paz_remove=paz_sts2, paz_simulate=paz_1hz, pre_filt=pre_filt) # we add the pre_filt to apply a bandpass
               # Save the preprocessed data in the output directory
               processed_file = os.path.join(layer_1, os.path.basename(data).replace('.sac', '_processed.sac'))
               # replace is a good way to do, but in this case our file did not end with .sac, so it will be ignored.
               st.write(processed_file, format='SAC')
               logging.info(f"Processed {data} and saved as {processed_file}")
            except Exception as e:
               # handle the exception and log it
               logging.error(f"Error processing {data}: {str(e)}")

logging.info('done')

