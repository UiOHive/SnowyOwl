from snowyowl import SnowyOwlAcquisition as SOA
import logging
import getpass

if getpass.getuser()=='livoxpi':
    ip_computer="192.168.13.35"
    outfolder="/mnt/LivoxDrive/"
elif getpass.getuser()=='snowyowl':
    ip_computer="192.168.13.36"
    outfolder="/home/snowyowl/data/LivoxDirect/"


testA=SOA.SnowyOwlAcquisition(outfolder=outfolder, ip_livox="192.168.1.104", ip_computer=ip_computer)
testA.acquireClouds(number_of_scans=0,duration_between_scans=10, duration=10)

