#%%
import obspy
from obspy import read
import os
from obspy.io.sac import attach_paz
from obspy.signal.invsim import corn_freq_2_paz
from obspy.signal import PPSD
import glob
import logging

# intialize the logging file
logging.basicConfig(filename='preprocessing.log',level=logging.INFO, filemode='w')
# Define the parent directory containing subdirectories with seismic data.
parent_directory = '/raid1/SM_data/archive/2023/TW'
azi_path = '/raid1/SeiscomP/archive/2023/TW/SM39/'
output_parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing' # parent folder of output data
os.makedirs(output_parent_dir, exist_ok=True) # create
days = range(274, 305) # oct days of year

# List of subdirectories within the parent directory.
station_list = ['SM01','SM02', 'SM06', 'SM09', 'SM19', 'SM37', 'SM39', 'SM40']
azi_list = os.listdir(azi_path)
# Loop through each subdirectory.

for station in station_list:
    # Define the full path to the current subdirectory.
    station_path = os.path.join(parent_directory, station) # ./TW/SM02
    # Create a corresponding parent subdirectory in the output parent directory with the naming pattern.
    output_station_path = os.path.join(output_parent_dir, station) # ./preprocessing/SM02
    os.makedirs(output_station_path, exist_ok=True)
    logging.info(f"we are now in {station}")

    for azi in azi_list: 
        try:
            logging.info(f"in the {azi}")
            # define the full path to current sub_subdirectory.
            sub_subdirectory_path = os.path.join(station_path, azi) # ./TW/SM02/EPZ.D

            # creating the corresponding output directory
            output_directory = os.path.join(output_station_path, azi) # ./preprocessing/SM02/EPZ.D
            os.makedirs(output_directory, exist_ok=True)
        except Exception as e:
            logging.info(f"{azi} not found in {station}")
        for day in days:
            try:
                data_file = glob.glob(os.path.join(sub_subdirectory_path, f'*{day}*'))

                logging.info(f"on the day of year:{day}")
                # Read the seismic data file into a Stream object.
                st = read(data_file[0])
                st_copy = st.copy() # adding a copy to avoid covering the data

                # Merge traces within the Stream if there are more than one trace.
                if len(st_copy) > 1:
                    st_copy = st_copy.merge(fill_value='interpolate')

                # Preprocess the Stream.
                st_copy.detrend('demean')
                st_copy.detrend('linear')
                #st_copy.taper(type='hann', max_percentage=0.05)
                logging.info(f"{os.path.basename(data_file[0])} detrend are done")
                # Define the output file path and save the preprocessed Stream.
                output_file = os.path.join(output_directory, os.path.basename(data_file[0]))
                logging.info(f"{os.path.basename(data_file[0])} is writing...")
                st_copy.write(output_file, format='SAC')
            except Exception as e:
                logging.info(f"{e} on {day} in {station}_{azi}")


logging.info("Preprocessing and saving completed for all directories.")
# %%
