#%%
import os
import glob
import pandas as pd
# dir
parent_dir = '/raid1/SM_data/TWSM2/'
list_all = os.listdir(parent_dir)
station_list = []
for list in list_all:
    if 'SM' in list:
        station_list.append(list)

latitude = None
longitude = None
Lat = []
Lon = []
Station =[]
for sta in station_list:
    path_to_file = os.path.join(parent_dir, sta)
    pzs = glob.glob(os.path.join(path_to_file, '*EPZ*'))
    Station.append(sta)
    with open(pzs[0], 'r') as file:
        for line in file:
            if line.startswith("* LATITUDE"):
                latitude = float(line.split(":")[1].strip())
                Lat.append(latitude)
            elif line.startswith("* LONGITUDE"):
                longitude = float(line.split(":")[1].strip())
                Lon.append(longitude)
            # If both latitude and longitude have been found, you can break out of the loop

data = {'Station':Station,'Lon':Lon,'Lat':Lat}
df = pd.DataFrame(data)
df.to_csv('station.csv', index=False)
# %%
