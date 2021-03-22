# SnowyOwl
Snow lidar time-lapse for snow surface morphology and wind transport flux estimate

All hardware design available in the folder `hardware`, and and Python App in `app`.

## Python App

### Code Structure

0. Objectives:
  - 1m2 subsample column vertical from lidar stored in `.las`
  - DEM of the swath (if possible 10cm) stored in netcdf (use
1. 5-10s acquisition (Python SDK Pylivox):
2. derive subsample 1m2 column every 10-20s
3. derive DEM every 10min
4. trash initial `.las` record
5. Pi pushing derived data via SCP or FTP to UiO

**IMPORTANT:** automatic startup

### Install Environment

#### Acquisition Computer
After installing Raspbian on microSD follow these steps:
```sh
# Clone SnowyOwl repository
mkdir github
cd github
git clone ...
cp SnowyOwl/appV2/example_config.ini ~/config.ini

cd
nano config.ini
# Add the proper config settings

# Install miniconda
conda create -n livox_env
conda activate livox_env
conda install pandas


crontab -e

# add the following two lines to the Crontab

# Set ssh connection to Processing computer
ssh-keygen
ssh-copy-id <user>@<processing_machine>

# Allow to reboot computer with no password (as connection to lidar is unstable after couple hours)
# Reboot after each scp file transfer
sudo visudo -f /etc/sudoers.d/reboot_privilege`
#add line : 
<user> ALL=(root) NOPASSWD: /sbin/reboot

# Create two folders one for temporary storage of data and one for archiving
mkdir <project_path>/tmp
mkdir <project_path>/archive
```
#### Processing Computer
```sh
# Clone SnowyOwl repository
mkdir github
cd github
git clone ...
cp SnowyOwl/appV2/example_config.ini ~/config.ini

cd
nano config.ini
# Add the proper config settings

crontab -e

# add the following two lines to the Crontab

# Set ssh connection to Processing computer
ssh-keygen
ssh-copy-id <user>@<storage_machine>

# Create two folders one for temporary storage of data and one for archiving
mkdir <project_path>/las_raw
mkdir <project_path>/las_referenced
mkdir <project_path>/OUTPUT
mkdir <project_path>/archive
```


## TODO
- Luc & Simon: 
  - Python appV2
    - Acquisisition
      - TEST code
      - add logging lines
      - add logic to check folders exist
    - Processing:
      - add logic to check folders exist `/las_raw, /las_referenced, /OUTPUT, ...`
      - implement pcl processing to DEM with pandas and store as netcdf
      - add logging lines
      
    - File transfer
      - grab bash script from Pi. See if bash can read config.ini to get settings
  - Python app:

    - [ ] reorganize the app to be cleaner
      - [ ] Aquisition code by the Pi
      - [ ] File transfer to Processing machine
      - [ ] Processing code for computing DEMs and cropped PCL
      - [ ] File transfer to UiO storage
      - [ ] possibility to adjust Aquisition on the fly (via config)
    - [ ] create a single config file for the whole stack and use [configparser](https://docs.python.org/3/library/configparser.html)
    - [ ] configure SSH to Vann or to Latice server directly
    - [ ] solve disconnect problem Pi to Livox (breaks after 2hrs)
    - [ ] define accurately the rotation matirx to apply. Crop z-range for potential crazy outliers
    - [ ] refine data to produce:
      - [ ] 10 minute DEM -> store in netcdf file if possible (with xarray)
      - [ ] 20s PCL crop (1*1m) including the sensor center
      - [ ] 1hr full PCL 

    
