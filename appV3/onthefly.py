"""
Script to run scanner once

Simon Filhol

Example:
    python onthefly.py -sd 20 -n 1 -o /home/tmp
"""

from appV3 import acquisition as aq
import time

def reboot_lidar():
    import relay_lib_seeed as rs
    rs.relay_on(1)
    print('---> Lidar is turned OFF')
    time.sleep(30) # wait nearly as long as the scanning interval before tunring on again

    # turn lidar on
    rs.relay_off(1)
    time.sleep(20) # 20 second wait, to be sure the scanner is booted up
    print('---> Lidar is turned ON')


if __name__ == "__main__":
    import argparse, os

    parser = argparse.ArgumentParser()
    parser.add_argument('--scan_duration', '-d', help='Duration of a single scan (second)', default=20)
    parser.add_argument('--nb_scan_max', '-n', help='Maximum number of scan to perform', default=1)
    parser.add_argument('--output_folder', '-o', help='Path to save output .bin files', default='/home/data')
    parser.add_argument('--IP_sensor', '-is', help='IP address of scanner', default='192.168.13.104')
    parser.add_argument('--IP_computer', '-ic', help='IP address of acquisition computer', default='192.168.13.35')

    args = parser.parse_args()

    if args.reboot_scanner:
        print('---> Rebooting lidar')
        reboot_lidar()
    print('---> Scanning triggered')
    aq.acquire_clouds(scan_duration=args.scan_duration,
                      scan_interval=args.scan_interval,
                      nb_scan_max=args.nb_scan_max,
                      folder=args.output_folder,
                      IP_sensor=args.IP_sensor,
                      IP_computer=args.IP_computer)
    print('-> {} scan saved to {}'.format(args.nb_scan_max, args.output_folder))
    print('---> Command to send data to Echobase:')
    cmd = 'scp tmp/* lucg@echobase:/home/lucg/tmp/'
    print(cmd)




