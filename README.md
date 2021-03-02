# Snowdar
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

- install Raspbian

## TODO
- Luc & Simon: 
  - Python app
  - Raspberry pi setup:
    - SSH/SCP config
    - IP adress via DynDNS
- John & Simon:
  - Mounting brackets, 
  - power supply, 
  - ethernet connection 
