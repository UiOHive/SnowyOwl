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
from wsn_client import query

import xarray as xr
import glob
import pandas as pd
import openpylivox as opl
import pdal, json, os

import configparser, logging
from appV2 import process_pcl as pp



# 1. Convert all point clouds to netcdf4 via geotiff

archive_dir = '/media/arcticsnow/My Book/SnowyOwl_Bin_Archive/'
proj_dir = '/media/arcticsnow/My Book/SO_spring_2021_processing/'
flist = glob.glob(archive_dir)
flist.sort()

# create dataframe of file metadata
meta = pd.DataFrame({'fname':flist})
#extract timestamp from filename
meta['tst'] = pd.to_datetime(meta.fname.apply(lambda x: x.split('/')[-1][:-4]))

# Create on netcdf file per day
for date in meta.tst.dt.day.unique():
    # create time variable
    time_var = xr.Variable('time', meta.tst.loc[meta.tst.dt.day==date])

    # convert by daily batches. Use functions from process_pcl!!!!
    pp.convert_bin_to_las()
    pp.rotate_point_clouds()
    pp.extract_dem()





