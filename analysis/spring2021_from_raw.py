'''
Script to process raw .bin files from the livo lidar collected from March 2021 to June 2021
S. Filhol 2021

-------
Part 1:  Find out when to convert bin file into DEMs

1. get wind, temperature, flux, precip and snow depth from flux station
2. identify events: precip, wind, transport.
3. create list of timestamp to convert bin to netcdf. High temporal resolution during events, low temporal resolution in low activity

-------
Part 2

1. write code to load files metadata to sort which file to process and post process
2. 

'''
import xarray as xr
import glob
import pandas as pd
import openpylivox as opl
import pdal, json, os
import getpass
import configparser, logging, sys
sys.path.append('/home/' + getpass.getuser() + '/github/SnowyOwl/')
from appV2 import process_pcl as pp
import shutil
import process as pp

#------------------------------------------------------
# Parameter
sampling_interval=60 * 12 #minute
GSD = 0.02
dir_bin = '/media/' + getpass.getuser() + '/My Book/SO_spring_2021_processing/bin/'
dir_netcdf = '/media/' + getpass.getuser() + '/My Book/SO_spring_2021_processing/netcdf/'
dir_daily = '/media/' + getpass.getuser() + '/My Book/SO_spring_2021_processing/daily/'

#------------------------------------------------------
# List files

flist = glob.glob(dir_bin + '*.bin')
flist.sort()

meta = pd.DataFrame({'fname_archive':flist})

# create dataframe of file metadata
meta = pd.DataFrame({'fname_archive':flist})
#extract timestamp from filename
meta['tst'] = pd.to_datetime(meta.fname_archive.apply(lambda x: x.split('/')[-1][:-4]), format="%Y.%m.%dT%H-%M-%S")
meta['daily']=(meta.tst - pd.to_datetime('2021-03-11 00:00:00')).dt.days

#------------------------------------------------------
# Loop through each day available

for day in meta.daily.unique():
    print('......')
    print('Processing Day ', day)
    daily = meta.loc[meta.daily==day]
    for file in daily.fname_archive:
        # Copy files that fit the sampling period to the folder 
        try:
            tst_data = pd.to_datetime(file.split('/')[-1][:19],format="%Y.%m.%dT%H-%M-%S")
            if (tst_data.second + 60*tst_data.minute + 3600*tst_data.hour) % sampling_interval == 0:
                shutil.copy(file, dir_daily)
        except IOerror:
            print('ERROR: cannot move ', file)
    print('-- File moved')
    pp.convert_bin_to_las(path_to_data=dir_daily)
    print('-- Bin converted to las')
    pp.tmp_rotate_point_clouds(z_range='[-20:20]', 
                               crop_corners='([-20, 10], [-5, 5])', 
                               path_to_data=dir_daily, 
                               delete_las=True)
    print('-- Rotated pcl')
    pp.extract_dem(GSD=GSD,
                origin_x=-16.2,
                origin_y=-4,
                height=7.8,
                width=22.3,
                method='pdal',
                path_to_data=dir_daily,
                delete_las=True,
                tif_to_zip=False)
    print('-- Tif extracted')
    pp.raster_to_ds_daily(dir_daily, dir_netcdf)
    print('-- daily Netcdf compiled')
