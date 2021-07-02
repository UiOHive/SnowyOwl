# Script to convert geotiff to netcdf

import glob, argparse, datetime
import pandas as pd
import xarray as xr
from osgeo import gdal
from gdalconst import *

def fillnodata(fname, band=1, maxSearchDist=5, smoothingIterations=0):
    ET = gdal.Open(fname, GA_Update)
    ETband = ET.GetRasterBand(band)
    result = gdal.FillNodata(targetBand=ETband, maskBand=None,
                             maxSearchDist=maxSearchDist, smoothingIterations=smoothingIterations)
    ETband = None
    ET = None
    

def raster_to_ds_daily(pwd, compression=True, filename_format='%Y%m%d.nc', only_yesterday=True):
    """
    function to store geotif into daily netcdf

    :param pwd: path to folder with geotif, str
    :param compression: copmress netcdf or not, defaults to True,  bool, optional
    :param filename_format: output file name format following datetime system, defaults to '%Y%m%d.nc',  str, optional
    :param only_yesterday: only the files created the day before the script is run (in UTC day) are converted to netcdf. Script is meant to be run about 2h after UTC=00:00, so all files from today-1 have been processed to tif already
 

    TODO: 
        - option to delete geotif once they are stored as netcdf
    """    

    # list filename
    if only_yesterday:
        date_yesterday=(datetime.utcnow()-datetime.timedelta(days=1)).strftime("%Y.%m.%d")    	
        flist = glob.glob(pwd + '/' + date_yesterday +'*.tif')    
    else:
        flist = glob.glob(pwd + '/*.tif')
    flist.sort()

    for f_rast in flist:
        fillnodata(f_rast)
        
    # create dataframe of file metadata
    meta = pd.DataFrame({'fname':flist})
    #extract timestamp from filename
    meta['tst'] = pd.to_datetime(meta.fname.apply(lambda x: x.split('/')[-1][:-4]))

    # Create on netcdf file per day
    for date in meta.tst.dt.day.unique():
        # create time variable
        time_var = xr.Variable('time', meta.tst.loc[meta.tst.dt.day==date])
        # open raster files in datarray
        geotiffs_da = xr.concat([xr.open_rasterio(i) for i in meta.fname.loc[meta.tst.dt.day==date]], dim=time_var)
        # drop all NaN values
        geotiffs_da = geotiffs_da.where(geotiffs_da!=-9999, drop=True)
        # rename variables with raster band names
        var_name = dict(zip(geotiffs_da.band.values, geotiffs_da.descriptions))
        geotiffs_ds = geotiffs_da.to_dataset('band')
        geotiffs_ds = geotiffs_ds.rename(var_name)

        # save to netcdf file
        fname_nc = pwd + '/' + meta.tst.loc[meta.tst.dt.day==date].iloc[0].strftime(filename_format)
        if compression:
            encode = {"min":{"compression": "gzip", "compression_opts": 9}, 
                        "max":{"compression": "gzip", "compression_opts": 9},
                        "mean":{"compression": "gzip", "compression_opts": 9},
                        "idw":{"compression": "gzip", "compression_opts": 9},
                        "count":{"compression": "gzip", "compression_opts": 9},
                        "stdev":{"compression": "gzip", "compression_opts": 9}}
            geotiffs_ds.to_netcdf(fname_nc,  encoding=encode, engine='h5netcdf')
        else:
            geotiffs_ds.to_netcdf(fname_nc)
        print('File saved: ', fname_nc)

        # clear memory cache before next loop
        geotiffs_da = None
        geotiffs_ds = None

if __name__ == "__main__":

    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-cf', help='Path to config file', default='/home/config.ini')
    args = parser.parse_args()
    
    raster_to_ds_daily(config['processing'].get('path_to_data'),
        compression=config['processing'].getboolean('netcdf_compression'),
        filename_format=config['processing'].get('netcdf_file_name_format'),
        only_yesterday=config['processing'].getboolean('netcdf_for_yesterday_only'))

    
