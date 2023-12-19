#%%
# !!! we need to transfer the HLZ acceleration into velocity !!!
# Module
import obspy
from obspy import read, Stream
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx
import logging
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
# Logging system
logging.basicConfig(filename='psd.log', level=logging.INFO, filemode='w')  # Create a log file

# def
# convert 1 to 001 for searching
def format_number(number):
    number_str = str(number) # Convert the number to a string
    num_digits = len(number_str) # Determine the number of digits in the original number
    num_zeros = 3 - num_digits # Calculate the number of leading zeros needed
    formatted_number = '0' * num_zeros + number_str # Add the leading zeros and return the formatted number as a string
    return formatted_number 

# variables
day_range = range(274,305)
month = 'October'
year = 2023
# directory setting
merged_stream = {} # THIS MERGE STREAM DID NOT REMOVE INSTRUMENT RESPONSE!!

# Define the parent directory containing subdirectories with seismic data.
parent_directory = '/raid1/SM_data/archive/2023/TW'
output = '/home/patrick/Work/Month_report_repo/output/2023_oct/'

# List of subdirectories within the parent directory.
station_list = ['SM01','SM02', 'SM06', 'SM09', 'SM19', 'SM37', 'SM39', 'SM40']
azi_list =['EPZ.D', 'HLZ.D']
# Loop through each subdirectory.
for station in station_list:
    logging.info(f"Now we are in station:{station}")
    subdirectory_path = os.path.join(parent_directory, station) # ./TW/SM01/
    for azi in azi_list:
        logging.info(f"in the {azi}")
        current_stream = Stream() # initial the stream when changing the station
        try:
            sub_subdirectory_path = os.path.join(subdirectory_path, azi) # ./TW/SM01/EPZ.D
        except Exception as e:
            logging.info(f"{e} existed in {azi}")
        for day in day_range:
            logging.info(f"Now we are in the {day} day of year")
            day_trans = format_number(day)
            day_file = f"{azi}.{year}.{day_trans}"
            day_path = os.path.join(sub_subdirectory_path, f'*{day_file}*') # ./TW/SM01/EPZ.D/*EPZ.D.2023.001*
            sac_data = glob.glob(day_path)
            try:
                # Read the seismic data file into a Stream object.
                st_1 = read(sac_data[0])
                st_copy = st_1.copy() # adding a copy to avoid covering the data
                # Merge traces within the Stream if there is more than one trace.
                if len(st_copy) > 1:
                    st_copy = st_copy.merge(method=1, fill_value='interpolate')

                current_stream += st_copy
                logging.info(f"the data of {day} day of year is merging, thank god")

            except Exception as e:
                # handle the exception and log it
                logging.error(f"Error processing thorugh the {day} day of year: {str(e)}")
        current_stream = current_stream.merge(fill_value='interpolate')
        logging.info(f"merging complete")
        if azi[:2] == 'EP':
            # EP
            paz_sts2 = {'poles': [-1.978100e+01+2.020270e+01j, -1.978100e+01-2.020270e+01j],
                    'zeros': [0j, 0j, 0j],
                    'gain': 27.7,
                    'sensitivity': 546976.0}
        else:
            # HL
            paz_sts2 = {'poles':[-9.770000e+02+3.280000e+02j, -9.770000e+02-3.280000e+02j,
                                -1.486000e+03+2.512000e+03j, -1.486000e+03-2.512000e+03j,
                                -5.736000e+03+4.946000e+03j, -5.736000e+03-4.946000e+03j],
                        'zeros':[0j, 0j, -515+0j],
                        'gain': 1.02,
                        'sensitivity': 408000.0}
        try:
            fig, ax = plt.subplots(figsize=(8,6))
            ppsd = PPSD(current_stream[0].stats, paz_sts2)
            ppsd.add(current_stream)
            ppsd.plot(filename=f"{output}{station}_{azi[:2]}_psd.png",cmap=obspy.imaging.cm.pqlx, period_lim=(0.5,100), xaxis_frequency=True)
            logging.info(f"ppsd finish!")
        except Exception as e:
            logging.info(f"{e} existed in {station}_{azi}")
    logging.info(f'{station} over')
logging.info('we did it!')
#%%