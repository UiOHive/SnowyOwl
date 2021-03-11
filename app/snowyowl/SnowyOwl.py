import openpylivox as opl
from datetime import datetime
import time, os, sys
import numpy as np
from laspy.file import File as lasFile
from math import sin, cos, radians
import pdal
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import logging

class SnowyOwl():
    def __init__(self, outfolder="/home/", extrinsic=[0,0,0,0,0,0]):
        '''
        outFolder: location of output
        LIVOX_IP: IP address of LIVOX sensor (typically 198.168.1.1XX, with XX the last numbers of serial number)
        Computer_IP: IP of the computer, setup fixed on the network connecting to the LIVOX
        extrinsic: [X,Y,Z,omega,phi,kappa] of the sensor

        '''

        self.outfolder = outfolder
        os.makedirs(self.outfolder, exist_ok=True)
        os.makedirs(self.outfolder + 'bin/', exist_ok=True)
        os.makedirs(self.outfolder + 'las_raw', exist_ok=True)
        os.makedirs(self.outfolder + 'las_referenced', exist_ok=True)
        os.makedirs(self.outfolder + 'OUTPUT', exist_ok=True)
        # Matrix for scipy
        #self.rotMat2=R.from_rotvec([radians(extrinsic[3]),radians(extrinsic[4]),radians(extrinsic[5])])

        #Matrix for pdal pipeline
        Mom = np.matrix([[1, 0, 0], [0, cos(radians(extrinsic[3])), sin(radians(extrinsic[3]))], [0, -sin(radians(extrinsic[3])), cos(radians(extrinsic[3]))]])
        Mph = np.matrix([[cos(radians(extrinsic[4])), 0, -sin(radians(extrinsic[4]))], [0, 1, 0], [sin(radians(extrinsic[4])), 0, cos(radians(extrinsic[4]))]])
        Mkp = np.matrix([[cos(radians(extrinsic[5])), sin(radians(extrinsic[5])), 0], [-sin(radians(extrinsic[5])), cos(radians(extrinsic[5])), 0], [0, 0, 1]])
        rotMat = (Mkp * Mph * Mom).T.getA().flatten()
        self.affineMatrix=np.concatenate((rotMat[0:3],[extrinsic[0]],rotMat[3:6],[extrinsic[1]],rotMat[6:9],[extrinsic[2]],[0],[0],[0],[1]))
        self.affineMatrixString = ' '.join([str(elem) for elem in self.affineMatrix])


    def extractDatafrombin(self, corners = [-0.5,0.5,-0.5,0.5], GSD=0.1):
        '''
        :param corners: [x_min,x_max,y_min,y_max] of the cropped area to keep all point for
        :return:
        '''
        logging.basicConfig(filename=self.outfolder + 'Processsing.log', level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s : %(message)s')
        listtmpfiles = os.listdir(self.outfolder + "bin/")
        for f in range(0,len(listtmpfiles)):
            opl.convertBin2LAS(self.outfolder + "bin/" + listtmpfiles[f], deleteBin=True)
            # Move converted las to las_raw folder
            os.rename(self.outfolder + "bin/" + listtmpfiles[f] + '.las', self.outfolder + 'las_raw/' + listtmpfiles[f] + '.las')

            # Tranform cloud accoring to extrinsics
            # create pdal transormation JSON
            json = """
            [
                """ + "\"" + self.outfolder + "las_raw/" +  listtmpfiles[f] + """.las",
                {
                    "type":"filters.transformation",
                    "matrix":" """ + self.affineMatrixString + """"
                },
                {
                    "type":"writers.las",
                    "filename":""" + "\"" + self.outfolder + "las_referenced/" +  listtmpfiles[f] + """.las"
                }
            ]
            """
            pipeline = pdal.Pipeline(json)
            count = pipeline.execute()
            #arrays = pipeline.arrays
            #metadata = pipeline.metadata
            #log = pipeline.log

            # Extract region of interest from cloud
            # create pdal transormation JSON
            json = """
            [
                """ + "\"" + self.outfolder + "las_referenced/" +  listtmpfiles[f] + """.las",
                {
                    "type":"filters.crop",
                    "bounds":" ([""" + str(corners[0]) + "," + str(corners[1]) + "],[" + str(corners[2]) + "," + str(corners[3]) + """])"
                },
                {
                    "type":"writers.las",
                    "filename":""" + "\"" + self.outfolder + "OUTPUT/" +  listtmpfiles[f] + """_cropped.las"
                }
            ]
            """
            pipeline = pdal.Pipeline(json)
            count = pipeline.execute()
            #arrays = pipeline.arrays
            #metadata = pipeline.metadata
            #log = pipeline.log

            # Extract DEM from cloud
            # create pdal transormation JSON
            json = """
            [
                """ + "\"" + self.outfolder + "las_referenced/" +  listtmpfiles[f] + """.las",
                {
                    "type":"writers.gdal",
                    "gdaldriver":"GTiff",
                    "output_type":"all",
                    "resolution":""" + "\"" + str(GSD) + """",
                    "filename":""" + "\"" + self.outfolder + "OUTPUT/" +  listtmpfiles[f] + """.tif"
                }
            ]
            """
            pipeline = pdal.Pipeline(json)
            count = pipeline.execute()
            #arrays = pipeline.arrays
            #metadata = pipeline.metadata
            #log = pipeline.log

            logging.info("Processed file : " + listtmpfiles[f])