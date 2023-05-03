# Script to acquire webcam and lidar at a single timestep
# Simon Filhol, May 2023

#============ Parameters ==============
# Webcam parameters
image_dir='/mnt/webcam/images/'
cam_ip='192.168.1.120'
# cam_user and cam_ip defined in .bashrc as    export cam_user='dfdf'

# Scanning parameters
scan_duration=20
n_scans=1
scan_dir='/mnt/livox/bins/'
scan_ip='192.168.13.104'
computer_ip='192.168.13.35'

# ------- STEP 1: turn relay on --------
sudo python relay.py -s 'on' -ri 1 -off 'True' -t 30

# ------- STEP 2: capture image from webcam --------
~/livox/bin/python ~/github/SnowyOwl/appV3/snap_picture_webcam.py -ip $cam_ip -p 554 -u $cam_user -pwd $cam_pwd -o $image_dir

# ------- STEP 3: acquire point cloud --------
~/livox/bin/python ~/github/SnowyOwl/appV3/acquisition.py -sd $scan_duration -n $n_scans -o $scan_dir -ips $scan_ip -ipc $computer_ip

# ------- STEP 4: turn relay off --------
sudo python relay.py -s 'off' -ri 1 -off 'False' -t 0
