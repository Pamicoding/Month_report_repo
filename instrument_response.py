import obspy
from obspy import read, UTCDateTime
import os
from obspy.io.sac import attach_paz
from obspy.signal.invsim import corn_freq_2_paz
from obspy.signal import PPSD
import glob 
import io
# the file path
parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing'  
pzs_parent_dir = '/raid1/SM_data/TWSM2'
output_dir = '/raid1/SM_data/archive/2023/TW/remove_resp'
pzs_path = '/raid1/SM_data/TWSM2/SM01/SAC_PZs_TW_SM01_EPZ__2021.001.00.00.00.0000_2599.365.23.59.59.99999'
#pzs_data = glob.glob(pzs_path) # just denote one of the file ./raid1/SM_data/TWSM2/SM01/...EPZ

# variable
station_name = os.listdir(parent_dir)
azimuth_dir = os.listdir(os.path.join(parent_dir, 'SM01'))

# Create an output directory for processed data
os.makedirs(output_dir, exist_ok=True)

# trim settings
#trim_starttime = UTCDateTime("2023-07-09T22:06:33")
#trim_endtime = UTCDateTime("2023-07-09T22:16:33")
trim_starttime = UTCDateTime("2023-07-09T22:06:33")
trim_endtime = UTCDateTime("2023-07-09T22:16:33")
# instrument response settings
corner_freq = 5
pre_filt = (0.05, 0.1, 30, 40)
damping = 0.7
# loop for iterate data and create the process folder after removing instrument response
for name in station_name:
    layer_1 = os.path.join(output_dir, name)
    os.makedirs(layer_1, exist_ok=True) # create ./remove_resp/SM01
    for azi in azimuth_dir:
        sac_data_dir = os.path.join(parent_dir, name, azi) # ./preprocessing/SM01/EPZ.D
        sac_data = glob.glob(os.path.join(sac_data_dir, '*190*')) # Catch the file match the path ./preprocessing/SM01/EPZ.D/*EP*
        for data in sac_data:
            st = read(data) # copy() is no need to use here due to the file is already copy in last step.
            st.trim(starttime = trim_starttime, endtime = trim_endtime)
            
            #attach_paz(st[0], pzs_path)
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

