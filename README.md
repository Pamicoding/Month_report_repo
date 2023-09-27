# For monthly report
## File intro
> These 2 files are necessary to do before any plot.    
* preprocssing.py    
Implementing the merge, demean, detrend, and taper.    
* instrument_responese.py    
Removing the instrument response     
> this one is for monthly data.(ideal, now we encounter the masked array problem to be resolved)    
* merge_month.py    
Generating the monthly data by merging daily stream. In addition, the file also be written into a specific folder for afterward utilizing.    
merge the original
## what we aim for
### Seismometer status        
* seis_status.py    
### Monthly PSD
**using the merge_month data**    
* psd.py    
Using the data **without removing instrument response** and merge them as monthly data.    
seems ok   
### Full month spectrogram       
we need to draw the apparatus status to compare the validation of spectrogram.    
* Monthly_spectrogram.py    
we still got problem when add the ax.set_yscale
### Map
### singlechannel with spectrogram
* <span style="color:green">bandpass_spectrogram.py</span>    
pass a bandpass(0.1, 10) and draw a singlechannel with spectrogram.
### stacked waveform plot for event analysis   
1. acquiring the station data    
* finding.py    
This can extraxt the Latitude and Longitude in the PZs file, and save it as CSV simultaneously.    
* station.csv   
information of station.    
2. Calculate the dist and plot it!    
* evt_analysis.py    
title     
---
### other files    
* quicknote.ipynb   
some quicktest and thoughts    
