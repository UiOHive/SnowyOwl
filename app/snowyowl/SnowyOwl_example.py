from snowyowl import SnowyOwl as SO

#path = "/home/luc/data/LIVOX/"
path = "/home/pi/data/livox_raw/"
test=SO.SnowyOwl(outfolder=path, ip_livox="192.168.1.104", ip_computer="192.168.1.2", extrinsic=[0,0,0,-30,90,0])

test.acquiereNCloud(number_of_scans=4,duration_between_scans=0, duration=10)

#test.extractDatafrombin()
