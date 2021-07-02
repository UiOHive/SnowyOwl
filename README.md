# SnowyOwl
S. Filhol and L.  Girod. 2021

Snow lidar time-lapse for snow surface morphology and wind transport flux estimate.

## Description
Snowyowl is a set of tools written Python to acquire and process point clouds from [Livox lidar](https://www.livoxtech.com/horizon) Horizon. The setup consists of one lidar Livox Horizon, one Raspberry Pi, and one Desktop machine. The Pi acquires the raw data stored in `.bin` files. It pushes the data then to the desktop computer. The Desktop computer:
1. converts the `.bin` point clouds into `.las`
2. crop the `.las` and store the cropped pointcloud into `.laz` compressed file
3. compute a raster from the point cloud with bands (min, max, mean, count, ) using the library [pdal](https://pdal.io)
4. interpolate the min raster with [gdal fillnodata](https://gdal.org/programs/gdal_fillnodata.html)
5. combine and compress daily the raster into single netcdf files

All hardware design available in the folder `hardware`, and and Python App in `appV2`.


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

### Install Environments for Acquisition and Processing

#### Acquisition Computer
After installing Raspbian on microSD follow these steps:
```sh
# Set ssh connection to Processing computer
ssh-keygen
ssh-copy-id <user>@<processing_machine>

# Clone SnowyOwl repository
mkdir github
cd github
git clone https://github.com/ArcticSnow/OpenPyLivox
git clone https://github.com/UiOHive/SnowyOwl
cp SnowyOwl/appV2/example_config.ini ~/config.ini

cd
nano config.ini
# Add the proper config settings

# Install miniconda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash

# create a Python VE
conda create -n livox_env
conda activate livox_env
conda install pandas ipython
pip install github/OpenPyLivox

crontab -e
# add the following line to the Crontab to transfer files every 30 minutes:
----
# Push raw livox file in tmp to snowyowl machine and archive file to SSD
26,56 * * * * bash /home/livoxpi/git/SnowyOwl/appV2/scp_transfer_file_acq2proc.sh
#1,31 * * * * /home/livoxpi/miniconda3/envs/livoxenv/bin/python /home/livoxpi/git/SnowyOwl/appV2/acquisition.py -cf /home/livoxpi/config.ini
@reboot sleep 30 && /home/livoxpi/miniconda3/envs/livoxenv/bin/python /home/livoxpi/git/SnowyOwl/appV2/acquisition.py -cf /home/livoxpi/config.ini
----


# Create two folders one for temporary storage of data and one for archiving
mkdir <project_path>/tmp
mkdir <project_path>/archive

# Allow to reboot computer with no password (as connection to lidar is unstable after couple hours)
# Reboot after each scp file transfer
sudo visudo -f /etc/sudoers.d/reboot_privilege`
#add line : 
<user> ALL=(root) NOPASSWD: /sbin/reboot
```

#### Processing Computer
```sh

# Set ssh connection to Processing computer
ssh-keygen
ssh-copy-id <user>@<storage_machine>

# Clone SnowyOwl repository
mkdir git
cd git
git clone https://github.com/UiOHive/SnowyOwl
cp SnowyOwl/appV2/example_config.ini ~/config.ini

# Install miniconda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash

# create a Python VE
conda env create -f conda_env_process.yml
conda activate snowyowl

# install manually openpylivox
cd git
git clone git@github.com:ArcticSnow/OpenPyLivox.git
pip install -e OpenPyLivox/.

cd
nano config.ini
# Add the proper config settings

crontab -e
# add the following two lines to the Crontab
0 4 * * * /home/lucg/miniconda3/envs/snowyowl/bin/python /home/lucg/git/SnowyOwl/appV2/geotiff2netcdf.py -cf /home/lucg/config.ini
5,35 * * * * /home/lucg/miniconda3/envs/snowyowl/bin/python /home/lucg/git/SnowyOwl/appV2/process_pcl.py -cf /home/lucg/config.ini

# Create two folders one for temporary storage of data and one for archiving
mkdir <project_path>/las_raw
mkdir <project_path>/las_crop
mkdir <project_path>/las_referenced
mkdir <project_path>/OUTPUT
mkdir <project_path>/archive
mkdir <project_path>/TIFs

```


## TODO:
- [ ] change logic of pi reboot. Find out if rebooting lidar can solve the connection problem (currently rebooting every 30min)
- [ ] find out where the Campbell laser is pointing out to recenter the pointcloud crop on it
- [ ] find out how to do some logging within the functions outside the main statemment of the scripts. See this [stackoverflow](https://stackoverflow.com/questions/5974273/python-avoid-passing-logger-reference-between-functions#5974391)
- [ ] find out more aboute the ~2m band with no point in the point clouds right above the surface
- [ ] figure out rotation matrix as it is rather empirical at the moment
- [ ] Check when OpenPyLivox will upgrade code to be compatible with laspy v2 that it can export `.laz` directly. Change code accordingly then


    
