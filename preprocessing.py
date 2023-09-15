# %%

import obspy
from obspy.io.sac import attach_paz
from obspy.signal.invsim import corn_freq_2_paz
from obspy.signal import PPSD
import glob

corner_freq = 5
pre_filt = (0.05, 0.1, 30, 40)
damping = 0.7

filename = '/raid1/SM_data/archive/2023/TW/SM01/EPZ.D/TW.SM01.00.EPZ.D.2023.232'
Pzs_path = '/raid1/SM_data/TWSM2/SM01/SAC_PZs_TW_SM01_EPZ__2021.001.00.00.00.0000_2599.365.23.59.59.99999'
st = obspy.read(filename)
st.merge()
st.detrend('demean')
st.detrend('linear')


# Remove Instrument response
attach_paz(st[0], Pzs_path)
paz_1hz = corn_freq_2_paz(corner_freq, damp=damping)
st.simulate(paz_remove=paz_1hz, pre_filt=pre_filt)

st.write('.sac')

# follow the filename: 3039.FM.00.DPE.2023.002.20230102.SAC