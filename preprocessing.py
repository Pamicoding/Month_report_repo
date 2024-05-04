from obspy import read
import os
import glob
import logging
import argparse
from argparse import RawDescriptionHelpFormatter
import multiprocessing
def format_number(number):
    number_str = str(number)
    num_digits = len(number_str)
    num_zeros = 3 - num_digits
    # Add the leading zeros if the num_zeros != 0.
    formatted_number = '0' * num_zeros + number_str
    return formatted_number # transfer the 1 to 001

def parse_arguments():
    parser = argparse.ArgumentParser(description='Preprocessing seismic data. \n\nExample usage:\n'
                                     'For preprocessing (merge, demean, detrend):\n'
                                     'python preprocessing.py --parent_dir=/raid1/SM_data/archive/2024/TW --start_day=92 --end_day=122 --logging_dir=/home/patrick/Work/Month_report_repo/log/ --mode=preprocessing\n\n'
                                     'For removing instrument response:\n'
                                     'python preprocessing.py --parent_dir=/raid1/SM_data/archive/2024/TW --start_day=92 --end_day=122 --logging_dir=/home/patrick/Work/Month_report_repo/log/ --mode=ins_resp\n\n',
                                     formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-p', '--parent_dir', type=str, default='/raid1/SM_data/archive/2024/TW', help='Path to the parent directory of data.')
    parser.add_argument('-s', '--start_day', type=int, default=None, help='Starting day of the year')
    parser.add_argument('-e', '--end_day', type=int, default=None, help='Starting day of the year')
    parser.add_argument('-l','--logging_dir', type=str, default='/home/patrick/Work/Month_report_repo/log/',help='Path of logging directory.')
    parser.add_argument('-m','--mode', type=str, choices=['preprocessing','ins_resp'], default=None,help='Select the mode.')
    args = parser.parse_args()
    return args

# preprocessing
def preprocessing(station):
    args = parse_arguments()
    parent_directory = args.parent_dir
    output_parent_dir = os.path.join(parent_directory,'preprocessing')
    os.makedirs(output_parent_dir, exist_ok=True) # create
    days = range(args.start_day, args.end_day)
    logging.basicConfig(filename=os.path.join(args.logging_dir,f'preprocessing_{station}.log'), level=logging.INFO, filemode='w')
    station_path = os.path.join(parent_directory, station) # {parent_dir}/SM02
    output_station_path = os.path.join(output_parent_dir, station) # {parent_dir}/preprocessing/SM02
    os.makedirs(output_station_path, exist_ok=True)
    logging.info(f"we are now in {station}")

    for azi in azi_list: 
        try:
            logging.info(f"in the {azi}")
            sub_subdirectory_path = os.path.join(station_path, azi) # {parent_dir}/SM02/EPZ.D
            output_directory = os.path.join(output_station_path, azi) # {parent_dir}/preprocessing/SM02/EPZ.D
            os.makedirs(output_directory, exist_ok=True)
        except Exception as e:
            logging.info(f"{azi} not found in {station}")
        for day in days:
            try:
                data_file = glob.glob(os.path.join(sub_subdirectory_path, f'*{format_number(day)}*'))
                logging.info(f"on the day of year:{format_number(day)}")
                st = read(data_file[0])
                # Merge traces within the Stream if there are more than one trace.
                if len(st) > 1:
                    st.merge(fill_value='interpolate') # Using interpolate because we don't want the masked array error.
                # Preprocess the Stream.
                st.detrend('demean')
                st.detrend('linear')
                #st.taper(type='hann', max_percentage=0.05) # optional
                logging.info(f"{os.path.basename(data_file[0])} detrend are done")
                output_file = os.path.join(output_directory, os.path.basename(data_file[0]))
                st.write(output_file, format='SAC')
                logging.info(f"{os.path.basename(data_file[0])} already saved!")
            except Exception as e:
                logging.info(f"{e} on {format_number(day)} in {station}_{azi}")
    logging.info(f"Preprocessing and saving {station} completed for all directories.")

# removing instrument response
def ins_resp(station):
    args = parse_arguments()
    logging.basicConfig(filename=os.path.join(args.logging_dir,f'response_{station}.log'), level=logging.INFO, filemode='w')
    input_dir = os.path.join(args.parent_dir,'preprocessing')
    output_dir = os.path.join(args.parent_dir,'remove_resp')
    os.makedirs(output_dir, exist_ok=True)
    days = range(args.start_day, args.end_day)
    # instrument response settings
    pre_filt = prefilt
    logging.info(f"Processing station: {station}") 
    layer_1 = os.path.join(output_dir, station)
    os.makedirs(layer_1, exist_ok=True) # {parent_dir}/remove_resp/SM01
    for azi in azimuth_dir:
        logging.info(f"Processing azimuth: {azi}")  # Log azimuth processing        
        sac_data_dir = os.path.join(input_dir, station, azi) # {parent_dir}/preprocessing/SM01/EPZ.D
        # different pzs file to remove the instrument response
        if azi[:2] == 'EP':
            # EP
            paz_sts2 = paz_EP         
        else:
            # HL
            paz_sts2 = paz_HL
        for day in days:
            day_f = format_number(day)
            day_path = f"{year}.{day_f}"
            search_pattern = os.path.join(sac_data_dir, f'*{day_path}*')
            try: 
                sac_data = glob.glob(search_pattern) 
            except Exception as e:
                logging.error(f"Error while searching for files in station {station}, azimuth {azi}: {str(e)}")
                continue  # Continue with the next azimuth
            for data in sac_data:
                try:
                    st = read(data) 
                    st.simulate(paz_remove=paz_sts2, pre_filt=pre_filt) # we add the pre_filt to apply a bandpass
                    # Save the preprocessed data in the output directory
                    processed_file = os.path.join(layer_1, os.path.basename(data))
                    st.write(processed_file, format='SAC')
                    logging.info(f"Processed {data} and saved as {processed_file}")
                except Exception as e:
                    logging.error(f"Error processing {data}: {str(e)}")
    logging.info('done')



if __name__ == '__main__':
    args = parse_arguments()
    station_list = ['SM01','SM02', 'SM06', 'SM09', 'SM19', 'SM37', 'SM39', 'SM40'] # change it when it's first time.
    if args.mode == 'preprocessing':
        # variable <- customerize it
        azi_list = ['EPE.D','EPN.D','EPZ.D','HLE.D','HLN.D','HLZ.D'] # change it when it's first time.
        # main+multiprocessing
        pool = multiprocessing.Pool(processes=8)
        pool.map(preprocessing, station_list)

        pool.close()
        pool.join()
    elif args.mode == 'ins_resp':
        # variable <- customerize it
        year = 2024
        azimuth_dir = ['EPZ.D','HLZ.D']
        prefilt = (0.05, 0.1, 50, 60)
        paz_EP = {'poles': [-19.781+20.2027j, -19.781-20.2027j],
                'zeros': [0, 0],
                'gain': 1.0*27.7,
                'sensitivity': 546976.0}
        paz_HL = {'poles': [-977+328j, -977-328j,
                            -1486+2512j, -1486-2512j,
                            -5736+4946j, -5736-4946j],
                'zeros': [-515+0j],
                'gain': 1.007725E+18*1.02,
                'sensitivity': 408000.0}
        # main
        pool = multiprocessing.Pool(processes=8)
        pool.map(ins_resp, station_list)

        pool.close()
        pool.join()