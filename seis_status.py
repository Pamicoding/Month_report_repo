#%%
import os
import glob
from  obspy.imaging.scripts.scan import Scanner
from obspy import read, UTCDateTime
#%%
# variable
output ='/home/patrick/Work/Month_report_repo/output/2023_oct'
year = '2023'
month = 'October'
starttime = UTCDateTime(year, 10, 1)
endtime = UTCDateTime(year, 10, 31)
title = f"{month}_data_availability"
equip_list = ['EPZ.D','HLZ.D']
# loop
for equip in equip_list:
    scanner = Scanner()
    for i in glob.glob(f"/raid1/SM_data/archive/{year}/TW/remove_resp/SM*/{'*'+equip+'*'}"):
        scanner.parse(i)
    scanner.plot(starttime=starttime, endtime=endtime, outfile=f'{output}/{title}_{equip}.png', print_gaps=True)
#%%
