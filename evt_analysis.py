# %%
import obspy
from obspy import read
import os
import logging
import numpy as np
import glob # package of searching
from obspy import UTCDateTime 
import matplotlib.pyplot as plt
import pandas as pd
import math
from geopy import distance

logging.basicConfig(filename='event.log',level=logging.INFO ,filemode='w',)
# define the variable
parent_dir = '/raid1/SM_data/archive/2023/TW/remove_resp/'
output_dir = '/home/patrick/Work/Month_report_repo/event_spectrogram'
day = '*263*'
myday = 263
station_list = os.listdir(parent_dir)
# Create the directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
# event lon, lat 
evt_lon = 121.38
evt_lat = 22.89
evt_point = (evt_lat, evt_lon)
starttime_trim = UTCDateTime("2023-09-20T12:35:29")
endtime_trim = UTCDateTime("2023-09-20T12:37:29")
station_path = '/home/patrick/Work/Month_report_repo/station.csv'

# create the empty list to accomodate the iterate data
sac_data = []
distance_data = []
station_data = []
for station in station_list:
    try:
        layer_1 = os.path.join(parent_dir, station)
        sac_select = glob.glob(os.path.join(layer_1, day)) # the day we want to trim
        st = read(sac_select[0])
        sta_loc = pd.read_csv(station_path)
        selected_station = sta_loc[sta_loc['Station']==station].iloc[0]
        sta_lon = selected_station['Lon']
        sta_lat = selected_station['Lat']
        sta_point = (sta_lat, sta_lon)
        dist = distance.distance(evt_point, sta_point).m
        logging.info(f"Distance to station {station}: {dist} meters")
        st[0].trim(starttime=starttime_trim, endtime=endtime_trim)
        time_sac = st[0].times()
        data_sac = st[0].data*150000000 + dist
        sac_data.append(data_sac) # the record of waveform from each station 
        distance_data.append(dist) # the distance between the station and target
        station_data.append(station) # the selected station information    
    except Exception as e:
        logging.error(f"the error from {station} is:{e}")
        #logging.debug()
'''        
    for index, i in enumerate(A):
        st = obspy.read(i)
        sta_name = i[28:32]
        sta_all = pd.read_csv(station_path)
        selected_station = sta_all[sta_all['Station']==int(sta_name)].iloc[0] # using int to transform string into integer
        sta_lon = selected_station['Lon']
        sta_lat = selected_station['Lat']
        point2 = (sta_lat, sta_lon)
        dist = distance.distance(evt_point, point2).m
        print(f"Distance to station {sta_name}: {dist} meters")
        st[0].trim(starttime=starttime_trim, endtime=endtime_trim)
        time_sac = st[0].times()
        data_sac = st[0].data*30 + dist
        # append the data into list
        seismic_distance_sac.append(data_sac) # the record of waveform from each station 
        only_distance.append(dist) # the distance between the station and target
        station.append(selected_station) # the selected station information
'''

fig = plt.figure(figsize=(10,50))
d_round = np.round(distance_data,1)
# Plot the valid data
for data, dist_o in zip(sac_data, distance_data):
    plt.plot(time_sac, data, color='k', linewidth=0.8)
# plot the label 
for sl, dl in zip(station_data, d_round):
    plt.text(time_sac[-1]+1, dl, f"{sl}", fontsize=20, verticalalignment='center')
# plot
plt.xlim(0,120)
plt.xlabel("Time (s)")
plt.ylabel("Distance (m)")
#plt.yscale('log')
plt.title("Seismic Data vs. Distance")
#plt.legend()
# Display the plot0
filename = f"{myday}_signal_dist_b.png"
file_path = os.path.join(output_dir,filename)
plt.savefig(file_path, dpi=300, bbox_inches = 'tight')

# %%





