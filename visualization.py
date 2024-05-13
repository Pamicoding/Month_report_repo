import os
import glob
import logging
import calendar
import argparse
from argparse import RawDescriptionHelpFormatter
import multiprocessing
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import obspy
from obspy import read, Stream
from obspy.signal import PPSD
from  obspy.imaging.scripts.scan import Scanner
from obspy import read, UTCDateTime

def format_number(number):
    number_str = str(number)
    num_digits = len(number_str)
    num_zeros = 3 - num_digits
    # Add the leading zeros if the num_zeros != 0.
    formatted_number = '0' * num_zeros + number_str
    return formatted_number # transfer the 1 to 001
# for transforming the y_label into 1x10^1 form
def scientific_formatter(value, pos): # parameter "pos" is a expectation of Matplotlib, in other words, this is built in parameter even we don't assign it.
    if value == 0: # avoid the 0 input
        return "0"
    exp = np.floor(np.log10(np.abs(value))) # np.floor is a round method to the nearest integer.
    coeff = value / 10**exp
    return f"${coeff:.0f} \\times 10^{{{int(exp)}}}$"

def parse_arguments():
    parser = argparse.ArgumentParser(description='Visualization of condition of instrument.\n\n'
                                     'Example usage:\n'
                                     'For seis_status:\n'
                                     'python visualization.py --mode=seis_status --month_index=4 --output_parent_dir=/home/patrick/Work/Month_report_repo/ \n\n'
                                     'For PSD: \n'
                                     'python visualization.py --mode=psd --month_index=4 --start_day=92 --end_day=122 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo \n\n'
                                     'For monthly spectrogram: \n'
                                     'python visualization.py --mode=spec --month_index=4 --start_day=92 --end_day=122 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo \n\n'
                                     ,formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-m','--mode', type=str, choices=['seis_status','psd','spec','all'], default=None,help='Select the mode.')
    parser.add_argument('-i', '--month_index',type=int,default=None,help='a month just passed.')
    parser.add_argument('-s', '--start_day', type=int, default=None, help='Starting day of the year')
    parser.add_argument('-e', '--end_day', type=int, default=None, help='Starting day of the year')
    parser.add_argument('-p', '--parent_dir', type=str, default='/raid1/SM_data/archive/2024/TW', help='Path to the parent directory of data.')
    parser.add_argument('-o','--output_parent_dir', type=str,default='/home/patrick/Work/Month_report_repo/',help='output_parent_dir')
    args = parser.parse_args()
    return args

def seis_status():
    args = parse_arguments()
    month = calendar.month_name[args.month_index]
    month_end = calendar.monthrange(year, args.month_index)[1]
    output = os.path.join(args.output_parent_dir,'output',f'{year}_{month}')
    os.makedirs(output, exist_ok=True)
    starttime = UTCDateTime(year, args.month_index, 1)
    endtime = UTCDateTime(year, args.month_index, month_end)
    title = f"{month}_data_availability"

    for equip in equip_list:
        scanner = Scanner()
        for i in glob.glob(f"/raid1/SM_data/archive/{year}/TW/SM*/{'*'+equip+'*'}"): # change it when this is first time.
            scanner.parse(i)
        scanner.plot(starttime=starttime, endtime=endtime, outfile=f'{output}/{title}_{equip}.png', print_gaps=True)

def psd(station):
    args = parse_arguments()
    logging.basicConfig(filename=os.path.join(args.output_parent_dir,'log', f'psd.log'),level=logging.INFO, filemode='a')
    month = calendar.month_name[args.month_index]
    day_range = range(args.start_day, args.end_day)
    output = os.path.join(args.output_parent_dir,'output',f"{year}_{month}",'PSD')
    os.makedirs(output, exist_ok=True)

    subdirectory_path = os.path.join(args.parent_dir, station) # ./TW/SM01/
    for equip in equip_list:
        current_stream = Stream() # initial the stream when changing the station
        try:
            sub_subdirectory_path = os.path.join(subdirectory_path, equip) # ./TW/SM01/EPZ.D
        except Exception as e:
            logging.info(f"{e} existed in {station}_{equip}")
        for day in day_range:
            day_trans = format_number(day)
            day_file = f"{equip}.{year}.{day_trans}"
            day_path = os.path.join(sub_subdirectory_path, f'*{day_file}*') # ./TW/SM01/EPZ.D/*EPZ.D.2023.001*
            sac_data = glob.glob(day_path)
            try:
                # Read the seismic data file into a Stream object.
                st = read(sac_data[0])
                # Merge traces within the Stream if there is more than one trace.
                if len(st) > 1:
                    st.merge(method=1, fill_value='interpolate')
                current_stream += st
            except Exception as e:
                # handle the exception and log it
                logging.error(f"Error processing thorugh the {station}_{equip}_{day} day of year: {str(e)}")
        current_stream = current_stream.merge(fill_value='interpolate')
        if equip[:2] == 'EP':
            # EP
            paz_sts2 = paz_EP
        else:
            # HL
            paz_sts2 = paz_HL
        try:
            plt.subplots(figsize=(8,6))
            ppsd = PPSD(current_stream[0].stats, paz_sts2)
            ppsd.add(current_stream)
            ppsd.plot(filename=os.path.join(output, f"{station}_{equip[:2]}_psd.png"),cmap=obspy.imaging.cm.pqlx, period_lim=(0.5,100), xaxis_frequency=True)
            logging.info(f"{station}_{equip} ppsd finish!")
        except Exception as e:
            logging.info(f"{e} existed in {station}_{equip}")
    logging.info(f"{station}'s ppsd is done")

def spec(station):
    args = parse_arguments()
    logging.basicConfig(filename=os.path.join(args.output_parent_dir,'log', f'spec.log'),level=logging.INFO, filemode='a')
    month = calendar.month_name[args.month_index]
    day_range = range(args.start_day, args.end_day)
    days = calendar.monthrange(year, args.month_index)[1]
    mydata_path = os.path.join(args.output_parent_dir,'output',f"{year}_{month}")
    station_dir = os.path.join(args.parent_dir,'remove_resp', station) # ./remove_resp/SM01
    for equip in equip_list:
        current_stream = Stream() # initial the stream when changing the station
        for day in day_range:
            day_path = os.path.join(station_dir, f'*{equip}.{year}.{format_number(day)}*') # ./remove_resp/SM01/*EPZ.D.2023.001*
            sac_data = glob.glob(day_path)
            try:
                st = read(sac_data[0]) # whole day stream
                #st.taper(type='hann', max_percentage=0.05) # we need to add taper to make sure the filter can sart from 0. (but I don't know why)
                #st_freq = st.filter("bandpass", freqmin=0.1, freqmax=50, zerophase=True) # whole month spec do not need to filter.
                current_stream += st
            except Exception as e:
                logging.error(f"Error processing thorugh the {station}_{equip}_{day} day of year: {str(e)}")
        current_stream = current_stream.merge(fill_value='interpolate')
        
        # for plotting
        fig, ax = plt.subplots(figsize=(14,10))
        # Create the spectrogram on ax
        NFFT = 1024*8
        num_overlap = 512*8
        cmap = plt.get_cmap('jet')
        if equip == 'EPZ.D':
            ax.specgram(current_stream[0].data, Fs=current_stream[0].stats.sampling_rate, NFFT=NFFT, noverlap=num_overlap, cmap=cmap, vmin=-250, vmax=-120)
        else:
            ax.specgram(current_stream[0].data, Fs=current_stream[0].stats.sampling_rate, NFFT=NFFT, noverlap=num_overlap, cmap=cmap, vmin=-250, vmax=-120)
        # Add a colorbar
        cbar_x = ax.get_position().x1 + 0.01
        cbar_y = ax.get_position().y0
        cbar_h = ax.get_position().height
        cbar = fig.add_axes([cbar_x, cbar_y, 0.02, cbar_h])
        cbar.tick_params(labelsize=15)
        cbar.set_ylabel('(db)', fontsize = 20)
        plt.colorbar(ax.images[0], cax=cbar)

        # Set the label
        ax.set_title(f"{station}_{equip}", fontsize = 20)
        ax.set_xlabel('Date (UTC)', fontsize = 20, labelpad=10)
        ax.set_ylabel('Frequency (Hz)', fontsize = 20,labelpad=10)
        ax.tick_params(axis='x', which='major', length = 5, width= 2)
        ax.tick_params(axis='y', labelsize=15, which='major', length = 6, width= 2)
        ax.tick_params(axis='y', which='minor', length = 4, width= 1)
        # Customize the y-axis tick labels to be in scientific notation
        ax.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))
        ax.set_ylim(0.005, 50)
        # about setting the x_label as time
        start_time = current_stream[0].stats.starttime
        end_time = start_time + timedelta(days=days)
        tick_positions = np.arange(0, end_time - start_time, 86400)

        time_label = []
        current_time = start_time
        while current_time.month == start_time.month:
            time_label.append(current_time.strftime('%Y-%m-%d'))
            current_time += 86400

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(time_label, rotation=45, ha = "right", fontsize = 15)
        ax.set_yscale('log')
        save_path = os.path.join(mydata_path, f"{station}_{equip[:3]}_spec.png")
        plt.savefig(save_path, dpi=300, bbox_inches = 'tight')
        logging.info(f"save your tears for {station}_{equip}")
    logging.info(f'we done with {station}')


