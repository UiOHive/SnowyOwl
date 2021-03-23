# Script to push newly acquired file to snowyowl for further processing

# USER SETTINGS
CONFIG_FILE=example_config.ini
TRANSFER="transfer_acq2proc"
delete_transfered_file=TRUE
reboot_system=TRUE


# Pull information from config_file
DATA_FOLDER=$(sed -n "/^\[$TRANSFER\]/ { :l /^send_folder[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
PCL_FILES=$DATA_FOLDER*
TARGET_MACHINE=$(sed -n "/^\[$TRANSFER\]/ { :l /^target_ssh_user[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
TARGET_IP=$(sed -n "/^\[$TRANSFER\]/ { :l /^target_IP_address[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
TARGET_FOLDER=$(sed -n "/^\[$TRANSFER\]/ { :l /^target_folder[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
ARCHIVE_FOLDER=$(sed -n "/^\[$TRANSFER\]/ { :l /^archive_folder[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)

cd $DATA_FOLDER

for f in $PCL_FILES
do
  echo "Processing $f file..."
  scp $f $TARGET_MACHINE@$TARGET_IP:$TARGET_FOLDER
  # uncomment if wanna keep all raw data. WARNING check disk capacity for duration


  if [ $delete_transfered_file ]
  then
    # remove raw file after file has been sent
    rm $f
  else
    mv  $f $ARCHIVE_FOLDER
  fi
done

if [reboot_system]
then
 sudo reboot
fi
