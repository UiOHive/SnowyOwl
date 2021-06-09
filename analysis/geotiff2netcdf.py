# Script to convert geotiff to netcdf

import xarray as xr
import glob
import pandas as pd
import argparse


def raster_to_ds_daily(pwd, compression=True, filename_format='%Y%m%d.nc'):
    """
    function to store geotif into daily netcdf

    :param pwd: path to folder with geotif, str
    :param compression: copmress netcdf or not, defaults to True,  bool, optional
    :param filename_format: output file name format following datetime system, defaults to '%Y%m%d.nc',  str, optional

    TODO: 
        - option to delete geotif once they are stored as netcdf
    """    

    # list filename
    flist = glob.glob(pwd + '/*.tif')
    flist.sort()

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

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--path2tif', '-pt', help='Path to geotif file', default='../data/202104')
    parser.add_argument('--fname_format', '-of', help='output filename format using datetime strftime syntax', default='%Y%m%d.nc')
    parser.add_argument('--compression', '-c', help='compression flag', default='true')
    args = parser.parse_args()

    raster_to_ds_daily(args.path2tif, compression=args.compression, filename_format=args.fname_format)

    