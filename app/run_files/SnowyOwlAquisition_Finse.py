from snowyowl import SnowyOwlAcquisition as SOA
import logging

testA=SOA.SnowyOwlAcquisition(outfolder="/mnt/LivoxDrive/", ip_livox="192.168.13.104", ip_computer="192.168.13.35")
testA.acquireClouds(number_of_scans=0,duration_between_scans=10, duration=10)

