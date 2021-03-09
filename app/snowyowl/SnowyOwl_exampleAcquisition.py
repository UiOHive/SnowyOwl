from snowyowl import SnowyOwlAcquisition as SOA
#path = "/home/luc/data/LIVOX/"
path = "/home/pi/data/livox_raw/"
testA=SOA.SnowyOwlAcquisition(outfolder=path, ip_livox="192.168.1.104", ip_computer="192.168.1.2")

test.acquiereNCloud(number_of_scans=4,duration_between_scans=0, duration=10)

