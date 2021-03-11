from snowyowl import SnowyOwlAcquisition as SOA
import logging

testA=SOA.SnowyOwlAcquisition(outfolder="/home/pi/data/livox_raw/", ip_livox="192.168.1.104", ip_computer="192.168.1.2")
testA.acquireClouds(number_of_scans=0,duration_between_scans=10, duration=10)

