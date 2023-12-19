import subprocess

subprocess.run(["python", "seis_status.py"])
subprocess.run(["python", "Monthly_spectrogram.py"])
subprocess.run(["python", "psd.py"])
subprocess.run(["python", "bandpass_spectrogram.py"])
# Add more lines for additional scripts if needed
