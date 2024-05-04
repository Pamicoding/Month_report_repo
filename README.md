# Monthly report
## Data preparation    
* For preprocessing (merge, demean, detrend)      
```
python preprocessing.py --parent_dir=/raid1/SM_data/archive/2024/TW --start_day=92 --end_day=122 --logging_dir=/home/patrick/Work/Month_report_repo/log/ --mode=preprocessing
```     
* For removing instrument response     
```
python preprocessing.py --parent_dir=/raid1/SM_data/archive/2024/TW --start_day=92 --end_day=122 --logging_dir=/home/patrick/Work/Month_report_repo/log/ --mode=ins_resp
```       
## plotting
### Seismometer status        
* seis_status.py    
### PSD
* psd.py    
Using the data **without removing instrument response** and merge them as monthly data.    
### Full month spectrogram       
> We first need to draw the status of apparutus to compare the validation of spectrogram.    
* Monthly_spectrogram.py    
<font color="red">*Fugure will exist some weird line along the xticks, but did not affect the visualization.*</font>      

Plotting setting: ylim(0.1, 50), yscale('log')
### singlechannel with spectrogram
* bandpass_spectrogram.py    
Pass a bandpass in (0.1, 10) and draw a singlechannel with spectrogram.
### stacked waveform plot for event analysis   
1. acquiring the station data    
* finding.py    
This can extraxt the Latitude and Longitude in the PZs file, and save it as CSV.    
* station.csv   
Information of station.    
2. Calculate the dist and plot it!    
* evt_analysis.py    
As title said.     
