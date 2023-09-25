# For monthly report
## File intro
> These 2 files are necessary to do before any plot.    
* preprocssing.py    
Implementing the merge, demean, detrend, and taper.    
* instrument_responese.py    
Removing the instrument response     
## what we aim for
### Seismometer status
### Monthly PSD
* psd.py    
Using the data without removing instrument response and merge them as monthly data.    
seems ok   
### Full month spectrogram   
we need to draw the apparatus status to compare the validation of spectrogram.
### Map
### singlechannel with spectrogram
* <span style="color:green">bandpass_spectrogram.py</span>    
pass a bandpass(0.1, 10) and draw a singlechannel with spectrogram.
### stacked waveform plot for event analysis 