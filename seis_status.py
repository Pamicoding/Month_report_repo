#%%
import os
import glob
from  obspy.imaging.scripts.scan import Scanner
from obspy import read, UTCDateTime

# variable
month = 'August'
starttime = UTCDateTime(2023, 8, 1)
endtime = UTCDateTime(2023, 8, 31)
title = f"{month}_data_availability"
scanner = Scanner()
for i in glob.glob('/raid1/SM_data/archive/2023/TW/remove_resp/SM*/%s%s%s' %('*', 'EPZ', '*')):
    scanner.parse(i)
scanner.plot(starttime=starttime, endtime=endtime, outfile=title, print_gaps=True)
# %%
