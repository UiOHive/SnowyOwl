"""
Script to acquire data from Livox Horizon lidar
S. Filhol & L. Girod
March 2021

TODO:
- add in __main__ logic to check if folder structure is good and existing
- TEST code!
"""

import openpylivox as opl
from datetime import datetime
import time, logging, sys
import configparser

def acquire_clouds(scan_duration=3.0,
                   scan_interval=10,
                   nb_scan_max=5,
                   folder='/home/data/',
                   IP_sensor='192.168.13.104',
                   IP_computer='192.168.13.35'):
    """
    Function to connect and sample point clouds for a given time at every given interval.
    :param scan_duration: duration in second of a scan
    :param scan_interval: time interval in seconds in between to scan
    :param nb_scan_max: maximum number of scan until reconnection, set to 0 for infinite number of scan , in which cases the script will disconnect and start again every hour
    :param folder: folder to save .bin point clouds
    :param IP_sensor: IP address of the scanner
    :return:
    """
    nb_scan = 0 # Reset value to 0 so the following logic works
    sensor = opl.openpylivox(True)
    connected = sensor.connect(IP_computer, IP_sensor,  60001,     50001,      40001)
    if connected:
        logging.info("Connection to LIVOX successful")
        sensor.setExtrinsicToZero()
        sensor.lidarSpinUp()                # Data Acquisition
        sensor.setLidarReturnMode(2)        # set lidar return mode (0 = single 1st return, 1 = single strongest return, 2 = dual returns
        sensor.setIMUdataPush(False)        # activate the IMU data stream (only for Horizon and Tele-15 sensors)
        sensor.setRainFogSuppression(False) # turn on (True) or off (False) rain/fog suppression on the sensor
        # False here because we are interested in catching snow particles moving through the sensor
        while (nb_scan_max == 0 or nb_scan < nb_scan_max) and sensor._isConnected:
            # Make sure the interval of acquisition give regular timestamp, instead of just using time.sleep()
            # as it would drift, giving data points clouds not neatly spread in time, even if scan_interval is up to 24h
            while not ((datetime.utcnow().second + 60*datetime.utcnow().minute + 3600*datetime.utcnow().hour) % scan_interval == 0):
                time.sleep(0.5)
            filename = folder + "tmp/" + datetime.utcnow().strftime("%Y.%m.%dT%H-%M-%S.bin")
            sensor.dataStart_RT_B()  # start data stream (real-time writing of point cloud data to a BINARY file)
            secsToWait = 0  # seconds, time delayed data capture start
            # (*** IMPORTANT: this command starts a new thread, so the current program (thread) needs to exist for the 'duration' ***)
            # capture the data stream and save it to a file (if applicable, IMU data stream will also be saved to a file)
            sensor.saveDataToFile(filename, secsToWait, scan_duration)
            # Timer to check if the sensor.doneCapturing() is not bugging out somehow, killing the thread if more than twice the expected time has passed
            AcquisitionStartTime=time.perf_counter()
            while True:
                if sensor.doneCapturing() | ((time.perf_counter()-AcquisitionStartTime)>(2*scan_duration)):
                    logging.info("Data capture stopped after {}s".format(time.perf_counter()-AcquisitionStartTime))
                    break
            sensor.dataStop()

            logging.info("Lidar loop " + str(nb_scan) + " ==== Cloud acquired with name " + filename)
            nb_scan += 1
        # if you want to stop the lidar from spinning (ie., lidar to power-save mode)
        sensor.lidarSpinDown()
        sensor.disconnect()
        logging.info("Disconnected from LIVOX, reached max nb of scans limit: {}".format(nb_scan_max))
    else:
        print("\n***** Could not connect to Livox sensor with IP address " + IP_sensor + " *****\n")
        logging.error("Could not connect to Livox sensor with IP address " + IP_sensor)



if __name__ == "__main__":
    import argparse, os

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-cf', help='Path to config file', default='/home/config.ini')
    args = parser.parse_args()

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(args.config_file)
    sys.path.append(config.get('acquisition', 'path_to_relay_pkg'))

    def reboot_lidar(config):
        relay_on(1)
        print('---> Lidar is turned OFF')
        time.sleep(20) # 20 second wait

        # turn lidar on
        relay_off(1)
        time.sleep(30) # 20 second wait
        print('---> Lidar is turned ON')

    path_to_data = config.get('acquisition', 'data_folder')
    os.makedirs(path_to_data, exist_ok=True)
    os.makedirs(path_to_data + 'tmp', exist_ok=True)
    os.makedirs(path_to_data + 'archive', exist_ok=True)
    
    logging.basicConfig(filename=config.get('acquisition', 'data_folder') + 'Acquisition.log',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s : %(message)s')
    logging.info('Reading config.ini file')

    '''
    TODO HERE: add logic to check if folder structure is good and existing
    '''

    while True:
        acquire_clouds(scan_duration=config.getint('acquisition', 'scan_duration'),
                       scan_interval=config.getint('acquisition', 'scanning_interval'),
                       nb_scan_max=config.getint('acquisition', 'number_of_scan_max'),
                       folder=config.get('acquisition', 'data_folder'),
                           IP_sensor=config.get('acquisition', 'scanner_IP'),
                       IP_computer=config.get('acquisition', 'computer_IP'))
        reboot_lidar(config)