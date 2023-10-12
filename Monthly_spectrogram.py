#%%
from obspy import read, Stream
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors  # for setting colorbar
import numpy as np
import pandas as pd
import os 
import glob
import numpy as np
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib import gridspec
import logging
from datetime import datetime, timedelta

# Initialize the logging system
logging.basicConfig(filename='test.log', level=logging.INFO, filemode='w')  # Create a log file

# def function
# for transforming the y_label into 1x10^1 form
def scientific_formatter(value, pos): # parameter "pos" is a expectation of Matplotlib, in other words, this is built in parameter even we don't assign it.
    """
    Custom tick formatter to display ticks in scientific notation.
    """
    if value == 0: # avoid the 0 input
        return "0"
    exp = np.floor(np.log10(np.abs(value))) # np.floor is a round method to the nearest integer.
    coeff = value / 10**exp
    return f"${coeff:.0f} \\times 10^{{{int(exp)}}}$"


# convert 1 to 001 for searching
def format_number(number):
    number_str = str(number) # Convert the number to a string
    num_digits = len(number_str) # Determine the number of digits in the original number
    num_zeros = 3 - num_digits # Calculate the number of leading zeros needed
    formatted_number = '0' * num_zeros + number_str # Add the leading zeros and return the formatted number as a string
    return formatted_number 

# variables
day_range = np.arange(244, 274, 1)
month = 'September'
days = 30
# directory setting
parent_dir = '/raid1/SM_data/archive/2023/TW/remove_resp/'
station_list = os.listdir(parent_dir)
#merged_stream = {}

# tidy up the data
for station in station_list:
    logging.info(f"Now we are in station:{station}")
    station_dir = os.path.join(parent_dir, station) # ./remove_resp/SM01
    current_stream = Stream() # initial the stream when changing the station

    for day in day_range:
        logging.info(f"Now we are in the {day} day of year")
        day_trans = format_number(day)
        day_file = f"EPZ.D.2023.{day_trans}"
        day_path = os.path.join(station_dir, f'*{day_file}*') # ./remove_resp/SM01/*EPZ.D.2023.001*
        sac_data = glob.glob(day_path)

        try:
            st = read(sac_data[0]) # whole day stream
            st_freq = st.filter("bandpass", freqmin=0.1, freqmax=45) # filter
            logging.info(f"{st_freq}")
            current_stream += st_freq
            logging.info(f"the data of {day} day of year is merging, thank god")
        except Exception as e:
            # handle the exception and log it
            logging.error(f"Error processing thorugh the {day} day of year: {str(e)}")

    current_stream = current_stream.merge(fill_value='interpolate')
    logging.info(f"merging complete")
    
    # for plotting
    fig, ax = plt.subplots(figsize=(14,10))

    # Create the spectrogram on ax
    NFFT = 1024*8
    num_overlap = 512*8
    cmap = plt.get_cmap('turbo')
    ax.specgram(current_stream[0].data, Fs=current_stream[0].stats.sampling_rate, NFFT=NFFT, noverlap=num_overlap, cmap=cmap, vmin=-250, vmax=-100)
    ''' 
    if we want to range the colorbar, we can add the parameter vmin, vmax into specgram function.
    '''

    # Add a colorbar
    cbar_x = ax.get_position().x1 + 0.01
    cbar_y = ax.get_position().y0
    cbar_h = ax.get_position().height
    cbar = fig.add_axes([cbar_x, cbar_y, 0.02, cbar_h])
    plt.colorbar(ax.images[0], label='(dB)', cax=cbar)


    # Set the label
    ax.set_title(f"{station}", fontsize = 20)
    ax.set_xlabel('Date (UTC)', fontsize = 20, labelpad=10)
    ax.set_ylabel('Frequency (Hz)', fontsize = 20,labelpad=10)

    # Customize the y-axis tick labels to be in scientific notation
    ax.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))
    ax.set_ylim(0.5, 50)
    # about setting the x_label as time
    start_time = current_stream[0].stats.starttime
    end_time = start_time + timedelta(days=days)
    tick_positions = np.arange(0, end_time - start_time, 86400)

    time_label = []
    current_time = start_time
    while current_time.month == start_time.month:
        time_label.append(current_time.strftime('%Y-%m-%d'))
        current_time += 86400
        logging.info(f"the {current_time} next")

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(time_label, rotation=45, ha = "right")
    ax.set_yscale('log')
    mydata_path = '/home/patrick/Work/Month_report_repo/event_spectrogram/'
    save_path = os.path.join(mydata_path, f"{station}_spectrogram.png")
    plt.savefig(save_path, dpi=300, bbox_inches = 'tight')
    plt.show()
    logging.info(f"save your tears for {station}")


    #merged_stream[f"st_all_{station}"] = current_stream
    #logging.info(f"the {station} stream is update in dictionary!")

#%%
