# %%
import obspy
import glob # package of searching
from obspy import UTCDateTime 
import matplotlib.pyplot as plt
import pandas as pd
import math
from geopy import distance

# define the variable
parent_dir = '/raid1/SM_data/archive/2023/TW/remove_resp/'

A = glob.glob(sac_path) 
evt_lon = 121.6912742 
evt_lat = 24.6895861
point1 = (evt_lat, evt_lon)
starttime_trim = UTCDateTime("2022-09-27T06:52:25.696")
endtime_trim = UTCDateTime("2022-09-27T06:52:35.696")
station_path = '/home/patrick/Work/Month_report_repo/station.csv'
# create the empty list to accomodate the iterate data
seismic_distance_sac = []
only_distance = []
station = []
for index, i in enumerate(A):
    st = obspy.read(i)
    sta_name = i[28:32]
    sta_all = pd.read_csv(station_path)
    selected_station = sta_all[sta_all['Station']==int(sta_name)].iloc[0] # using int to transform string into integer
    sta_lon = selected_station['Lon']
    sta_lat = selected_station['Lat']
    point2 = (sta_lat, sta_lon)
    dist = distance.distance(point1, point2).m
    print(f"Distance to station {sta_name}: {dist} meters")
    st[0].trim(starttime=starttime_trim, endtime=endtime_trim)
    time_sac = st[0].times()
    data_sac = st[0].data*30 + dist
    # append the data into list
    seismic_distance_sac.append(data_sac) # the record of waveform from each station 
    only_distance.append(dist) # the distance between the station and target
    station.append(selected_station) # the selected station information
#%%
# Checking whether the trace is empty
#for data, imposter in zip(seismic_distance_sac, station):
    #if len(data) != 2501:
        #print(f"this is {imposter}")
        #print(data)
#%%
# testify the empty trace (in this case, station 3039) condition
#path_3039 = '/home/patrick/Work/20220927/*3039*DPZ*.SAC'
#singlechannel = obspy.read(path_3039)
#singlechannel.plot() 
#%%
import numpy as np
fig = plt.figure(figsize=(8,20))
# adding the label
df = pd.DataFrame(station)
station_id = df['Station']
# Initialize lists for valid data and corresponding distances
valid_seismic_data = []
valid_distances = []
valid_station = []
# Filter out empty arrays and their corresponding distances
for data, dist_o, vs in zip(seismic_distance_sac, only_distance, station_id):
    if len(data) == 2501:  # Check if the array is not empty
        valid_seismic_data.append(data)
        valid_distances.append(dist_o)
        valid_station.append(vs)
station_list = [int(valid) for valid in valid_station]
d_round = np.round(valid_distances,1)
# Plot the valid data
for data, dist_o in zip(valid_seismic_data, valid_distances):
    plt.plot(time_sac, data, color='k', linewidth=0.8)
# plot the label 
for sl, dl in zip(station_list, d_round):
    plt.text(time_sac[-1]+0.1, dl, f"Station:{sl}", fontsize=6, verticalalignment='center')
# plot
plt.xlim(-1,12)
plt.xlabel("Time (s)")
plt.ylabel("Distance (m)")
plt.title("Seismic Data vs. Distance")
#plt.legend()
plt.show()
#plt.savefig('plot.png')

# %%





