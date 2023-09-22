#%%
from obspy.core import read, UTCDateTime
import os
import glob

# directory location
parent_dir = '/raid1/SM_data/archive/2023/TW/preprocessing/'

# create the list for iterating
station_list = os.listdir(parent_dir) # station
azimuth_list = os.listdir(os.path.join(parent_dir, 'SM01')) # azimuth
# to acquire the filehead
for station in station_list:
    station_dir = os.path.join(parent_dir,station,'EPZ.D')
    sac_data = glob.glob(os.path.join(station_dir,"*191*"))
    for data in sac_data:
        st = read(data)
        print(st[0].stats)

'''
----MEMO----
Info above did not contain the longitude and latitude data,
opening the PZs file directly to acquire the info.
'''

# %%
