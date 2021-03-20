from snowyowl import SnowyOwl as SO
test=SO.SnowyOwl(outfolder="/home/snowyowl/data/livox/", extrinsic=[0,0,0,0,90,-20])

test.extractDatafrombin(GSD=0.05)
