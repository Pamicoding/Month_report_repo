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
output_parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing' # parent folder of output data
os.makedirs(output_parent_dir, exist_ok=True) # create

# List of subdirectories within the parent directory.
station_list = ['SM01','SM02', 'SM06', 'SM09', 'SM19', 'SM37', 'SM39', 'SM40']
azi_list = ['EPZ.D','EPN.D', 'EPE.D']
# Loop through each subdirectory.
for station in station_list:
    # Define the full path to the current subdirectory.
    station_path = os.path.join(parent_directory, station) # ./TW/SM02
    # I finally understand it. For example, parent_directory='/path/qoo', and subdirectory is 'juice'
    # when we use os.path.join, it will be like /path/qoo/juice, fucking cool.
    
    # Create a corresponding parent subdirectory in the output parent directory with the naming pattern.
    output_station_path = os.path.join(output_parent_dir, station) # ./preprocessing/SM02
    os.makedirs(output_station_path, exist_ok=True)
    logging.info(f"we are now in {station}")
    for azi in azi_list: 
        # define the full path to current sub_subdirectory.
        sub_subdirectory_path = os.path.join(station_path, azi) # ./TW/SM02/EPZ.D

        # creating the corresponding output directory
        output_directory = os.path.join(output_station_path, azi) # ./preprocessing/SM02/EPZ.D
        os.makedirs(output_directory, exist_ok=True)

    # Use glob to find all files with a specific extension (e.g., .mseed) in the subdirectory.
    # data_files = glob.glob(sub_subdirectory_path) # no need to use glob
        data_files = glob.glob(os.path.join(sub_subdirectory_path, '*EP*'))
        logging.info(f"and in the {azi}")
    # Loop through each data file in the subdirectory and process them.
        for data_file in data_files:
            # Read the seismic data file into a Stream object.
            st = read(data_file)
            st_copy = st.copy() # adding a copy to avoid covering the data

            # Merge traces within the Stream if there is more than one trace.
            if len(st_copy) > 1:
                st_copy = st_copy.merge(fill_value='interpolate')

            # Preprocess the Stream.
            st_copy.detrend('demean')
            st_copy.detrend('linear')
            #st_copy.taper(type='hann', max_percentage=0.05)
            logging.info(f"{data_file} detrend are done")
            # Define the output file path and save the preprocessed Stream.
            output_file = os.path.join(output_directory, os.path.basename(data_file))
            st_copy.write(output_file, format='SAC')
            logging.info(f"{data_file} writing...")

logging.info("Preprocessing and saving completed for all directories.")
# %%
