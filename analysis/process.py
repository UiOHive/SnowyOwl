"""
Script to process Livox point clouds
S. Filhol and L. Girod
March 2021

TODO:
- add pandas method to derive DEM that we can grab percentile and other stats from the cloud and save as netcdf with xarray
"""
import numpy as np
import configparser, logging
import openpylivox as opl
import glob, os
import pdal, json
import pandas as pd
import datetime
from osgeo import gdal
import xarray as xr


def rotation_matrix_pdal(extrinsic=[0,0,0,0,0,0]):
    """
    Function to compute rotation matrix for PDAL
    :param extrinsic: [X,Y,Z,omega,phi,kappa] of the sensor
    :return: rotation matrix in string format ready for PDAL
    """
    ext_rad = np.radians(extrinsic)
    Mom = np.array([[1, 0, 0], [0, np.cos(ext_rad[3]), np.sin(ext_rad[3])],
                     [0, -np.sin(ext_rad[3]), np.cos(ext_rad[3])]])
    Mph = np.array([[np.cos(ext_rad[4]), 0, -np.sin(ext_rad[4])], [0, 1, 0],
                     [np.sin(ext_rad[4]), 0, np.cos(ext_rad[4])]])
    Mkp = np.array([[np.cos(ext_rad[5]), np.sin(ext_rad[5]), 0],
                     [-np.sin(ext_rad[5]), np.cos(ext_rad[5]), 0], [0, 0, 1]])
    rotMat = (Mkp * Mph * Mom).T.flatten()
    affineMatrix = np.concatenate((rotMat[0:3], [extrinsic[0]], rotMat[3:6], [extrinsic[1]], rotMat[6:9], [extrinsic[2]], [0], [0], [0], [1]))
    affineMatrixString = ' '.join([str(elem) for elem in affineMatrix])
    return affineMatrixString

def convert_bin_to_las(path_to_data='/home/data/'):
    file_list = glob.glob(path_to_data + '*.bin')
    for file in file_list:
        opl.convertBin2LAS(file, deleteBin=False)
        os.remove(file)
        os.rename(file+'.las', file[:-4]+'.las')
        print(file, ' removed and las renamed.')

def rotate_point_clouds(extrinsic=[0,0,0,0,0,0], z_range='[-20:20]', crop_corners='([-20, 10], [-5, 5])', path_to_data='/home/data/', delete_las=True):
    """
    Function to rotate point clouds and crop potential outliers
    :param extrinsic: [X,Y,Z,omega,phi,kappa] of the sensor
    :param z_range: [Zmin, Zmax] crop in Z of the point clouds.
    :param crop_corners: [Xmin, Xmax, Ymin, Ymax] crop in X and Y of the point clouds to exclude
    :param path_to_data:
    :return:
    """
    rot_mat = rotation_matrix_pdal(extrinsic)
    file_list = glob.glob(path_to_data + '*.las')

    for file in file_list:
        try:
            pip_filter_json = json.dumps(
                {
                    "pipeline":
                        [
                            file,
                            {
                                "type":"filters.transformation",
                                "matrix": '-0.34448594  0.93707407  0.05675957  2.51637959 -0.00583132  0.05832322 -0.9982807   0.35913649 -0.93877339 -0.34422466 -0.01462715  9.57211494 0. 0. 0. 1.'
                             },
                            {
                                "type": "filters.range",
                                "limits": "Z" + z_range
                            },
                            {
                                    "type": "filters.crop",
                                    "bounds": crop_corners
                                },
                            {
                                "type":"writers.las",
                                "filename": path_to_data + file.split('/')[-1]
                            }
                        ]
                })
            pipeline = pdal.Pipeline(pip_filter_json)
            pipeline.execute()
            if delete_las:
                os.remove(file)
        except Exception:
            print('Pdal pipeline failed to extract subset')

