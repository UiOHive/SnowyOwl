#! /usr/bin/bash

# Script to acquire webcam and lidar at a single timestep
# Simon Filhol, May 2023

#============ Parameters ==============
# Webcam parameters
image_dir='/mnt/images/'
cam_ip='192.168.1.10'
# cam_user and cam_ip defined in .bashrc as    export cam_user='dfdf'

# Scanning parameters
scan_duration=10
scan_dir='/mnt/bins/'
scan_ip='192.168.1.170'
computer_ip='192.168.1.1'

# ------ STEP 1: Powering Sensors ------------
echo "\n ================================================= \n" >> log.log
now=$(date +"%Y-%m-%d %H:%M:%S")
echo "$now ---> Powering lidar and webcam" >> log.log
sudo python ~/github/SnowyOwl/appV3/relay.py -s 'on' -ri 1 -off 'True' -t 30

# ------- STEP 2: capture image from webcam --------
now=$(date +"%Y-%m-%d %H:%M:%S")
echo "$now ---> Snap picture" >> log.log
#sudo python ~/github/SnowyOwl/appV3/snap_picture_webcam.py -ip $cam_ip -p 554 -u $cam_user -pwd $cam_pwd -o $image_dir >> log.log
sudo python ~/scripts/snap_picture_webcam.py -cf ~/scripts/config_webcam.ini

# ------- STEP 3: acquire point cloud --------
now=$(date +"%Y-%m-%d %H:%M:%S")
echo "$now ---> Start lidar" >> log.log
~/livox/bin/python ~/github/SnowyOwl/appV3/acquisition.py -d $scan_duration -o $scan_dir -ips $scan_ip -ipc $computer_ip >> log.log

# ------- STEP 4: turn relay off --------
now=$(date +"%Y-%m-%d %H:%M:%S")
echo "$now ---> Depowering sensors" >> log.log
sudo python ~/github/SnowyOwl/appV3/relay.py -s 'off' -ri 1 -off 'False' -t 0