import os
import glob
import calendar
import logging
import argparse
import multiprocessing
from argparse import RawDescriptionHelpFormatter
from datetime import datetime
import numpy as np
import pandas as pd
from obspy import read, UTCDateTime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib import gridspec
from geopy import distance

def format_number(number):
    number_str = str(number)
    num_digits = len(number_str)
    num_zeros = 3 - num_digits
    # Add the leading zeros if the num_zeros != 0.
    formatted_number = '0' * num_zeros + number_str
    return formatted_number # transfer the 1 to 001

def scientific_formatter(value, pos): # parameter "pos" is a expectation of Matplotlib, in other words, this is built in parameter even we don't assign it.
    if value == 0: # avoid the 0 input
        return "0"
    exp = np.floor(np.log10(np.abs(value))) # np.floor is a round method to the nearest integer.
    coeff = value / 10**exp
    return f"${coeff:.0f} \\times 10^{{{int(exp)}}}$"


def parse_arguments():
    parser = argparse.ArgumentParser(description='for event analysis.\n\n'
                                     'Example usage:\n'
                                     'For waveform + spectrogram:\n'
                                     'python event_analysis.py --mode=wave_spec --month_index=4 --event_day=94 --event_time=2024-03-25T10:13:37 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/  \n\n'
                                     'For waveform arrange by distance: \n'
                                     'python event_analysis.py --mode=wave_dist --month_index=4 --event_day=94 --event_time=2024-03-25T10:13:37 --event_lon=121.56  --event_lat=24.01 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo  --station_location_file=/home/patrick/Work/Month_report_repo/station.csv\n\n'
                                     'For running both: \n'
                                     'python event_analysis.py --mode=all --month_index=4 --event_day=94 --event_time=2024-03-25T10:13:37 --event_lon=121.56  --event_lat=24.01 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo  --station_location_file=/home/patrick/Work/Month_report_repo/station.csv\n\n'
                                     ,formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-m','--mode', type=str, choices=['wave_spec','wave_dist','all'], default='all',help='Select the mode.')
    parser.add_argument('-i', '--month_index',type=int,default=None,help='a month just passed.')
    parser.add_argument('-d', '--event_day', type=int, default=None, help='event day of the year.')
    parser.add_argument('-t', '--event_time', type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S'), default=None, help='event time.')
    parser.add_argument('-lon','--event_lon', type=float, default=None,help='Longitude of event.')
    parser.add_argument('-lat','--event_lat', type=float, default=None,help='Latitude of event.')
    parser.add_argument('-p', '--parent_dir', type=str, default='/raid1/SM_data/archive/2024/TW', help='Path to the parent directory of data.')
    parser.add_argument('-o','--output_parent_dir', type=str,default='/home/patrick/Work/Month_report_repo/',help='output parent directory.')
    parser.add_argument('-s','--station_location_file', type=str, default='/home/patrick/Work/Month_report_repo/station.csv',help='Path of station location.')
    args = parser.parse_args()
    return args

def wave_spec(equip):
    args = parse_arguments()
    time_window = time_window_wave_spec
    logging.basicConfig(filename=os.path.join(args.output_parent_dir,'log','wave_spec.log'),level=logging.INFO, filemode='a') 
    starttime_trim = event_time - time_window 
    endtime_trim = event_time + time_window 
    parent_dir = args.parent_dir 
    output_dir = os.path.join(args.output_parent_dir,'output', f"{year}_{month}", f"{event_time}")
    os.makedirs(output_dir,exist_ok=True)

    fig = plt.figure(figsize=(15,8))
    outer_gs = gridspec.GridSpec(2, 4, figure=fig)
    for i, station in enumerate(station_list):
        layer_1 = os.path.join(parent_dir,'remove_resp',station,f'*{equip}*')
        try:
            data_path = glob.glob(layer_1)[0]
            st = read(data_path)
            st[0].trim(starttime=starttime_trim, endtime=endtime_trim)
            st.taper(type='hann', max_percentage=0.05)
            st.filter("bandpass", freqmin=0.1, freqmax=10)
            st_time = st[0].times() # Times
            st_data = st[0].data # the signal
            # set the axes
            inner_gs = gridspec.GridSpecFromSubplotSpec(2, 3,
                                                subplot_spec=outer_gs[i // 4, i % 4],
                                                height_ratios=[1, 2.5],
                                                width_ratios=[1, 1, 0.05])
            ax1 = plt.subplot(inner_gs[0, :-1])
            ax2 = plt.subplot(inner_gs[1, :-1],sharex=ax1) 

            # ax1
            ax1.plot(st_time, st_data, linewidth = 0.5, color='k', alpha = 0.6)
            ax1.grid(visible=True, color='lightgray')
            ax1.set_title( f'{station}_{equip[:3]}', fontsize = 20)
            
            # ax2
            NFFT = 256
            cmap = plt.get_cmap('turbo')
            im = ax2.specgram(st[0].data, Fs=st[0].stats.sampling_rate, NFFT=NFFT, cmap=cmap)
            # For simplifying the output, we only plot color bar and label in specific grid location. 
            if i not in [0, 1, 2, 4, 5, 6]:
                # Add a colorbar
                cax = plt.subplot(inner_gs[1, -1])
                cbar = plt.colorbar(im[3], format='%+2.0f', cax=cax)
                cbar.set_label('Amplitude (dB)')
            # Set the title, label
            if i not in [0, 1, 2, 3]:
                ax2.set_xlabel('Times (s)', fontsize = 12)
            if i not in [1, 2, 3, 5, 6, 7]:
                ax2.set_ylabel('Frequency (Hz)', fontsize = 12)
            ax2.set_yscale('log')
            ax2.set_xlim(0,time_window*2)
            ax2.set_ylim(0.1, 10)
            # Customize the y-axis tick labels to be in scientific notation
            ax2.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))
            plt.subplots_adjust(wspace=0.3, hspace=0.3)       
        except IndexError:
            logging.info(f"{equip}_{station} do not have the data")
    filename = f"wavespec_{equip[:3]}.png"
    file_path = os.path.join(output_dir,filename)
    plt.savefig(file_path, dpi=300, bbox_inches = 'tight')
    logging.info(f'{station}_{equip} done')

def wave_dist(equip):
    args = parse_arguments()
    time_window = time_window_wave_dist
    logging.basicConfig(filename=os.path.join(args.output_parent_dir,'log','wave_dist.log'),level=logging.INFO ,filemode='a') 
    evt_lon = args.event_lon
    evt_lat = args.event_lat
    evt_point = (evt_lat, evt_lon) 
    starttime_trim = event_time - time_window
    endtime_trim = event_time + time_window
    parent_dir = os.path.join(args.parent_dir,'remove_resp')
    output_dir = os.path.join(args.output_parent_dir,'output', f"{year}_{month}", f"{event_time}")
    os.makedirs(output_dir, exist_ok=True)
    station_path = args.station_location_file
    # loop
    sac_data = []
    distance_data = []
    station_data = []
    for station in station_list:
        layer_1 = os.path.join(parent_dir, station) 
        sac_select = glob.glob(os.path.join(layer_1, f'*{equip}*')) 
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
            st[0].trim(starttime=starttime_trim, endtime=endtime_trim)
            sampling_rate = 1 / st[0].stats.sampling_rate
            time_sac = np.arange(0,2*time_window+sampling_rate,sampling_rate) # using array to ensure the time length as same as time_window.
            x_len = len(time_sac)
            data_sac_raw = st[0].data / max(st[0].data) # normalize the amplitude.
            data_sac_raw = data_sac_raw*100 + dist # amplify the amplitude. Here we multiply to 100.
            data_sac = np.pad(data_sac_raw, (0, x_len - len(data_sac_raw)), mode='constant', constant_values=np.nan) # adding the Nan to ensure the data length as same as time window.
            sac_data.append(data_sac)  
            distance_data.append(dist) 
            station_data.append(station) 
        except Exception as e:
            logging.info(f'{e} existed in {station}_{equip}')
    # plotting
    plt.figure(figsize=(15,40))
    d_round = np.round(distance_data,1)
    # Plot the valid data
    for data in sac_data:
        plt.plot(time_sac, data, color='k', linewidth=0.8)
    for sl, dl in zip(station_data, d_round):
        plt.text(time_sac[-1]+1, dl, f"{sl}", fontsize=20, verticalalignment='center')
    # plot
    plt.xlim(0,120)
    plt.xticks(fontsize = 15)
    plt.gca().xaxis.set_minor_locator(MultipleLocator(5))
    plt.tick_params(axis='x', which='major', length=6, width=2)
    plt.tick_params(axis='x', which='minor', length=4, width=1)
    plt.xlabel("Time (s)", fontsize = 25)
    plt.title(f"{event_time}_{equip},\ntime window=±{time_window}s, bandpass: 0.1-10 Hz", fontsize = 25)
    filename = f"{equip[:3]}_signal_dist.png"
    file_path = os.path.join(output_dir,filename) 
    plt.savefig(file_path, dpi=300, bbox_inches = 'tight')
    logging.info(f'{station}_{equip} done')

if __name__ == '__main__':
    args = parse_arguments()
    os.makedirs(os.path.join(args.output_parent_dir,'log'),exist_ok=True)
    year = 2024
    month = calendar.month_name[args.month_index]
    day = format_number(args.event_day)
    event_time = UTCDateTime(args.event_time)
    station_list = ['SM01','SM02','SM06','SM09','SM19','SM37','SM39','SM40']
    equip_list = [f'EPZ.D.{year}.{day}',f'HLZ.D.{year}.{day}']
    time_window_wave_spec = 300
    time_window_wave_dist = 60
    if args.mode == 'wave_spec':
        #main
        pool = multiprocessing.Pool(processes=2)
        pool.map(wave_spec, equip_list)

        pool.close()
        pool.join()
    if args.mode == 'wave_dist':
        #main
        pool = multiprocessing.Pool(processes=2)
        pool.map(wave_dist, equip_list)

        pool.close()
        pool.join()
    if args.mode == 'all':
        # pool for wave_spec
        pool_1 = multiprocessing.Pool(processes=2)
        pool_1.map(wave_spec, equip_list)

        pool_1.close()
        pool_1.join()
        # pool for wave_list
                #main
        pool_2 = multiprocessing.Pool(processes=2)
        pool_2.map(wave_dist, equip_list)

        pool_2.close()
        pool_2.join()