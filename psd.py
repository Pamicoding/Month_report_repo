#%%
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
day_range = np.arange(244, 274, 1)
month = 'September'

# directory setting
merged_stream = {} # THIS MERGE STREAM DID NOT REMOVE INSTRUMENT RESPONSE!!

# Define the parent directory containing subdirectories with seismic data.
parent_directory = '/raid1/SM_data/archive/2023/TW'


# List of subdirectories within the parent directory.
station_list = ['SM01','SM02', 'SM06', 'SM09', 'SM19', 'SM37', 'SM39', 'SM40']
# Loop through each subdirectory.
for station in station_list:
    logging.info(f"Now we are in station:{station}")
    subdirectory_path = os.path.join(parent_directory, station, 'EPZ.D') # ./TW/SM01/EPZ.D
    current_stream = Stream() # initial the stream when changing the station
    for day in day_range:
        logging.info(f"Now we are in the {day} day of year")
        day_trans = format_number(day)
        day_file = f"EPZ.D.2023.{day_trans}"
        day_path = os.path.join(subdirectory_path, f'*{day_file}*') # ./TW/SM01/EPZ.D/*EPZ.D.2023.001*
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
    merged_stream[f"st_all_{station}"] = current_stream
    logging.info(f"the {station} stream is update in dictionary!")
#%%
# we will acquire a dictionary contain the whole month stream for each station.
st_sm01 = merged_stream["st_all_SM40"]

paz = {  'poles': [-1.978100e+01+2.020270e+01j, -1.978100e+01-2.020270e+01j],
            'zeros': [0j, 0j, 0j],
            'sensitivity': 546976,
            'gain': 27.7}

ppsd = PPSD(st_sm01[0].stats, paz)
ppsd.add(st_sm01)
ppsd.plot( cmap=obspy.imaging.cm.pqlx, period_lim=(0.5,100), xaxis_frequency=True)
logging.info(f"we here!")
# %%
# loop version (haven't attest)
for station in station_list:
    st_plot = merged_stream[f"st_all_{station}"]
    paz = {  'poles': [-1.978100e+01+2.020270e+01j, -1.978100e+01-2.020270e+01j],
            'zeros': [0j, 0j, 0j],
            'sensitivity': 546976,
            'gain': 27.7}
    try:
        ppsd = PPSD(st_plot[0].stats, paz)
        ppsd.add(st_plot)
        ppsd.plot(filename= f"{station}_psd.png", cmap=obspy.imaging.cm.pqlx, period_lim=(0.5,100), xaxis_frequency=True)
        logging.info(f"the psd of {station} done")
    except IndexError as e: # to exclude the condition that the station did not acquire the data.
        logging.error(f"The error from {station}:{e}")

logging.info('done')
