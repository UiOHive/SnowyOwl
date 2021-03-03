import openpylivox as opl
from datetime import datetime
import time, os, sys
import numpy as np

class SnowyOwl():
    def __init__(self, outfolder="/home/luc/data/LIVOX/", ip_livox="192.168.1.104", ip_computer="192.168.1.2"):
        '''
        outFolder: location of output
        LIVOX_IP: IP address of LIVOX sensor (typically 198.168.1.1XX, with XX the last numbers of serial number)
        Computer_IP: IP of the computer, setup fixed on the network connecting to the LIVOX

        '''

        self.outfolder = outfolder
        self.ip_livox = ip_livox
        self.ip_computer = ip_computer

    def acquiereNCloud(self, duration=3.0, number_of_scans=1, duration_between_scans=10, outFolder):
        # Setup
        # duration : integration time for the lidar in seconds (default = 3s)
        # number_of_scans : number of consecutive scans to be made (default = 1)
        # duration_between_scans : cooldown between acquisitions in seconds (default=10)

        sensor = opl.openpylivox(True)
        connected = sensor.connect(self.ip_computer, self.ip_livox,  60001,     50001,      40001)
        sensor.setExtrinsicToZero()



        # Data Acquisition
        sensor.lidarSpinUp()
        # set lidar return mode (0 = single 1st return, 1 = single strongest return, 2 = dual returns)
        sensor.setLidarReturnMode(2)
        # activate the IMU data stream (only for Horizon and Tele-15 sensors)
        sensor.setIMUdataPush(False)
        # turn on (True) or off (False) rain/fog suppression on the sensor
        # False here because we are interested in catching snow particules moving through the sensor
        sensor.setRainFogSuppression(False)

        for i in range(0, number_of_scans):
            # start data stream (real-time writing of point cloud data to a BINARY file)
            sensor.dataStart_RT_B()
            filename = self.outfolder + "tmp/" + datetime.now().strftime("%Y.%m.%d-%H-%M-%S.bin")
            secsToWait = 0 # seconds, time delayed data capture start
            # (*** IMPORTANT: this command starts a new thread, so the current program (thread) needs to exist for the 'duration' ***)
            # capture the data stream and save it to a file (if applicable, IMU data stream will also be saved to a file)
            sensor.saveDataToFile(filename, secsToWait, duration)
            while True:
                if sensor.doneCapturing():
                    break
            sensor.dataStop()
            time.sleep(duration_between_scans)
        # if you want to put the lidar in stand-by mode, not sure exactly what this does, lidar still spins?
        # sensor.lidarStandBy()
        # if you want to stop the lidar from spinning (ie., lidar to power-save mode)
        sensor.lidarSpinDown()
        sensor.disconnect()

    def extractDatafrombin(self):
        listtmpfiles = os.listdir(self.outfolder + "tmp/")
        for i in range(0,len(listtmpfiles)):
            opl.convertBin2LAS(listtmpfiles[i], deleteBin=True)
            # move output out of tmp folder
            os.rename(self.outfolder + "tmp/" + listtmpfiles[i], self.outfolder + listtmpfiles[i])



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