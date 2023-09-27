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
day_range = np.arange(213, 244, 1)
month = 'August'

# directory setting
parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing/'
station_list = os.listdir(parent_dir)
merged_stream = {} # THIS MERGE STREAM DID NOT REMOVE INSTRUMENT RESPONSE!!
# tidy up the data
for station in station_list:
    logging.info(f"Now we are in station:{station}")
    station_dir = os.path.join(parent_dir, station) # ./preprocessing/SM01
    current_stream = Stream() # initial the stream when changing the station

    for day in day_range:
        logging.info(f"Now we are in the {day} day of year")
        day_trans = format_number(day)
        day_file = f"EPZ.D.2023.{day_trans}"
        day_path = os.path.join(station_dir, 'EPZ.D', f'*{day_file}*') # ./preprocessing/SM01/EPZ.D/*EPZ.D.2023.001*
        sac_data = glob.glob(day_path)

        try:
            st = read(sac_data[0]) # whole day stream
            current_stream += st
            logging.info(f"the data of {day} day of year is merging, thank god")
        except Exception as e:
            # handle the exception and log it
            logging.error(f"Error processing thorugh the {day} day of year: {str(e)}")
    current_stream = current_stream.merge()
    logging.info(f"merging complete")
    '''
    adding the plotting block here to loop
    '''
    merged_stream[f"st_all_{station}"] = current_stream
    logging.info(f"the {station} stream is update in dictionary!")


from obspy.imaging.cm import pqlx
# we will acquire a dictionary contain the whole month stream for each station.
st_sm01 = merged_stream["st_all_SM01"]

paz = {'poles': [-1.978100e+01+2.020270e+01j, -1.978100e+01-2.020270e+01j],
            'zeros': [0j, 0j],
            'gain': 546976,
            'sensitivity': 546976.0}

ppsd = PPSD(st_sm01[0].stats, paz)
ppsd.add(st_sm01)
ppsd.plot(filename = 'psd.png', cmap=obspy.imaging.cm.pqlx, period_lim=(0.5,100), xaxis_frequency=True)
logging.info(f"we here!")
# %%
