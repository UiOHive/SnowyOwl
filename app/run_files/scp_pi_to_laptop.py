from snowyowl import SnowyOwlAcquisition as SOA
Owl=SOA.SnowyOwlAcquisition(outfolder="/mnt/LivoxDrive/")

Owl.sendDataToProcessing(server='192.168.13.36', username='snowyowl', remote_path=b'/home/snowyowl/data/LIVOX/bin/')
