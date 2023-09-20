# %%
# spectrogram test
from obspy import imaging
from obspy import read, UTCDateTime
import os
import glob
import matplotlib.pyplot as plt
from matplotlib import gridspec
path = '/raid1/SM_data/archive/2023/TW/remove_resp/SM01/TW.SM01.00.EPZ.D.2023.190'
st = read(path)
st_copy = st.copy()
st_freq = st_copy.filter("bandpass", freqmin=0.1, freqmax=10)
st_time = st_freq[0].times() # Times
st_data = st_freq[0].data # the signal


fig = plt.figure(layout= "constrained")
gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[1, 1], width_ratios=[1, 1, 0.05])
ax1 = plt.subplot(gs[0, :-1])
ax2 = plt.subplot(gs[1, :-1],sharex=ax1)
cax = plt.subplot(gs[1, -1]) 
#fig, (ax1, ax2) = plt.subplots(nrows = 2, sharex = True)
ax1.plot(st_time, st_data)
ax1.set_ylabel('Signal')

# spectrogram in ObsPy
st_freq.spectrogram(log=True, title='SM01'+str(st_freq[0].stats.starttime), axes = ax2)
# spectrogram setting for matplotlib
#Fs = 100
#NFFT = 1024
#ax2.specgram(st_data, NFFT=NFFT, Fs=Fs)
#ax2.set_xlabel('Times')
#ax2.set_ylabel('Frequency (Hz)')

# Create the colorbar for the spectrogram
cbar = plt.colorbar(ax2.list[0], cax=cax, format='%+2.0f')

# Set the label for the colorbar
cbar.set_label('Power/Frequency (dB/Hz)')
plt.show()
# %%
