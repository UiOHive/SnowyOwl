from snowyowl import SnowyOwl as SO

test=SO.SnowyOwl(outfolder="/home/luc/data/LIVOX/", ip_livox="192.168.1.104", ip_computer="192.168.1.2", extrinsic=[0,0,0,-30,90,0])

test.acquiereNCloud(number_of_scans=1,duration_between_scans=0)

test.extractDatafrombin()