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
    Mom = np.matrix([[1, 0, 0], [0, np.cos(np.radians(extrinsic[3])), np.sin(np.radians(extrinsic[3]))],
                     [0, -np.sin(np.radians(extrinsic[3])), np.cos(np.radians(extrinsic[3]))]])
    Mph = np.matrix([[np.cos(np.radians(extrinsic[4])), 0, -np.sin(np.radians(extrinsic[4]))], [0, 1, 0],
                     [np.sin(np.radians(extrinsic[4])), 0, np.cos(np.radians(extrinsic[4]))]])
    Mkp = np.matrix([[np.cos(np.radians(extrinsic[5])), np.sin(np.radians(extrinsic[5])), 0],
                     [-np.sin(np.radians(extrinsic[5])), np.cos(np.radians(extrinsic[5])), 0], [0, 0, 1]])
    rotMat = (Mkp * Mph * Mom).T.getA().flatten()
    affineMatrix = np.concatenate((rotMat[0:3], [extrinsic[0]], rotMat[3:6], [extrinsic[1]], rotMat[6:9], [extrinsic[2]], [0], [0], [0], [1]))
    affineMatrixString = ' '.join([str(elem) for elem in affineMatrix])
    return affineMatrixString

def convert_bin_to_las(path_to_data='/home/data/'):
    file_list = glob.glob(path_to_data + 'bin/*.bin')
    for file in file_list:
        opl.convertBin2LAS(file, deleteBin=True)
        os.rename(file + '.las', path_to_data + 'las_raw/' + file.split('/')[-1][:-4] + '.las')

def rotate_point_clouds(extrinsic=[0,0,0,0,0,0], z_range='[-20, 20]', crop_corners='([-20, 5], [-5, 5])', path_to_data='/home/data/'):
    """
    Function to rotate point clouds and crop potential outliers
    :param extrinsic: [X,Y,Z,omega,phi,kappa] of the sensor
    :param z_range: [Zmin, Zmax] crop in Z of the point clouds.
    :param crop_corners: [Xmin, Xmax, Ymin, Ymax] crop in X and Y of the point clouds to exclude
    :param path_to_data:
    :return:
    """
    rot_mat = rotation_matrix_pdal(extrinsic)
    file_list = glob.glob(path_to_data + 'las_raw/*.las')

    for file in file_list:
        pip_filter_json = json.dumps(
            {
                "pipeline":
                    [
                        file,
                        {
                            "type":"filters.transformation",
                            "matrix": rot_mat
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
                            "filename": path_to_data + "las_referenced/" + file.split('/')[-1]
                        }
                    ]
            })
        pipeline = pdal.Pipeline(pip_filter_json)
        pipeline.execute()

def extract_pcl_subset(corners='([-0.5,0.5],[-0.5,0.5])', path_to_data='/home/data/'):
    """
    Function to extract a point cloud vertical column subset defined by the corners coordinates
    :param corners: x_min,x_max,y_min,y_max of the cropped area to keep all point for
    :param path_to_data:
    :return:
    """
    try:
        file_list = glob.glob(path_to_data + 'las_referenced/*.las')
        for file in file_list:
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
                                "filename":path_to_data + "las_crop/" +  file.split('/')[-1][:-4] + "_cropped.las"
                            }
                        ]
                }
            )
            pipeline = pdal.Pipeline(pip_filter_json)
            pipeline.execute()
    except IOError:
        print('Pdal pipeline failed to extract subset')

def las_2_laz(path_to_data='/home/data/'):
    """
    Function to convert the LAS output into a lighter file format, LAZ
    :param path_to_data:
    :return:
    """
    try:
        file_list = glob.glob(path_to_data + 'las_crop/*.las')
        for file in file_list:
            commandLas2Laz="pdal translate" + file + file.split('/')[-1][:-4] + "laz"
            os.system(commandLas2Laz)
    except IOError:
        print('Failed to transform las to laz')

