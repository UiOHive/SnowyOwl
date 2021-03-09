from snowyowl import SnowyOwl as SO
from snowyowl import SnowyOwlAcquisition as SOA
#path = "/home/luc/data/LIVOX/"
path = "/home/pi/data/livox_raw/"
test=SO.SnowyOwl(outfolder=path, extrinsic=[0,0,0,-30,90,0])

test.extractDatafrombin()
