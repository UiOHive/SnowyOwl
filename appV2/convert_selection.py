import numpy as np
import configparser, logging
import openpylivox as opl
import glob, os
import pdal, json
import pandas as pd

def convert_bin_to_las(bin_flist, output_path, deleteBin = False):
    """
    Functionto convert a list of files from .bin to .las
    Args:
        bin_flist (str list): list of .bin filepath to convert
        output_path (str): path where to export file
        deleteBin (bool): delete bin file, True/False
    """

    for file in bin_flist:
        opl.convertBin2LAS(file, deleteBin=deleteBin)
        if os.path.isfile(file + '.las'):
            os.rename(file + '.las', output_path + file.split('/')[-1][:-4] + '.las')
        else:
            os.remove(file)
            print(file, ' removed.')

