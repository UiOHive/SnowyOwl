# Script to push newly acquired file to snowyowl for further processing
FILES=/mnt/LivoxDrive/tmp/*

for f in $FILES
do
	echo "Processing $f file..."
	scp $f snowyowl@192.168.13.36:/home/snowyowl/data/livox/bin
	# uncomment if wanna keep all raw data. WARNING check disk capacity for duration
	#mv  $f /mnt/LivoxDrive/archive/

	# remove raw file after file has been sent
	rm $f
done
