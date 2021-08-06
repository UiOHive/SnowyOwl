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
        opl.convertBin2LAS(file, deleteBin=True)
        os.remove(file)
        print(file, ' removed.')

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
