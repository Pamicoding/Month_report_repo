# for transform the daily data into a monthly data by using merge() and save as a dictionary
# module
from obspy import read, Stream
import numpy as np
import os 
import glob
import logging
import pickle # for saving the dictionary
# def
# convert 1 to 001 for searching
def format_number(number):
    number_str = str(number) # Convert the number to a string
    num_digits = len(number_str) # Determine the number of digits in the original number
    num_zeros = 3 - num_digits # Calculate the number of leading zeros needed
    formatted_number = '0' * num_zeros + number_str # Add the leading zeros and return the formatted number as a string
    return formatted_number 

# Initialize the logging system
logging.basicConfig(filename='month_merge.log', level=logging.INFO, filemode='w')  # Create a log file

# variables
day_range = np.arange(244, 274, 1)
month = 'September'

# directory setting
output_dir = f'/raid1/SM_data/archive/2023/TW/{month}_merge'
os.makedirs(output_dir,exist_ok=True)
parent_dir = '/raid1/SM_data/archive/2023/TW/remove_resp/'
station_list = os.listdir(parent_dir)
merged_stream = {}

# tidy up the data
for station in station_list:
    logging.info(f"Now we are in station:{station}")
    station_dir = os.path.join(parent_dir, station) # ./remove_resp/SM01
    current_stream = Stream() # initial the stream when changing the station

    for day in day_range:
        logging.info(f"Now we are in the {day} day of year")
        day_trans = format_number(day)
        day_file = f"EPZ.D.2023.{day_trans}"
        day_path = os.path.join(station_dir, f'*{day_file}*') # ./remove_resp/SM01/*EPZ.D.2023.001*
        sac_data = glob.glob(day_path)

        try:
            st = read(sac_data[0]) # whole day stream
            #st_freq = st.filter("bandpass", freqmin=0.1, freqmax=10) # filter
            current_stream += st # adding it into a stream
            logging.info(f"the data of {day} day of year is merging, thank god")
        except Exception as e:
            # handle the exception and log it, we use it due to the data lack in our month
            logging.error(f"Error processing thorugh the {day} day of year: {str(e)}")
    current_stream = current_stream.merge(fill_value='interpolate') 
    logging.info(f"merging complete")
    merge_file = os.path.join(output_dir, station)
    #current_stream.write(merge_file, format='SAC') # We can't write the masked array
    #logging.info(f"the {station} merge data is now save in {output_dir}")
    merged_stream[f"st_all_{station}"] = current_stream
    logging.info(f"the {station} stream is update in dictionary!")


# save this merge_stream as dictionary
file_name = f"{month}_mergedata"
file_path = os.path.join('/home/patrick/Work/',file_name)
with open(file_path, 'wb') as file:
    pickle.dump(merged_stream, file)

logging.info('done, the merged_stream was saved')