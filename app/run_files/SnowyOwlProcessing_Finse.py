from snowyowl import SnowyOwl as SO
#path = "/home/luc/data/LIVOX/"
path = "/home/pi/data/livox_raw/"
test=SO.SnowyOwl(outfolder=path, extrinsic=[0,0,0,0,90,-30])

test.extractDatafrombin(GSD=0.01)
