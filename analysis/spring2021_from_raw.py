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
import pdal

import configparser, logging
from app.process_pcl import *

