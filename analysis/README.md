# Analysis README
S. Filhol, June 2021

## Conversion to compress NETCDF
- compute `gdal_fillna()` on `min` band
- store daily all raster into a compressed NETCDF. See file `geotiff2netcdf.py`

## Notes
See Obsidian notes `Continuous Lidar Monitoring.md`, and `livox_lidar_notes.md`


## Animation
Produce videos of the surface changes. See the file `animate_snow.py`



## Compute age of snow
Develop a routine that can compute the age of the snow at the surface. Create a 3D volume. When the snow goes up tick time in voxel. If snow goes down bring voxel to nan. This adds a 4d dimension, or needs to be computed within a for loop and no saved (if memory prb).

This age matrix can be for the  whole snowpack or just the surface. The reference coordinate system should be set fixed. NaNs where no snow, and then each voxel is a timer


## Issues
- There seem to be prb de timestamo, at least for the first test. Check the DEMs are named properly