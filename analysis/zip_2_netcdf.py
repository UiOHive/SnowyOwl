'''
# Script to convert from zipfile to netcdf
S. Filhol, June 2021

Loop by day


TODO:
- check logging

'''
from zipfile import ZipFile
import glob, logging
import os
import pandas as pd
import xarray as xr
import gdal
from gdalconst import *

# %%

# Parameter setup
src_dir = '/mn/vann/climaland/LIVOXFinse/'
tmp_dir = '/mn/vann/climaland/dems/unzip/'
dst_dir = '/mn/vann/climaland/dems/netcdf/'
compression = True
create_netcdf = True
fname_fmt_netcdf = '%Y%m%d.nc'

logging.basicConfig(filename='./Convert_tif2nc.log', level='DEBUG', format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
flist = glob.glob(src_dir + '*.zip')
flist.sort()

# CHECK that original .ZIP files and destination folder exist
if len(flist) == 0:
    logging.error("Sorry, no file in {} directory".format(src_dir))
    raise Exception("Sorry, no file in {} directory".format(src_dir))
if not os.path.exists(tmp_dir):
    logging.error("Sorry, no file in {} directory".format(tmp_dir))
    raise Exception("Sorry, no directory {}".format(tmp_dir))
if not os.path.exists(dst_dir):
    logging.error("Sorry, no file in {} directory".format(dst_dir))
    raise Exception("Sorry, no directory {}".format(dst_dir))


meta = pd.DataFrame({'fname': flist})
# extract timestamp from filename
meta['tst'] = pd.to_datetime(meta.fname.apply(lambda x: x.split('/')[-1][:-4]), format='%Y.%m.%dT%H-%M-%S')


def fillnodata(fname, band=1, maxSearchDist=5, smoothingIterations=0):
    ET = gdal.Open(fname, GA_Update)
    ETband = ET.GetRasterBand(band)
    result = gdal.FillNodata(targetBand=ETband, maskBand=None,
                             maxSearchDist=maxSearchDist, smoothingIterations=smoothingIterations)
    ETband = None
    ET = None

# %%

for mydate in meta.tst.dt.date.unique():
    try:
        print('Converting {}'.format(mydate.strftime('%Y-%m-%d')))
        logging.info('Converting {}'.format(mydate.strftime('%Y-%m-%d')))
        for i, row in meta.loc[meta.tst.dt.date == mydate].iterrows():
            with ZipFile(row.fname, 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                zipObj.extractall(tmp_dir)
        logging.info('File unzipped')

        if os.path.exists(tmp_dir + 'home/'):
            rast_list = glob.glob(tmp_dir+'/home/snowyowl/data/OUTPUT/*.tif')
        else:
            rast_list = glob.glob(tmp_dir + '*.tif')
        rast_list.sort()

        df_tmp = meta.loc[meta.tst.dt.date == mydate].copy()
        df_tmp['rast_name'] = rast_list

        for f_rast in rast_list:
            fillnodata(f_rast)
        # ========
        #
        if create_netcdf:
            try:

                # create time variable
                time_var = xr.Variable('time', df_tmp.tst)
                # open raster files in datarray
                geotiffs_da = xr.concat([xr.open_rasterio(i) for i in df_tmp.rast_name], dim=time_var)
                # drop all NaN values
                geotiffs_da = geotiffs_da.where(geotiffs_da != -9999, drop=True)
                # rename variables with raster band names
                var_name = dict(zip(geotiffs_da.band.values, geotiffs_da.descriptions))
                geotiffs_ds = geotiffs_da.to_dataset('band')
                geotiffs_ds = geotiffs_ds.rename(var_name)

                # save to netcdf file
                fname_nc = dst_dir + df_tmp.tst.loc[df_tmp.tst.dt.date == mydate].iloc[0].strftime(fname_fmt_netcdf)
                if compression:
                    encode = {"min": {"compression": "gzip", "compression_opts": 9},
                              "max": {"compression": "gzip", "compression_opts": 9},
                              "mean": {"compression": "gzip", "compression_opts": 9},
                              "idw": {"compression": "gzip", "compression_opts": 9},
                              "count": {"compression": "gzip", "compression_opts": 9},
                              "stdev": {"compression": "gzip", "compression_opts": 9}}
                    geotiffs_ds.to_netcdf(fname_nc, encoding=encode, engine='h5netcdf')
                    print('--- Compressed netcdf saved: {}'.format(fname_nc))
                    logging.debug('Compressed netcdf saved: {}'.format(fname_nc))
                else:
                    geotiffs_ds.to_netcdf(fname_nc)
                    print('File saved: {}'.format(fname_nc))
                    logging.debug('File saved: {}'.format(fname_nc))
            except:
                logging.error('Cannot compile into netcdf date: {}'.format(mydate.strftime('%Y-%m-%d')))
                print(' --- Cannot compile into netcdf date: {}'.format(mydate.strftime('%Y-%m-%d')))

            # Remove all remaining rasters in the tmp folder
        for f_rast in rast_list:
            os.remove(f_rast)
        print(' --- Raster files removed')
    except:
        logging.error('Could not create netcdf for day {}'.format(mydate.strftime('%Y-%m-%d')))
