# %%
import obspy
from obspy import read
import os
import logging
import numpy as np
import glob # package of searching
from obspy import UTCDateTime 
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd
import math
from geopy import distance

logging.basicConfig(filename='event.log',level=logging.INFO ,filemode='w',)
# variable
## time
year = 2023
month = 'oct'
day = 296
## event lon, lat, and time 
Mw = 5.94
evt_lon = 122.64
evt_lat = 24.10
evt_point = (evt_lat, evt_lon)
timee = "2023-10-23T23:05:28"
earthquake_time = UTCDateTime(f'{timee}')
time_window = 60 
starttime_trim = earthquake_time - time_window
endtime_trim = earthquake_time + time_window
## path
parent_dir = f'/raid1/SM_data/archive/{year}/TW/remove_resp/'
output_dir = f'/home/patrick/Work/Month_report_repo/output/{year}_{month}'
# Create the directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
station_path = '/home/patrick/Work/Month_report_repo/station.csv'
## list
station_list = os.listdir(parent_dir)
#station_list = ['SM01','SM02','SM06','SM19','SM39','SM40']
#station_list = ['SM01','SM02','SM06','SM09','SM19','SM39']
equip_list = ['EPZ.D','HLZ.D']
# loop
for equip in equip_list:
    # create the empty list to accomodate the iterate data
    sac_data = []
    distance_data = []
    station_data = []
    for station in station_list:
        layer_1 = os.path.join(parent_dir, station) # /raid1/SM_data/archive/2023/TW/remove_resp/SM01
        sac_select = glob.glob(os.path.join(layer_1, f'*{equip}*{day}*')) # /raid1/SM_data/archive/2023/TW/remove_resp/SM01/*THE DAY*
        try:
            st = read(sac_select[0])
            st.taper(type='hann', max_percentage=0.05)
            st.filter("bandpass", freqmin=0.1, freqmax=10)
            sta_loc = pd.read_csv(station_path)
            selected_station = sta_loc[sta_loc['Station']==station].iloc[0]
            sta_lon = selected_station['Lon']
            sta_lat = selected_station['Lat']
            sta_point = (sta_lat, sta_lon)
            dist = distance.distance(evt_point, sta_point).m
            logging.info(f"Distance to station {station}: {dist} meters")
            st[0].trim(starttime=starttime_trim, endtime=endtime_trim)
            time_sac = st[0].times()
            if equip == 'EPZ.D':
                data_sac = st[0].data*10000000 + dist
            else:
                data_sac = st[0].data / 8e10 + dist
            sac_data.append(data_sac) # the record of waveform from each station 
            distance_data.append(dist) # the distance between the station and target
            station_data.append(station) # the selected station information
        except Exception as e:
            logging.info(e)
    # plotting
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
    plt.xticks(fontsize = 15)
    plt.gca().xaxis.set_minor_locator(MultipleLocator(5))
    # Set the length and width of major ticks
    plt.tick_params(axis='x', which='major', length=6, width=2)
    # Set the length and width of minor ticks
    plt.tick_params(axis='x', which='minor', length=4, width=1)
    plt.xlabel("Time (s)", fontsize = 25)
    #plt.ylabel("Distance (m)")
    #plt.yscale('log')
    plt.title(f"{timee}_{equip}, Mw={Mw}\ntime window=±{time_window}s, bandpass: 0.1-10 Hz", fontsize = 25)
    #plt.legend()
    # Display the plot0
    filename = f"{day}_{equip[:3]}_signal_dist_2.png"
    file_path = os.path.join(output_dir,filename) # /home/patrick/Work/Month_report_repo/output/2023_oct/284_EPZ_signal_dist
    plt.savefig(file_path, dpi=300, bbox_inches = 'tight')
    #plt.show()
# %%





