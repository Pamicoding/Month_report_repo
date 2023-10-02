#%%
from obspy import read
from obspy.io.sac import attach_paz

path = '/raid1/SeiscomP/archive/2023/TW/SM01/EPZ.D/TW.SM01.00.EPZ.D.2023.260'
file = '/raid1/SM_data/TWSM2/SM01/SAC_PZs_TW_SM01_EPZ__2021.001.00.00.00.0000_2599.365.23.59.59.99999'
st = read(path)
attach_paz(st[0], file)

# %%
