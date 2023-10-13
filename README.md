# For monthly report
## File intro
> These 2 files are necessary to do before any plot.    
* preprocssing.py    
Implementing the merge, demean & detrend.  
* instrument_responese.py    
Removing the instrument response.     
## what we aim for
### Seismometer status        
* seis_status.py    
### Monthly PSD
* psd.py    
Using the data **without removing instrument response** and merge them as monthly data.    
### Full month spectrogram       
We first need to draw the apparatus status to compare the validation of spectrogram.    
* Monthly_spectrogram.py    
My plot will exist some weird line along the xticks, but did not affect the visualization.     
Plotting setting: ylim(0.1, 50), yscale('log')
### Map
* map.py   
This is held in abeyance till I need to plot map.
### singlechannel with spectrogram
* bandpass_spectrogram.py    
Pass a bandpass in (0.1, 10) and draw a singlechannel with spectrogram.
### stacked waveform plot for event analysis   
1. acquiring the station data    
* finding.py    
This can extraxt the Latitude and Longitude in the PZs file, and save it as CSV simultaneously.    
* station.csv   
Information of station.    
2. Calculate the dist and plot it!    
* evt_analysis.py    
As title said.     
---
### other files    
* quicknote.ipynb   
Some quicktest and thoughts    
