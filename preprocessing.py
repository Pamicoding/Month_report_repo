# %%
import obspy
from obspy import read
import os
from obspy.io.sac import attach_paz
from obspy.signal.invsim import corn_freq_2_paz
from obspy.signal import PPSD
import glob
# follow the filename: 3039.FM.00.DPE.2023.002.20230102.SAC
#%%
# merge->demean->detrend->taper

# Define the directory containing your seismic data files (EPZ).
data_directory = '/raid1/SM_data/archive/2023/TW/SM01/EPZ.D/'
output_dir = '/raid1/SM_data/archive/2023/TW/SM01_ppreprocessing'
os.makedirs(output_dir, exist_ok=True)
# exist_ok, when dir is exist that won't exist error.

# Use glob to find all files with a specific extension (e.g., .mseed) in the directory.
data_files = glob.glob(os.path.join(data_directory, '*EPZ*'))

# Loop through each data file and process them.
for data_file in data_files:
    # Read the seismic data file into a Stream object.
    st = read(data_file)

    # Merge traces within the Stream if there is more than one trace.
    if len(st) > 1:
        st = st.merge(method=1, fill_value=0)
        # method 1: more flexible, but for our purpose there's no difference between using method 0 or 1.
        # filled = 0, that's a default, we don't want to interpolate the value.
    # Preprocess the Stream.
    st.detrend('demean')
    st.detrend('linear')
    st.taper(type='hann', max_percentage=0.05)

    # Define the output file path and save the preprocessed Stream.
    output_file = os.path.join(output_dir, os.path.basename(data_file))
    st.write(output_file, format='SAC')

print("Preprocessing and saving completed.")
#%%
# Remove Instrument response
corner_freq = 5
pre_filt = (0.05, 0.1, 30, 40)
damping = 0.7
Pzs_path = '/raid1/SM_data/TWSM2/SM01/SAC_PZs_TW_SM01_EPZ__2021.001.00.00.00.0000_2599.365.23.59.59.99999'
attach_paz(st[0], Pzs_path)
paz_1hz = corn_freq_2_paz(corner_freq, damp=damping)
st.simulate(paz_remove=paz_1hz, pre_filt=pre_filt)

#%%

# Define the parent directory containing subdirectories with seismic data.
parent_directory = '/raid1/SM_data/archive/2023/TW'
output_parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing' # parent folder of output data
os.makedirs(output_parent_dir, exist_ok=True) # create la

# List of subdirectories within the parent directory.
subdirectories = ['SM01','SM02', 'SM06', 'SM09', 'SM19', 'SM37', 'SM39', 'SM40']
sub_subdirectories = ['EPZ.D','EPN.D', 'EPE.D']
# Loop through each subdirectory.
for subdirectory in subdirectories:
    # Define the full path to the current subdirectory.
    subdirectory_path = os.path.join(parent_directory, subdirectory) # ./TW/SM02
    # I finally understand it. For example, parent_directory='/path/qoo', and subdirectory is 'juice'
    # when we use os.path.join, it will be like /path/qoo/juice, fucking cool.
    
    # Create a corresponding parent subdirectory in the output parent directory with the naming pattern.
    parent_subdirectory = os.path.join(output_parent_dir, subdirectory) # ./preprocessing/SM02
    os.makedirs(parent_subdirectory, exist_ok=True)

    for sub_subdirectory in sub_subdirectories: 
        # define the full path to current sub_subdirectory.
        sub_subdirectory_path = os.path.join(subdirectory_path, sub_subdirectory) # ./TW/SM02/EPZ.D

        # creating the corresponding output directory
        output_directory = os.path.join(parent_subdirectory, sub_subdirectory) # ./preprocessing/SM02/EPZ.D
        os.makedirs(output_directory, exist_ok=True)

    # Use glob to find all files with a specific extension (e.g., .mseed) in the subdirectory.
    # data_files = glob.glob(sub_subdirectory_path) # no need to use glob
        data_files = os.listdir(sub_subdirectory_path)

    # Loop through each data file in the subdirectory and process them.
        for data_file in data_files:
            # Read the seismic data file into a Stream object.
            st = read(data_file)

            # Merge traces within the Stream if there is more than one trace.
            if len(st) > 1:
                st = st.merge(method=1, fill_value=0)

            # Preprocess the Stream.
            st.detrend('demean')
            st.detrend('linear')
            st.taper(type='hann', max_percentage=0.05)

            # Define the output file path and save the preprocessed Stream.
            output_file = os.path.join(output_directory, os.path.basename(data_file))
            st.write(output_file, format='SAC')

print("Preprocessing and saving completed for all directories.")

