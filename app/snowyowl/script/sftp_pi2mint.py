
'''
Script to handle files on the Pi
'''

import pysft
import argsparse
import glob
import logging
import shutil



parser = argparse.ArgumentParser(description='SFTP and archiving files')
parser.add_argument('-host','--hostname', type=str, default='192.168.10',
                    help='hostname of target computer')
parser.add_argument('-user','--username', type=str, default='livox',
                    help='username for target computer')
parser.add_argument('-sk','--path_to_key', type=str, default='~/.ssh/id_rsa',
                    help='path to local private SSH key')
parser.add_argument('-fori','--folder_ori', type=str, default='/tmp/',
                    help='path to folder containing original files, not yet transfered')
parser.add_argument('-farc','--folder_archive', type=str, default='/archive',
                    help='path to archive folder to which files are archived')
parser.add_argument('-ftar','--folder_target', type=str, default='/data/',
                    help='target folder to which transfer the files')
args = parser.parse_args()


flist_ori = glob.glob(args.folder_ori)

try:
	# Establish SSH connection
	sftp = pysftp.Connection(args.hostname, username=args.username, private_key=args.path_to_key)
	try: 
		# goes to target directory
		sftp.Connection.cd(args.folder_target)
		for file in flist_ori:
			# Check if file exists
			if sftp.Connection.exist(file):
				logging.info(file + 'already exist in ' + args.unsername + '@' + args.hostname)
			else:
				# send file if not existing in target folder
				sftp.put(file, preserve_mtime=True)
				logging.info(file + ' copied to ' + args.unsername + '@' + args.hostname)

				# move file to archive folder
				shutil.move(file, args.folder_archive + file.split('/')[-1])
				logging.info(file + ' archived')	

	except:
		logging.error('Target folder not existing')

except:
	logging.error('SFTP Connection to ' + args.username + '@' + args.hostname + ' not established')