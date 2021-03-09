import openpylivox as opl
from datetime import datetime
import time, os, sys
import numpy as np
from laspy.file import File as lasFile
from math import sin, cos, radians

from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class SnowyOwl():
    def __init__(self, outfolder="/home/luc/data/LIVOX/", extrinsic=[0,0,0,0,0,0]):
        '''
        outFolder: location of output
        LIVOX_IP: IP address of LIVOX sensor (typically 198.168.1.1XX, with XX the last numbers of serial number)
        Computer_IP: IP of the computer, setup fixed on the network connecting to the LIVOX
        extrinsic: [X,Y,Z,omega,phi,kappa] of the sensor

        '''

        self.outfolder = outfolder
        self.rotMat2=R.from_rotvec([radians(extrinsic[3]),radians(extrinsic[4]),radians(extrinsic[5])])
        #
        # Mom = np.matrix([[1, 0, 0], [0, cos(radians(extrinsic[3])), sin(radians(extrinsic[3]))], [0, -sin(radians(extrinsic[3])), cos(radians(extrinsic[3]))]])
        # Mph = np.matrix([[cos(radians(extrinsic[4])), 0, -sin(radians(extrinsic[4]))], [0, 1, 0], [sin(radians(extrinsic[4])), 0, cos(radians(extrinsic[4]))]])
        # Mkp = np.matrix([[cos(radians(extrinsic[5])), sin(radians(extrinsic[5])), 0], [-sin(radians(extrinsic[5])), cos(radians(extrinsic[5])), 0], [0, 0, 1]])
        # rotMat = (Mkp * Mph * Mom).getA().flatten()
        # self.affineMatrix=np.concatenate((rotMat[0:3],[extrinsic[0]],rotMat[3:7],[extrinsic[1]],rotMat[7:9],[extrinsic[2]],[0],[0],[0],[1]))
        # self.affineMatrixString = ' '.join([str(elem) for elem in self.affineMatrix])


    def extractDatafrombin(self, corners = [0.75,1.25,-0.25,0.25]):
        '''
        :param corners: [x_min,x_max,y_min,y_max] of the cropped area to keep all point for
        :return:
        '''
        listtmpfiles = os.listdir(self.outfolder + "tmp/")
        for f in range(0,len(listtmpfiles)):
            opl.convertBin2LAS(self.outfolder + "tmp/" + listtmpfiles[f], deleteBin=True)
            inFile = lasFile(self.outfolder + "tmp/" + listtmpfiles[f] + '.las', mode='r')
            # extract points
            coords = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
            # transpose using external orientation.
            coordsRotated=rotMat2.apply(coords)
            fig = plt.figure()
            ax = Axes3D(fig)
            ax.scatter(coords[1:10000, 0], coords[1:10000, 1], coords[1:10000, 2])

            fig = plt.figure()
            ax = Axes3D(fig)
            ax.scatter(coordsRotated[1:10000, 0], coordsRotated[1:10000, 1], coordsRotated[1:10000, 2])


            #
            #
            #
            # # Tranform cloud accoring to extrinsics
            # # create pdal transormation JSON
            # json = """
            # [
            #     """ + "\"" + self.outfolder + "tmp/" +  listtmpfiles[f] + """.las",
            #     {
            #         "type":"filters.transformation",
            #         "matrix":" """ + self.affineMatrixString + """"
            #     },
            #     {
            #         "type":"writers.las",
            #         "filename":""" + "\"" + self.outfolder + "tmp/" +  listtmpfiles[f] + """_transformed.las"
            #     }
            # ]
            # """
            # pipeline = pdal.Pipeline(json)
            # count = pipeline.execute()
            # arrays = pipeline.arrays
            # metadata = pipeline.metadata
            # log = pipeline.log
            #
            # # use CloudCompareto rotate the Cloud of the appropriate value
            # commandRotate = 'cloudcompare.CloudCompare -SILENT -o '+ self.outfolder + "tmp/" + listtmpfiles[f] + '.las -APPLY_TRANS CCTransform.txt'
            # print(commandRotate)
            # os.system(commandRotate)
            # # make DEM from Cloud
            # commandRaster='cloudcompare.CloudCompare -SILENT -o -RASTERIZE -GRID_STEP 0.1 -PROJ MIN -OUTPUT_RASTER_Z'
            # print(commandRaster)
            # os.system(commandRaster)
            #
            #
            # inFile = lasFile(self.outfolder + "tmp/" + listtmpfiles[f] + '.las', mode='r')
            # # extract points
            # coords= inFile.points  #= np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
            # # transpose using external orientation.
            # for i in range(len(inFile.x)):
            #     newcoord=self.rotMat * np.matrix([[coords[i,0] - self.sensorPos[0]], [coords[i,1] - self.sensorPos[1]], [coords[i,2] - self.sensorPos[2]]])
            #     coords[i] = newcoord.getA()
            # # create filter to remove points out of square of interest
            # filter = np.logical_and(np.logical_and(coords[:,0] >= corners[0],coords[:,0] <= corners[1]),np.logical_and(coords[:,1] >= corners[2],coords[:,1] <= corners[3]))
            #
            # # Grab an array of all points which meet this threshold
            # points_kept = inFile.points[filter]
            # outFile = lasFile(self.outfolder + listtmpfiles[f] + '.las', mode="w",header=inFile.header)
            # outFile.points = points_kept
            # outFile.close()
            #
            # # move output out of tmp folder
            # os.rename(self.outfolder + "tmp/" + listtmpfiles[i] + '.las', self.outfolder + listtmpfiles[i] + '.las')
            #
            #

# x = 0  # units of meters
# y = 0  # units of meters
# z = 0  # units of meters
# roll = 0  # units of degrees
# pitch = 60  # units of degrees
# yaw = 0  # units of degrees
#
# # set the sensor's extrinsic parameters to specific values
# # (*** IMPORTANT: does not affect raw point cloud data stream, seems to only be used in Livox-Viewer? ***)
# sensor.setExtrinsicTo(x, y, z, roll, pitch, yaw)
