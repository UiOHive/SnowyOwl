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
import time, logging
import argparse, os
import numpy as np

import subprocess


def ping(host, interface=None):
    if interface is None:
        command = ['ping', '-c', '1', host]
    else:
        command = ['ping', '-c', '1', '-I', 'enp2s0', host]
    return subprocess.call(command) == 0


def acquire_clouds(scan_duration=3.0,
                   folder='/home/data/',
                   IP_sensor='192.168.13.104',
                   IP_computer='192.168.13.35', 
                  network_interface=None):
    """
    Function to connect and sample point clouds for a given time at every given interval.
    :param scan_duration: duration in second of a scan
    :param folder: folder to save .bin point clouds
    :param IP_sensor: IP address of the scanner
    :return:
    """
    if ping(IP_sensor, interface=network_interface):
        nb_scan = 0  # Reset value to 0 so the following logic works
        sensor = opl.openpylivox(True)
        connected = sensor.connect(IP_computer, IP_sensor, 60001, 50001, 40001)
        if sensor._isConnected:
            logging.info("Connection to Livox scanner successful")
            sensor.setExtrinsicToZero()
            sensor.lidarSpinUp()  # Data Acquisition
            sensor.setLidarReturnMode(
                2)  # set lidar return mode (0 = single 1st return, 1 = single strongest return, 2 = dual returns
            sensor.setIMUdataPush(False)  # activate the IMU data stream (only for Horizon and Tele-15 sensors)
            sensor.setRainFogSuppression(False)  # turn on (True) or off (False) rain/fog suppression on the sensor
            # False here because we are interested in catching snow particles moving through the sensor
            print("\n***** Done setting parameters *****\n")
            filename = folder + datetime.utcnow().strftime("%Y.%m.%dT%H-%M-%S.bin")
            sensor.dataStart_RT_B()  # start data stream (real-time writing of point cloud data to a BINARY file)
            sec_wait = 0  # seconds, time delayed data capture start
            # (*** IMPORTANT: this command starts a new thread, so the current program (thread) needs to exist for the 'duration' ***)
            # capture the data stream and save it to a file (if applicable, IMU data stream will also be saved to a file)
            sensor.saveDataToFile(filename, sec_wait, scan_duration)
            acquisition_start_time = time.perf_counter()
            while True:
                if sensor.doneCapturing() or ((time.perf_counter() - acquisition_start_time) > (2 * scan_duration)):
                    logging.info("Data capture stopped after {}s".format(time.perf_counter() - acquisition_start_time))
                    if (time.perf_counter() - acquisition_start_time) < (0.5 * scan_duration):
                        logging.info("Data capture was much shorter than expected, disconnecting and starting again")
                        # sensor.disconnect()
                    elif (time.perf_counter() - acquisition_start_time) > (2 * scan_duration):
                        logging.info("Data capture was much longer than expected, disconnecting and starting again")
                        # sensor.disconnect()
                    else:
                        sensor.dataStop()
                        logging.info(f"Lidar loop {nb_scan} ==== Cloud acquired with name {filename}")
                    break

            sensor.disconnect()
            # logging.info("Disconnected from LIVOX, reached max nb of scans limit: {}".format(nb_scan_max))
        else:
            print(f"\n***** Could not connect to Livox sensor with IP address {IP_sensor} *****\n")
            logging.error(f"Could not connect to Livox sensor with IP address {IP_sensor}")
    else:
        print(f'IP {IP_sensor} does not ping')
        logging.error(f'IP {IP_sensor} does not ping')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--scan_duration', '-d', help='Scan duration (s)', type=int, default=10)
    parser.add_argument('--output_folder', '-o', help='Path to store bin file', default='/home/<user>/myscans/')
    parser.add_argument('--IP_scanner', '-ips', help='IP address of sensor', default='192.168.13.104')
    parser.add_argument('--IP_computer', '-ipc', help='IP address of computer', default='192.168.13.35')
    parser.add_argument('--network_interface', '-i', help='Network interface', default='None')
    args = parser.parse_args()

    path_to_data = args.output_folder
    os.makedirs(path_to_data, exist_ok=True)
    os.makedirs(path_to_data + 'bins', exist_ok=True)
    os.makedirs(path_to_data + 'archive', exist_ok=True)

    logging.basicConfig(filename=path_to_data + 'lidar_acquisition.log',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s : %(message)s')

    '''
    TODO HERE: add logic to check if folder structure is good and existing
    '''
    acquire_clouds(scan_duration=np.int64(args.scan_duration),
                   folder=args.output_folder,
                   IP_sensor=args.IP_scanner,
                   IP_computer=args.IP_computer,
                  network_interface=args.network_interface)
