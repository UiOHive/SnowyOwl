# Script to push newly acquired file to snowyowl for further processing

# USER SETTINGS
CONFIG_FILE=config.ini
TRANSFER="transfer_proc2storage"
delete_transfered_file=true
reboot_system=false


# Pull information from config_file
DATA_FOLDER=$(sed -n "/^\[$TRANSFER\]/ { :l /^send_folder[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
PCL_FILES=$DATA_FOLDER*
TARGET_USER=$(sed -n "/^\[$TRANSFER\]/ { :l /^target_ssh_user[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
TARGET_SERVER=$(sed -n "/^\[$TRANSFER\]/ { :l /^target_server[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
TARGET_FOLDER=$(sed -n "/^\[$TRANSFER\]/ { :l /^target_folder[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)
ARCHIVE_FOLDER=$(sed -n "/^\[$TRANSFER\]/ { :l /^archive_folder[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./$CONFIG_FILE)


cd $DATA_FOLDER
if [[ "$DATA_FOLDER" == "$(pwd)/" ]];
then
for f in $PCL_FILES
do
  echo "Processing $f file..."
  scp $f $TARGET_USER@$TARGET_SERVER:$TARGET_FOLDER
  # uncomment if wanna keep all raw data. WARNING check disk capacity for duration


  if $delete_transfered_file;
  then
    # remove raw file after file has been sent
    rm $f
  else
    mv  $f $ARCHIVE_FOLDER
  fi
done
fi

if $reboot_system;
then
 sudo reboot
fi
