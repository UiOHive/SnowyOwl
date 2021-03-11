from snowyowl import SnowyOwl as SO
#path = "/home/luc/data/LIVOX/"
path = "/home/pi/data/livox_raw/"
test=SO.SnowyOwl(outfolder=path)

test.sendDataToServer(server='lucg@vann.uio.no', username='lucg', password='', remote_path=b'/mn/vann/climaland/LIVOXFinse/')
