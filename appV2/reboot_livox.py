'''
Script to reboot lidar.

'''
import sys
import time, logging, configparser

def reboot_lidar(config):
    sys.path.append(config.get('acquisition', 'path_to_relay_pkg'))
    from relay_lib_seeed import *

    relay_on(1)
    print('---> Lidar is turned OFF')
    time.sleep(config.getint('acquisition', 'scanning_interval')-60) # wait nearly as long as the scanning interval before tunring on again

    # turn lidar on
    relay_off(1)
    time.sleep(20) # 20 second wait, to be sure the scanner is booted up
    print('---> Lidar is turned ON')

if __name__ == "__main__":
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-cf', help='Path to config file', default='/home/config.ini')
    args = parser.parse_args()

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(args.config_file)

    logging.basicConfig(filename=config.get('acquisition', 'data_folder') + 'Acquisition.log',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s : %(message)s')
    logging.info('Rebooting lidar')
    # turn lidar off:
    reboot_lidar(config)
    logging.info('Lidar has been rebooted')