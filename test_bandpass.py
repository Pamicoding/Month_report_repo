#%%
from obspy.core import read, UTCDateTime
import os
import glob

# Variable: directory location
parent_dir = '/raid1/SM_data/archive/2023/TW/remove_resp/'
output_dir = '/raid1/SM_data/archive/2023/TW/test'
os.makedirs(output_dir, exist_ok=True)

# create the list for iterating
station_list = os.listdir(parent_dir) # station
#azimuth_list = ['EPE', 'EPN', 'EPZ'] # azimuth (for for loop)
azimuth_list = os.listdir(os.path.join(parent_dir, 'SM01'))

# read the 239 (day of year) to test the bandpass filter!
for station in station_list:
    station_dir = os.path.join(parent_dir,station)
    for azimuth in azimuth_list:
        sac_data = glob.glob(os.path.join(station_dir,f"*{azimuth}*"))
        for data in sac_data:
            st = read(data)
            #print(st)
            #st.taper(type='hann', max_percentage=0.05) 
            # the command line above (taper) is needed when we use trim(). However, the result shows no differnce, it seems like we don't have to use it
            st.filter("bandpass", freqmin=0.1, freqmax=10)
            st.plot()

            # Save the preprocessed data in the output directory
            #processed_file = os.path.join(output_dir, os.path.basename(data).replace('.sac', '_bandpass.sac'))
            #st.write(processed_file, format='SAC')            

print('done')


# %%
