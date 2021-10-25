# SnowyOwl
S. Filhol and L.  Girod. 2021
See the file `LICENSE` for copyrights (MIT License)

Snow lidar time-lapse for snow surface morphology and wind transport flux estimate.

## Description
Snowyowl is a set of tools written in Python to acquire and process point clouds from [Livox lidar](https://www.livoxtech.com/horizon) Horizon. The setup consists of one lidar Livox Horizon, one Raspberry Pi, and one Desktop machine. The Pi acquires the raw data stored in `.bin` files. It pushes the data then to the desktop computer. The Desktop computer:
1. converts the `.bin` point clouds into `.las`
2. crop the `.las` and store the cropped pointcloud into `.laz` compressed file
3. compute a raster from the point cloud with bands (min, max, mean, count, ) using the library [pdal](https://pdal.io)
4. interpolate the min raster with [gdal fillnodata](https://gdal.org/programs/gdal_fillnodata.html)
5. combine and compress daily the raster into single netcdf files
6. *There is an option to push the data to an external server via scp.*

The folder `/analysis` contains juptyer notebooks and python script to process and post process the data. For instance how to create animations of the snow surface.

The lidar sensor, the Pi, and the desktop machine are assumed to be on the same local network as they need high bandwidth/speed to transfer data, and require the SSH protocol to communicate.

All hardware design available in the folder `hardware`, and Python App in `appV2`.


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
conda create -f conda_env_acquire
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

sudo apt-get install fail2ban

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


# fail2ban is a piece of software to ban IP addresses that tries over and over to ping open ports (for instance port 22 open here)
sudo apt-get install fail2ban
# see how to configure
```

#### Lidar Power Setup
The lidar power (12V 3A) can be controlled by a relay on the Raspberry Pi. By default the relay is connected to power the lidar. The lidar power is connected to Relay 1.

To turn the lidar off:
```python
from relay_lib_seed import *

relay_on(1)
# apply a delay

relay_off(1)

```

The librayr is not installed in an environment so `cd git/seeed-studio-relay-board` to find the python files.

This exposes a series of functions to your application:
-   relay_on(int_value) - Turns a single relay on. Pass an integer value between 1 and 4 (inclusive) to the function to specify the relay you wish to turn on. For example: relay_on(1) will turn the first relay (which is actually relay 0 internally) on.
-   relay_off(int_value) - Turns a single relay on. Pass an integer value between 1 and 4 (inclusive) to the function to specify the relay you wish to turn on. For example: relay_on(4) will turn the first relay (which is actually relay 3 internally) off.
-   relay_all_on() - Turns all of the relays on simultaneously.
-   relay_all_off() - Turns all of the relays off simultaneously.



## TODO:
- [ ] Send email if no tif to compile into NetCDF at end of day (as a daily failure check)
- [ ] change logic of pi reboot. Find out if rebooting lidar can solve the connection problem (currently rebooting every 30min)
- [ ] htere seem to be prb de timestamo, at least for the first test. Check the DEMs are named properly. Check this out
- [ ] find out where the Campbell laser is pointing out to recenter the pointcloud crop on it
- [ ] find out how to do some logging within the functions outside the main statemment of the scripts. See this [stackoverflow](https://stackoverflow.com/questions/5974273/python-avoid-passing-logger-reference-between-functions#5974391)
- [ ] find out more aboute the ~2m band with no point in the point clouds right above the surface
- [ ] figure out rotation matrix as it is rather empirical at the moment
- [ ] Check when OpenPyLivox will upgrade code to be compatible with laspy v2 that it can export `.laz` directly. Change code accordingly then
- [ ] install fail2ban on the Pi. Check if echobase has banned IPs


    
