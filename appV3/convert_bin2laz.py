import openpylivox as opl
import glob, os
from multiprocessing import Pool
from pathlib import Path


def convert_bin_to_laz(project_dir='/home/data',
                       bin_folder='bin',
                       file_pattern='*.bin',
                       laz_folder='laz_raw',
                       delete_bin = False,
                       num_proc=4):
    """
    Function to convert a list of Livox binary files from .bin to .laz
    Args:
        bin_flist (str list): list of .bin filepath to convert
        output_path (str): path where to export file
        deleteBin (bool): delete bin file, True/False
    """
    p = Path(project_dir)
    file_list = glob.glob(str(p / bin_folder / file_pattern))
    file_list.sort()
    if file_list.__len__() == 0:
        print('WARNING: No file found')
        return

    pool = Pool(num_proc)
    pool.starmap(opl.convertBin2LAZ, zip(file_list, [delete_bin]*len(file_list)))
    pool.close()
    pool.join()

    laz_list = (p / bin_folder).glob('*.laz')

    for file in laz_list:
        if os.path.isfile(file):
            os.rename(file, str(p / laz_folder / file.name))
    return
    
    

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--project_directory', '-dir', help='Path to project directory', default='./myproject')
    parser.add_argument('--bin_folder', '-bf', help='Folder containing bin files', default='bins')
    parser.add_argument('--laz_folder', '-lf', help='Folder containing laz files', default='laz_raw')
    parser.add_argument('--file_pattern', '-fp', help='File pattern of the bin file to convert', default='20*.bin')
    parser.add_argument('--delete_bin', '-db', help='Delete bin files or not True/False', default=False, type=bool)
    parser.add_argument('--num_proc', '-nc', help='Number of core to use', default=4, type=int)
    args = parser.parse_args()
    
    convert_bin_to_laz(project_dir=args.project_directory,
                       bin_folder=args.bin_folder,
                       file_pattern=args.file_pattern,
                       laz_folder=args.laz_folder,
                       delete_bin=args.delete_bin,
                       num_proc=args.num_proc)
        
                       
                       
                       
                       
