import openpylivox as opl
from datetime import datetime
import time, os, sys, logging

class SnowyOwlAcquisition():
    def __init__(self, outfolder="/home/luc/data/LIVOX/", ip_livox="192.168.1.104", ip_computer="192.168.1.2"):
        '''
        outFolder: location of output
        LIVOX_IP: IP address of LIVOX sensor (typically 198.168.1.1XX, with XX the last numbers of serial number)
        Computer_IP: IP of the computer, setup fixed on the network connecting to the LIVOX
        extrinsic: [X,Y,Z,omega,phi,kappa] of the sensor

        '''

        self.outfolder = outfolder
        self.ip_livox = ip_livox
        self.ip_computer = ip_computer

    def acquireClouds(self, duration=3.0, duration_between_scans=10, number_of_scans=1):
        # Setup
        # duration : integration time for the lidar in seconds (default = 3s)
        # number_of_scans : number of consecutive scans to be made (default = 1, set to 0for infinity)
        # duration_between_scans : cooldown between acquisitions in seconds (default=10)
        logging.basicConfig(filename=self.outfolder + 'Acquisition.log', level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s : %(message)s')
        sensor = opl.openpylivox(True)
        connected = sensor.connect(self.ip_computer, self.ip_livox, 60001, 50001, 40001)
        if connected:
            logging.info("Connection to LIVOX successful")
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
            i=1
            while (i<=number_of_scans or number_of_scans==0):
                try:
                    # Make sure the interval of acquisition give regular timestamp, instead of just using time.sleep()
                    # as it would drift, giving data points not neatly spread
                    while not (datetime.utcnow().second % (duration + duration_between_scans) == 0):
                        sleep(0.5)
                    filename = self.outfolder + "tmp/" + datetime.utcnow().strftime("%Y.%m.%dT%H-%M-%S.bin")
                    # start data stream (real-time writing of point cloud data to a BINARY file)
                    sensor.dataStart_RT_B()
                    secsToWait = 0  # seconds, time delayed data capture start
                    # (*** IMPORTANT: this command starts a new thread, so the current program (thread) needs to exist for the 'duration' ***)
                    # capture the data stream and save it to a file (if applicable, IMU data stream will also be saved to a file)
                    sensor.saveDataToFile(filename, secsToWait, duration)
                    while True:
                        if sensor.doneCapturing():
                            break
                    sensor.dataStop()
                    logging.info("Cloud acquiered with name" + filename)
                    # increment counter
                    i=i+1
                except:
                    logging.warning("Data acquisition failed")
                    sensor.disconnect()
                    connected = False

            # if you want to stop the lidar from spinning (ie., lidar to power-save mode)
            sensor.lidarSpinDown()
            sensor.disconnect()
        else:
            print("\n***** Could not connect to a Livox sensor *****\n")
            logging.error("Could not connect to a Livox sensor")