def extract_dem(GSD= 0.1, sampling_interval=180, method='pdal', path_to_data='/home/data/'):
    """

    :param GSD: Ground
    :param method:
    :param path_to_data:
    :return: 1 if success, 0 otherwise
    """
    try:
        file_list = glob.glob(path_to_data + 'las_referenced/*.las')
        for file in file_list:
            tst_data = pd.to_datetime(file.split('/')[-1][:19])
            if tst_data % sampling_interval == 0:
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
                                        "filename": path_to_data + "OUTPUT/" +  file.split('/')[-1][:-4] + ".tif"
                                    }
                                ]
                        })
                    pipeline = pdal.Pipeline(pip_filter_json)
                    pipeline.execute()

                    # Compute DEM with pandas groupby
                    # if method == 'pandas':
                    #     """
                    #     In development, WARNING:To Be Tested
                    #     """
                    #     from laspy.file import File
                    #
                    #     file_list = glob.glob(path_to_data + 'las_referenced/*.las')
                    #     for las_file in file_list:
                    #         inFile = File(las_file, mode='r')
                    #         myXYZ = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
                    #
                    #         x = myXYZ[:, 0].ravel()
                    #         y = myXYZ[:, 1].ravel()
                    #         z = myXYZ[:, 2].ravel()
                    #         df = pd.DataFrame({'X': x, 'Y': y, 'Z': z})
                    #         bins_x = np.linspace(xstart, xend, nx + 1)
                    #         x_cuts = pd.cut(df.X, bins_x, labels=False)
                    #         bins_y = np.linspace(ystart, yend, ny + 1)
                    #         y_cuts = pd.cut(df.Y, bins_y, labels=False)
                    #         bin_xmin, bin_ymin = x_cuts.min(), y_cuts.min()
                    #         print('Data cut in a ' + str(bins_x.__len__()) + ' by ' + str(bins_y.__len__()) + ' matrix')
                    #         dx = (xend - xstart) / nx
                    #         dy = (yend - ystart) / ny
                    #         print('dx = ' + str(dx) + ' ; dy = ' + str(dy))
                    #         grouped = df.groupby([x_cuts, y_cuts])
    except Exception:
        print('Pdal pipeline to derive DEM failed')


if __name__ == "__main__":
    import argparse, os

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-cf', help='Path to config file', default='/home/config.ini')
    args = parser.parse_args()

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(args.config_file)
    logging.basicConfig(filename=config.get('processing','path_to_data') + 'Processing.log', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s : %(message)s')

    '''
    TODO HERE: 
        - add logic here to check folders to move files around exist. Create if not existing
    '''
    path_to_data=config.get('processing', 'path_to_data')
    os.makedirs(path_to_data, exist_ok=True)
    os.makedirs(path_to_data + 'bin', exist_ok=True)
    os.makedirs(path_to_data + 'las_raw', exist_ok=True)
    os.makedirs(path_to_data + 'las_referenced', exist_ok=True)
    os.makedirs(path_to_data + 'las_crop', exist_ok=True)
    os.makedirs(path_to_data + 'OUTPUT', exist_ok=True)
    os.makedirs(path_to_data + 'SENT', exist_ok=True)

    convert_bin_to_las(path_to_data=config.get('processing', 'path_to_data'))
    rotate_point_clouds(extrinsic=[float(i) for i in config.get('processing', 'sensor_extrinsic').split(',')],
                        z_range=config.get('processing', 'z_range'),
                        crop_corners=config.get('processing', 'crop_extent'),
                        path_to_data=config.get('processing', 'path_to_data'))
    extract_pcl_subset(corners=config.get('processing', 'crop_extent_subsample'),
                       path_to_data=config.get('processing', 'path_to_data'))
    las_2_laz(path_to_data=config.get('processing', 'path_to_data'))
    extract_dem(GSD=config.getfloat('processing', 'dem_resolution'),
                sampling_interval=config.getint('processing', 'dem_sampling_interval'),
                method=config.get('processing', 'dem_method'),
                path_to_data=config.get('processing', 'path_to_data'))

