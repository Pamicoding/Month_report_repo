#%%
import obspy
from obspy import read, UTCDateTime
import os
from obspy.io.sac import attach_paz
from obspy.signal.invsim import corn_freq_2_paz
from obspy.signal import PPSD
import glob 

# the file path
parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing'  
station_name = os.listdir(parent_dir)
azimuth_dir = ['EPE.D', 'EPN.D', 'EPZ.D']
pzs_azimuth = ['EPE', 'EPN', 'EPZ']
pzs_parent_dir = '/raid1/SM_data/TWSM2'
output_dir = '/raid1/SM_data/archive/2023/TW/remove_resp'

# Create an output directory for processed data
os.makedirs(output_dir, exist_ok=True)

# trim settings
trim_starttime = UTCDateTime("")
trim_endtime = UTCDateTime("")

# instrument response settings
corner_freq = 5
pre_filt = (0.05, 0.1, 30, 40)
damping = 0.7

# loop for iterate data and create the process folder after removing instrument response
for name in station_name:
    layer_1 = os.path.join(output_dir, name)
    os.makedirs(layer_1, exist_ok=True) # create ./remove_resp/SM01
    for azi_ori, azi_pzs in zip(azimuth_dir, pzs_azimuth):
        sac_data_dir = os.path.join(parent_dir, name, azi_ori) # ./preprocessing/SM01/EPZ.D
        pzs_data_dir = os.path.join(pzs_parent_dir, name) # ./TWSM2/SM01
        sac_data = glob.glob(os.path.join(sac_data_dir, '*EP*')) # Catch the file match the path ./preprocessing/SM01/EPZ.D/*EP*
        pzs_data = glob.glob(os.path.join(pzs_data_dir, f'*{azi_pzs}*')) # Catch the file match the path ./raid1/SM_data/TWSM2/SM01/*EPZ*
        layer_2 = os.path.join(layer_1, azi_ori) 
        os.makedirs(layer_2, exist_ok=True) # create ./remove_resp/SM01/EPE.D
        for data in sac_data:
            st = read(data)
            st.trim(starttime = trim_starttime, endtime = trim_endtime)
            attach_paz(st[0], pzs_data[0])
            paz_1hz = corn_freq_2_paz(corner_freq, damp=damping)
            st.simulate(paz_remove=paz_1hz, pre_filt=pre_filt)

            # Save the preprocessed data in the output directory
            processed_file = os.path.join(layer_2, os.path.basename(data).replace('.sac', '_processed.sac'))
            st.write(processed_file, format='SAC')

'''
----THOUGHT----
1. maybe we don't need that much directory(for N, E, and Z), comparing to ILAN2022 to see if it's reasonable.
'''