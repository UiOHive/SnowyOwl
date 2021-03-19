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

    
