'''
Python Script to connect and run Livox lidar with SnowyOwl on Pi@finse 
Luc Girod, Simon Filhol
March 2021

'''


from snowyowl import SnowyOwlAcquisition as SOA
import logging
import getpass

if getpass.getuser()=='livoxpi':
    ip_computer="192.168.13.35"
    outfolder="/mnt/LivoxDrive/"
elif getpass.getuser()=='snowyowl':
    ip_computer="192.168.13.36"
    outfolder="/home/snowyowl/data/LivoxDirect/"
else:
    print("Computer Not supported yet")

# Config
duration_between_scans = 180 - 10	# time to spend in between end last scane and start next scan
scan_duration = 10			# time in second during which the scanner acquire data for one point cloud 
ip_livox = "192.168.13.104"

# Routine to connect and run scanner
testA=SOA.SnowyOwlAcquisition(outfolder=outfolder, ip_livox=ip_livox, ip_computer=ip_computer)
testA.acquireClouds(number_of_scans=0, duration_between_scans=duration_between_scans, duration=scan_duration)

