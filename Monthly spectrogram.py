# %%
from obspy import read
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors  # for setting colorbar
import numpy as np
import pandas as pd
import os 
import glob
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec
import logging

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
day_range = np.arange(213, 244, 1)
month = 'August'

# directory setting
parent_dir = '/raid1/SM_data/archive/2023/TW/remove_resp/'
station_list = os.listdir(parent_dir)

# data aggregation, using a dictionary
timeset = {}
dataset = {}

# tidy up the data
for station in station_list:
    logging.info(f"Now we are in station:{station}")
    station_dir = os.path.join(parent_dir, station) # ./remove_resp/SM01

    # initialize lists for time and signal data
    station_timeset=[]
    station_dataset=[]

    for day in day_range:
        logging.info(f"Now we are in the {day} day of year")
        day_trans = format_number(day)
        day_file = f"EPZ.D.2023.{day_trans}"
        day_path = os.path.join(station_dir, f'*{day_file}*') # ./remove_resp/SM01/*EPZ.D.2023.001*
        sac_data = glob.glob(day_path)

        try:
            st = read(sac_data[0]) # whole day stream
            st_freq = st.filter("bandpass", freqmin=0.1, freqmax=10) # filter
            st_time = st_freq[0].times() # get Times
            st_data = st_freq[0].data # the signal
            station_timeset.append(st_time)
            station_dataset.append(st_data)
            logging.info(f"the data of {day} day of year is pass, thank god")
        except Exception as e:
            # handle the exception and log it
            logging.error(f"Error processing thorugh the {day} day of year: {str(e)}")


    # store the data into dictionary    
    timeset[station] = np.concatenate(station_timeset)
    dataset[station] = np.concatenate(station_dataset)

# create a df and merge them into a df and save it as .csv
timesets_df = pd.DataFrame(timeset.items(), columns=['station', 'timeset'])
datasets_df = pd.DataFrame(dataset.items(), columns=['station', 'dataset'])
merge_df = pd.merge(timesets_df, datasets_df, on='station')

# Specify the file name you want to create
output_file_name = f'{month}_wholedata.csv'

# Check if the file already exists
if not os.path.exists(output_file_name):
    # Save the dataframe to the CSV file
    merge_df.to_csv(output_file_name, index=False)
    logging.info(f"The CSV file '{output_file_name}' has been created.")
else:
    logging.info(f"The CSV file '{output_file_name}' already exists. Skipping file creation.")

#%%
# plotting the monthly spectrogram
for name in station_list:
    y = dataset[name] # acquire the signal from dictionary
    x = timeset[name] # acquire the time from dictionary
'''
The ideal aggreagation of time
In my project, I'm trying to create a monthly spectrogram through the earthquack data. In our dataWe select the specfic time window (day of year), acquiring the  and I think we should append the index while 
acquiring the data. The reason to annotate the index is I want to classify different day before I merge 
all times together.
'''

# set the axes
fig = plt.figure(figsize=(6,6))
gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[1, 0.05])
ax = plt.subplot(gs[0, 0])
cax = plt.subplot(gs[0, 1]) 

# Create the spectrogram on ax
NFFT = 256
cmap = plt.get_cmap('turbo')
im = ax.specgram(st_freq[0].data, Fs=st_freq[0].stats.sampling_rate, NFFT=NFFT, cmap=cmap, vmin=-300, vmax=-120)
''' 
if we want to range the colorbar, we can add the parameter vmin, vmax into specgram function.
'''
# Add a colorbar
cbar = plt.colorbar(im[3], format='%+2.0f', cax=cax)
cbar.set_label('Amplitude (dB)')

# Set the title, label
ax2.set_xlabel('Times (s)', fontsize = 12)
ax2.set_ylabel('Frequency (Hz)', fontsize = 12)
ax2.set_xlim(0,600)

# Customize the y-axis tick labels to be in scientific notation
ax2.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))

# Display the plot
plt.show()

# %%
