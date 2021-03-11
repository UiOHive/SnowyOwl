from snowyowl import SnowyOwlAcquisition as SOA
Owl=SOA.SnowyOwlAcquisition(outfolder="/home/snowyowl/data/LIVOX/")

Owl.sendDataToProcessing(server='finseflux.dyndns.org', username='snowyowl', password='finse_girod', remote_path=b'/home/snowyowl/data/LIVOX/bin/')