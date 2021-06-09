'''
Script to convert point cloud file between .las and .laz
S. Filhol, Apr 2021

Example:
python lazzip.py -c laz2las -plaz ../data/OUTPUT/ -plas ../data/OUTPUT/ -rm false


TODO:
- add progress bar with tqdm

'''
import os
import glob
from tqdm import tqdm

def laz_2_las(path_to_laz='/home/data/', path_to_las=None, delete_laz=False):
    """
    Function to convert the LAZ files to LAS, redeable with laspy
    :param path_to_las:
    :param path_to_laz:
    :param delete_laz: boolean to indicate if removing file:return:
    """
    if path_to_las is None:
        path_to_las = path_to_laz
        
    file_list = glob.glob(path_to_laz + '*.laz')
      
    for file in tqdm(file_list):
        try:
            commandLaz2Las = "pdal translate " + file + ' ' + path_to_las  + file.split('/')[-1][:-4] + ".las"
            os.system(commandLaz2Las)
            if delete_laz:
                os.remove(file)
        except IOError:
            print('Failed to transform file ' + file.split('/')[-1] + ' laz to las')

            
def las_2_laz(path_to_las='/home/data/', path_to_laz=None, delete_las=False):
    """
    Function to convert the LAS files to LAZ, a highly compressed format for point clouds
    :param path_to_las:
    :param path_to_laz:
    :param delete_las: boolean to indicate if removing file
    :return:
    """
    if path_to_laz is None:
        path_to_laz = path_to_las
        
    file_list = glob.glob(path_to_las + '*.laz')
      
    for file in tqdm(file_list, ncols=75):
        try:
            commandLas2Laz = "pdal translate " + file + ' ' + path_to_laz  + file.split('/')[-1][:-4] + ".laz"
            os.system(commandLas2Laz)
            if delete_las:
                os.remove(file)
        except IOError:
            print('Failed to transform file ' + file.split('/')[-1] + ' las to laz')

            
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True', 'Y'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False', 'N'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        
            
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--conversion', '-c', help='File conversion to apply', default='las2laz')
    parser.add_argument('--path_laz', '-plaz', help='Path to *.laz files', default='~/github/SnowyOwl/data')
    parser.add_argument('--path_las', '-plas', help='Path to *.las files', default='~/github/SnowyOwl/data')
    parser.add_argument('--remove_files', '-rm', help='Delete original files', default='false')
    args = parser.parse_args()
    
    # Check is directories exist, if not it will create them
    os.makedirs(args.path_laz, exist_ok=True)
    os.makedirs(args.path_las, exist_ok=True)
    
    if args.conversion == 'las2laz':
        las_2_laz(path_to_las=args.path_las, path_to_laz=args.path_laz, delete_las= str2bool(args.remove_files))
    elif args.conversion == 'laz2las':
        laz_2_las(path_to_laz=args.path_laz, path_to_las=args.path_las, delete_laz= str2bool(args.remove_files))
    else:
        print('Conversion type not existing. Must be las2laz or laz2las')
    