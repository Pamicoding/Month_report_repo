# %%
from obspy import read
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors  # for setting colorbar
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec

# def function
def scientific_formatter(value, pos): # parameter "pos" is a expectation of Matplotlib, in other words, this is built in parameter even we don't assign it.
    """
    Custom tick formatter to display ticks in scientific notation.
    """
    if value == 0: # avoid the 0 input
        return "0"
    exp = np.floor(np.log10(np.abs(value))) # np.floor is a round method to the nearest integer.
    coeff = value / 10**exp
    return f"${coeff:.0f} \\times 10^{{{int(exp)}}}$"

path = '/raid1/SM_data/archive/2023/TW/remove_resp/SM01/TW.SM01.00.EPZ.D.2023.190'
st = read(path)
st_copy = st.copy()
st_freq = st_copy.filter("bandpass", freqmin=0.01, freqmax=45)
st_time = st_freq[0].times() # Times
st_data = st_freq[0].data # the signal


# set the axes
fig = plt.figure(figsize=(6,6))
gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[1, 2.5], width_ratios=[1, 1, 0.05])
ax1 = plt.subplot(gs[0, :-1])
ax2 = plt.subplot(gs[1, :-1],sharex=ax1)
cax = plt.subplot(gs[1, -1]) 

# ax1
ax1.plot(st_time, st_data, linewidth = 0.5, color='k', alpha = 0.6)
ax1.grid(visible=True, color='lightgray')
ax1.set_title('SM01' + str(st_freq[0].stats.starttime), fontsize = 12)
ax1.set_ylabel('Signal', fontsize=12)


# Create the spectrogram
NFFT = 256
cmap = plt.get_cmap('turbo')
im = ax2.specgram(st_freq[0].data, Fs=st_freq[0].stats.sampling_rate, NFFT=NFFT, cmap=cmap, vmin=-300, vmax=-120)
''' 
if we want to range the colorbar, we can add the parameter vmin, vmax into specgram function.
'''
# Add a colorbar
cbar = plt.colorbar(im[3], format='%+2.0f', cax=cax)
cbar.set_label('Amplitude (dB)')

# Set the title, label
ax2.set_xlabel('Times (s)', fontsize = 12)
ax2.set_ylabel('Frequency (Hz)', fontsize = 12)
ax2.set_yscale('log')
ax2.set_xlim(0,600)
ax2.set_ylim(0.05, 50)

# Customize the y-axis tick labels to be in scientific notation
ax2.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))

# Display the plot
plt.show()

# %%
