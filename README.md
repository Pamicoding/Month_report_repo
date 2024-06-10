# Monthly report   
## Directory structure    
```
Directory structure of data in this repository (take SM station as an example.)

/raid1/SM_data/archive/2024/TW (parent_dir)
├── preprocessing (optional generated, if u use mode='all', only remove_resp directory being created.)
│   └── SM01
│       └── EPZ.D
│           └── TW.SM01.00.EPZ.D.2024.123
├── remove_resp (generated after removing instrument response, for most of visualization)
│   └── SM01
│       ├── TW.SM01.00.EPZ.D.2024.122
│       └── TW.SM01.00.HLZ.D.2024.122
├── SM01 (original data directory, for seis_status & PSD)
│   └── EPZ.D
│       ├── TW.SM01.00.EPZ.D.2024.122
│       └── TW.SM01.00.EPZ.D.2024.123
```
```
Directory structure of output in this repository (take 2024_April as an example.)

/home/patrick/Work/Month_report_repo/ (output_parent_dir)
├── log  
│   ├── spec.log
│   └── response_SM01.log
├── output
│   └── 2024_April
│       ├── April_data_availibility_EPZ.D.png
│       └── SM01_EPZ_spec.png
```
## Data preparation    
```
usage: preprocessing.py [-h] [-p PARENT_DIR] [-s START_DAY] [-e END_DAY] [-o OUTPUT_PARENT_DIR] [-m {preprocessing,ins_resp}]

options:
  -h, --help            show this help message and exit
  -p PARENT_DIR, --parent_dir PARENT_DIR
                        Path to the parent directory of data.
  -s START_DAY, --start_day START_DAY
                        Starting day of the year
  -e END_DAY, --end_day END_DAY
                        Starting day of the year
  -l OUTPUT_PARENT_DIR, --output_parent_dir OUTPUT_PARENT_DIR
                        Path of output parent directory.
  -m {preprocessing,ins_resp,all}, --mode {preprocessing,ins_resp,all}
                        Select the mode.
```
### Preprocessing (merge, demean, detrend)      
```
python preprocessing.py --mode=preprocessing  --start_day=92 --end_day=122 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/
```     
### Removing instrument response     
```
python preprocessing.py --mode=ins_resp --start_day=92 --end_day=122 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/
```       
### All in one (preprocessing + removing instrument response)
```
python preprocessing.py --mode=all --parent_dir=/raid1/SM_data/archive/2024/TW --start_day=123 --end_day=124 --output_parent_dir=/home/patrick/Work/Month_report_repo/
```
## Visualization of monthly status of apparatus   
```
usage: visualization.py [-h] [-m {seis_status,psd,spec,all}] [-i MONTH_INDEX] [-s START_DAY] [-e END_DAY] [-p PARENT_DIR] [-o OUTPUT_PARENT_DIR]

options:
  -h, --help            show this help message and exit
  -m {seis_status,psd,spec,all}, --mode {seis_status,psd,spec,all}
                        Select the mode.
  -i MONTH_INDEX, --month_index MONTH_INDEX
                        a month just passed.
  -s START_DAY, --start_day START_DAY
                        Starting day of the year
  -e END_DAY, --end_day END_DAY
                        Starting day of the year
  -p PARENT_DIR, --parent_dir PARENT_DIR
                        Path to the parent directory of data.
  -o OUTPUT_PARENT_DIR, --output_parent_dir OUTPUT_PARENT_DIR
                        output_parent_dir
```     
### Checking the ability of data recording     
```
python visualization.py --mode=seis_status --month_index=4 --output_parent_dir=/home/patrick/Work/Month_report_repo/
```
### PSD
==Using the data **without removing instrument response** and merge them as monthly data.==       
```
python visualization.py --mode=psd --month_index=4 --start_day=92 --end_day=122 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/
```   
### Full month spectrogram       
==Plotting setting: ylim(0.1, 50), yscale('log')==
```
python visualization.py --mode=spec --month_index=4 --start_day=92 --end_day=122 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/
```     
## Event analysis    
```
usage: event_analysis.py [-h] [-m {wave_spec,wave_dist,all}] [-i MONTH_INDEX] [-d EVENT_DAY] [-t EVENT_TIME] [-lon EVENT_LON] [-lat EVENT_LAT]
                         [-p PARENT_DIR] [-o OUTPUT_PARENT_DIR] [-s STATION_LOCATION_FILE]

options:
  -h, --help            show this help message and exit
  -m {wave_spec,wave_dist,all}, --mode {wave_spec,wave_dist,all}
                        Select the mode.
  -i MONTH_INDEX, --month_index MONTH_INDEX
                        a month just passed.
  -d EVENT_DAY, --event_day EVENT_DAY
                        event day of the year.
  -t EVENT_TIME, --event_time EVENT_TIME
                        event time.
  -lon EVENT_LON, --event_lon EVENT_LON
                        Longitude of event.
  -lat EVENT_LAT, --event_lat EVENT_LAT
                        Latitude of event.
  -p PARENT_DIR, --parent_dir PARENT_DIR
                        Path to the parent directory of data.
  -o OUTPUT_PARENT_DIR, --output_parent_dir OUTPUT_PARENT_DIR
                        output parent directory.
  -s STATION_LOCATION_FILE, --station_location_file STATION_LOCATION_FILE
                        Path of station location.
```
### waveform with spectrogram
**Please check the num of station first, (2,4) grid was configured due to I have 8 station. It's fine if your station < 8,  changing the <span style="color: red;"> line66 </span> if your station > 8**       
**For a better visualization, some label and color bar ware ignored according to specific index, changing the <span style="color: red;"> line95, 101, 103 </span> for your own dataset**      
``` 
python event_analysis.py --mode=wave_spec --month_index=4 --event_day=85 --event_time=2024-03-25T10:13:37 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/
``` 
* Creating a event_list for GNU Parallel (change the num of j according to the availibilty of cores)    
```
# Recommending format of event_list (day_of_year UTC_event_time event_lon event_lat)      
85 2024-03-25T10:13:37 121.56 24.01
```   
```
parallel -j5 --colsep ' ' 'python event_analysis.py --mode=wave_spec --month_index=4 --event_day={1} --event_time={2} --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/' :::: event_list
``` 
### waveform arranged by distance   
==**Preparing the location of station is needed**==
``` 
python event_analysis.py --mode=wave_dist --month_index=4 --event_day=85 --event_time=2024-03-25T10:13:37 --event_lon=121.56  --event_lat=24.01 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/ --station_location_file=/home/patrick/Work/Month_report_repo/station.csv
``` 
* Creating a event_list for GNU Parallel (change the num of j according to the availibilty of cores) 
```
parallel -j5 --colsep ' ' 'python event_analysis.py --mode=wave_dist --month_index=4 --event_day={1} --event_time={2} --event_lon={3}  --event_lat={4} --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/ --station_location_file=/home/patrick/Work/Month_report_repo/station.csv' :::: event_list
```   
### generating these two figure above at the same time    
``` 
python event_analysis.py --mode=all --month_index=4 --event_day=85 --event_time=2024-03-25T10:13:37 --event_lon=121.56  --event_lat=24.01 --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/ --station_location_file=/home/patrick/Work/Month_report_repo/station.csv
``` 
* Creating a event_list for GNU Parallel (change the num of j according to the availibilty of cores)    
```
parallel -j5 --colsep ' ' 'python event_analysis.py --mode=all --month_index=4 --event_day={1} --event_time={2} --event_lon={3}  --event_lat={4} --parent_dir=/raid1/SM_data/archive/2024/TW --output_parent_dir=/home/patrick/Work/Month_report_repo/ --station_location_file=/home/patrick/Work/Month_report_repo/station.csv' :::: event_list
```