if __name__ == '__main__':
    args = parse_arguments()
    os.makedirs(os.path.join(args.output_parent_dir,'log'),exist_ok=True)
    print(args)
    year =2024
    equip_list = ['EPZ.D','HLZ.D']
    station_list = ['SM01','SM02', 'SM06', 'SM09', 'SM19', 'SM37', 'SM39', 'SM40']
    if args.mode == 'seis_status':
        seis_status()
    elif args.mode == 'psd':
        # variable
        paz_EP = {'poles': [-19.781+20.2027j, -19.781-20.2027j],
                'zeros': [0, 0, 0], # trans to displacement
                'gain': 1.0*27.7, # Using A0*INSTGAIN
                'sensitivity': 546976.0}
        paz_HL = {'poles': [-977+328j, -977-328j,
                            -1486+2512j, -1486-2512j,
                            -5736+4946j, -5736-4946j],
                'zeros': [0, 0, -515+0j], # trans to displacement
                'gain': 1.007725E+18*1.02, # Using A0*INSTGAIN
                'sensitivity': 408000.0}
        # main
        pool = multiprocessing.Pool(processes=8)
        pool.map(psd, station_list)

        pool.close()
        pool.join()
    
    elif args.mode == 'spec':
        # main
        pool = multiprocessing.Pool(processes=8)
        pool.map(spec, station_list)

        pool.close()
        pool.join()
    elif args.mode == 'all': 
        print('I am still thinking about that, sorry')
        pass