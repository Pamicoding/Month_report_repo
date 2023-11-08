#%%
import os
import glob
from  obspy.imaging.scripts.scan import Scanner
from obspy import read, UTCDateTime

# variable
month = 'October'
starttime = UTCDateTime(2023, 10, 1)
endtime = UTCDateTime(2023, 10, 31)
title = f"{month}_data_availability"
equip_list = ['EPZ.D','HLZ.D']
# loop
for equip in equip_list:
    scanner = Scanner()
    for i in glob.glob('/raid1/SM_data/archive/2023/TW/remove_resp/SM*/%s%s%s' %('*', equip, '*')):
        scanner.parse(i)
    scanner.plot(starttime=starttime, endtime=endtime, outfile=f'{title}_{equip}.png', print_gaps=True)
# %%