def tmp_rotate_point_clouds(z_range='[-20:20]', crop_corners='([-20, 10], [-5, 5])', path_to_data='/home/data/', delete_las=True):
    """
    Function to rotate point clouds and crop potential outliers
    :param z_range: [Zmin, Zmax] crop in Z of the point clouds.
    :param crop_corners: [Xmin, Xmax, Ymin, Ymax] crop in X and Y of the point clouds to exclude
    :param path_to_data:
    :return:
    """

    file_list = glob.glob(path_to_data + '*.las')

    for file in file_list:
        try:
            pip_filter_json = json.dumps(
                {
                    "pipeline":
                        [
                            file,
                            {
                                "type":"filters.transformation",
                                "matrix": '-0.34448594  0.93707407  0.05675957  2.51637959 -0.00583132  0.05832322 -0.9982807   0.35913649 -0.93877339 -0.34422466 -0.01462715  9.57211494 0. 0. 0. 1.'
                             },
                            {
                                "type": "filters.range",
                                "limits": "Z" + z_range
                            },
                            {
                                    "type": "filters.crop",
                                    "bounds": crop_corners
                                },
                            {
                                "type":"writers.las",
                                "filename": path_to_data + file.split('/')[-1][:-4] + "_rot.las"
                            }
                        ]
                })
            pipeline = pdal.Pipeline(pip_filter_json)
            pipeline.execute()
            if delete_las:
                os.remove(file)
        except Exception:
            print('Pdal pipeline failed to extract subset')
        
def extract_pcl_subset(corners='([-0.5,0.5],[-0.5,0.5])', path_to_data='/home/data/'):
    """
    Function to extract a point cloud vertical column subset defined by the corners coordinates
    :param corners: x_min,x_max,y_min,y_max of the cropped area to keep all point for
    :param path_to_data:
    :return:
    """
    
    file_list = glob.glob(path_to_data + '*.las')
    for file in file_list:
        try:
            pip_filter_json = json.dumps(
                {
                    "pipeline":
                        [
                            file,
                            {
                                "type": "filters.crop",
                                "bounds": corners
                            },
                            {
                                "type":"writers.las",
                                "filename":path_to_data +   file.split('/')[-1][:-4] + "cropped.las"
                            }
                        ]
                }
            )
            pipeline = pdal.Pipeline(pip_filter_json)
            pipeline.execute()
        except Exception:
            print('Pdal pipeline failed to extract subset')

def las_2_laz(path_to_data='/home/data/', delete_las=True):
    """
    Function to convert the LAS output into a lighter file format, LAZ
    :param path_to_data:
    :return:
    """
    file_list = glob.glob(path_to_data + '*.las')
      
    for file in file_list:
        try:
            commandLas2Laz="pdal translate " + file + ' ' + path_to_data + file.split('/')[-1][:-4] + ".laz"
            os.system(commandLas2Laz)
            if delete_las:
                os.remove(file)
        except IOError:
            print('Failed to transform las to laz')

def extract_dem(GSD= 0.1,
                origin_x=0,
                origin_y=0,
                height=10,
                width=20,
                sampling_interval=180,
                method='pdal',
                path_to_data='/home/data/',
                delete_las=True,
                tif_to_zip=False):
    """
    Function to extract DEM using pdal writers

    https://pdal.io/stages/writers.gdal.html

    :param GSD: Ground Sampling Distance, often calle resolution [m]
    :param origin_x: lower left x coordinate [m]
    :param origin_y: lower left y coordinate [m]
    :param height: DEM height [m]
    :param width:  DEM width [m]
    :param method:
    :param path_to_data:
    :param delete_las:
    :return:
    """
    
    file_list = glob.glob(path_to_data + '*.las')

    # Convert width and height from meter to number of cell to be compatible with pdal
    ncell_width = width // GSD
    ncell_height = height // GSD


    for file in file_list:
        try:
            # Compute DEM with PDAL
            if method == 'pdal':
                pip_filter_json = json.dumps(
                    {
                        "pipeline":
                            [
                                file,
                                {
                                    "type": "writers.gdal",
                                    "gdaldriver": "GTiff",
                                    "output_type": "all",
                                    "resolution": str(GSD),
                                    "origin_x": str(origin_x),
                                    "origin_y": str(origin_y),
                                    "width": str(ncell_width),
                                    "height": str(ncell_height),
                                    "filename": path_to_data +  file.split('/')[-1][:-4] + ".tif"
                                }
                            ]
                    })
                pipeline = pdal.Pipeline(pip_filter_json)
                pipeline.execute()
