'''
# Script to convert from zipfile to netcdf

Loop by day

1. unzip
2. https://gdal.org/programs/gdal_fillnodata.html
3. https://gdal.org/programs/gdal_merge.html
4. 

'''
from zipfile import ZipFile
import glob
import os
import pandas as pd
import xarray as xr

#%%
src_dir = './'
dst_dir = './unzip/'
compression = True
create_netcdf = False
filename_format = '%Y%m%d.nc'



flist = glob.glob(src_dir + '*.zip')
flist.sort()

# CHECK that original .ZIP files and destination folder exist
if len(flist) == 0:
    raise Exception("Sorry, no file in {} directory".format(src_dir)) 
if not os.path.exists(dst_dir):
    raise Exception("Sorry, no directory {}".format(dst_dir)) 


meta = pd.DataFrame({'fname':flist})
#extract timestamp from filename
meta['tst'] = pd.to_datetime(meta.fname.apply(lambda x: x.split('/')[-1][:-4]))


#%%

for mydate in meta.tst.dt.date.unique():
    for i, row in meta.loc[meta.tst.dt.date == mydate].iterrows:
        with ZipFile(row.fname, 'r') as zipObj:
            # Extract all the contents of zip file in current directory
            zipObj.extractall(dst_dir)

    rast_list = glob.glob(dst_dir + '*.tif')

    for f_rast in rast_list:

        f_fill = f_rast[:-4] + '_fill.tif'
        f_rast_out = f_rast[:-4] + '_'
        cmd_fillnodata = 'gdal_fillnodata.py -q -md 10 -b min {} {}'.format(f_rast, f_fill)
        print(cmd_fillnodata)
        os.system(cmd_fillnodata)

        cmd_merge = 'gdal_merge.py -o {} {} {}'.format(f_rast_out, f_rast, f_fill)
        print(cmd_merge)
        os.system(cmd_merge)

        # remove f_fill, f_rast
        
        os.remove(f_rast)
        os.remove(f_fill)

    #========
    # 
    if create_netcdf:

        # create time variable
        time_var = xr.Variable('time', meta.tst.loc[meta.tst.dt.date==mydate])
        # open raster files in datarray
        geotiffs_da = xr.concat([xr.open_rasterio(i) for i in meta.fname.loc[meta.tst.dt.date==mydate]], dim=time_var)
        # drop all NaN values
        geotiffs_da = geotiffs_da.where(geotiffs_da!=-9999, drop=True)
        # rename variables with raster band names
        var_name = dict(zip(geotiffs_da.band.values, geotiffs_da.descriptions))
        geotiffs_ds = geotiffs_da.to_dataset('band')
        geotiffs_ds = geotiffs_ds.rename(var_name)

        # save to netcdf file
        fname_nc = dst_dir + meta.tst.loc[meta.tst.dt.date==mydate].iloc[0].strftime(filename_format)
        if compression:
            encode = {"min_fill":{"compression": "gzip", "compression_opts": 9},
                        "min":{"compression": "gzip", "compression_opts": 9}, 
                        "max":{"compression": "gzip", "compression_opts": 9},
                        "mean":{"compression": "gzip", "compression_opts": 9},
                        "idw":{"compression": "gzip", "compression_opts": 9},
                        "count":{"compression": "gzip", "compression_opts": 9},
                        "stdev":{"compression": "gzip", "compression_opts": 9}}
            geotiffs_ds.to_netcdf(fname_nc,  encoding=encode, engine='h5netcdf')
        else:
            geotiffs_ds.to_netcdf(fname_nc)
            print('File saved: ', fname_nc)
    
        # Remove all remaining rasters in the dst folder
        rast_list = glob.glob(dst_dir + '*.tif')
        for f_rast in rast_list:
            os.remove(f_rast)