#                if tif_to_zip:
#                    # zip the geotiff and remove it
#                    zipcmd = "sh -c \"cd " + path_to_data + "TIFs/ && zip " + file.split('/')[-1][:-4] + ".zip " + file.split('/')[-1][:-4] + ".tif\""
#                    os.system(zipcmd)
#                    os.remove(path_to_data + "TIFs/" + file.split('/')[-1][:-4] + ".tif")
            # even if the las wasn't turned into a DEM, it is now meant to be removed :
            if delete_las:
                os.remove(file)
        except Exception:
            print('Pdal pipeline to derive DEM failed')

            # Script to convert geotiff to netcdf


def fillnodata(fname, band=1, maxSearchDist=5, smoothingIterations=0):
    ET = gdal.Open(fname, gdal.GA_Update)
    ETband = ET.GetRasterBand(band)
    result = gdal.FillNodata(targetBand=ETband, maskBand=None,
                             maxSearchDist=maxSearchDist, smoothingIterations=smoothingIterations)
    ETband = None
    ET = None
    

def raster_to_ds_daily(dir_input, dir_output, compression=True, filename_format='%Y%m%d.nc'):
    """
    function to store geotif into daily netcdf

    :param dir_input: path to folder with geotif, str
    :param dir_output: path to output folder, str
    :param compression: copmress netcdf or not, defaults to True,  bool, optional
    :param filename_format: output file name format following datetime system, defaults to '%Y%m%d.nc',  str, optional
    """    

    # list filename
    flist = glob.glob(dir_input + '*.tif')
    flist.sort()
    print(flist)
    for f_rast in flist:
        fillnodata(f_rast)
        
    # create dataframe of file metadata
    meta = pd.DataFrame({'fname':flist})
    #extract timestamp from filename
    meta['tst'] = pd.to_datetime(meta.fname.apply(lambda x: x.split('/')[-1][:-4]), format="%Y.%m.%dT%H-%M-%S_rot")

    # Create one netcdf file per day
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
        fname_nc = dir_output + meta.tst.loc[meta.tst.dt.day==date].iloc[0].strftime(filename_format)
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
    for file in flist:
        os.remove(file)

        
def raster_to_ds_daily_single(file_input, dir_output='./', compression=True, filename_format='%Y%m%d.nc', remove_raster=True):
    """
    function to store geotif into daily netcdf

    :param dir_input: path to folder with geotif, str
    :param dir_output: path to output folder, str
    :param compression: copmress netcdf or not, defaults to True,  bool, optional
    :param filename_format: output file name format following datetime system, defaults to '%Y%m%d.nc',  str, optional
    """    

    
    fillnodata(file)
    geotiffs_da = xr.open_rasterio(file)
    geotiffs_da = geotiffs_da.where(geotiffs_da!=-9999, drop=True)
    var_name = dict(zip(geotiffs_da.band.values, geotiffs_da.descriptions))
    geotiffs_ds = geotiffs_da.to_dataset('band')
    geotiffs_ds = geotiffs_ds.rename(var_name)
    
    # save to netcdf file
    fname_nc = dir_output + geotiffs_ds.time.strftime(filename_format)
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
    
    if remove_raster:
        os.remove(file)
        
        
        
        
    # create dataframe of file metadata
    meta = pd.DataFrame({'fname':flist})
    #extract timestamp from filename
    meta['tst'] = pd.to_datetime(meta.fname.apply(lambda x: x.split('/')[-1][:-4]), format="%Y.%m.%dT%H-%M-%S_rot")

    # Create one netcdf file per day
    for date in meta.tst.dt.day.unique():
        # create time variable
        time_var = xr.Variable('time', meta.tst.loc[meta.tst.dt.day==date])
        # open raster files in datarray
        geotiffs_da = xr.open_rasterio(file)
        # drop all NaN values
        geotiffs_da = geotiffs_da.where(geotiffs_da!=-9999, drop=True)
        # rename variables with raster band names
        var_name = dict(zip(geotiffs_da.band.values, geotiffs_da.descriptions))
        geotiffs_ds = geotiffs_da.to_dataset('band')
        geotiffs_ds = geotiffs_ds.rename(var_name)

        # save to netcdf file
        fname_nc = dir_output + meta.tst.loc[meta.tst.dt.day==date].iloc[0].strftime(filename_format)
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
    for file in flist:
        os.remove(file)