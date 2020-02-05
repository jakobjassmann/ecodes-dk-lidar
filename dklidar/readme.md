## Under construction ...
## dklidar - python package with functions for processing and rasterising Denmark's Nationwide LiDAR dataset 'Punktsky' from 2014/15

## Modules
Module name | Content
--- | ---
settings.py | Global settings file
common.py | Functions for logging, process managment etc.
points.py | Functions for processing point cloud data
dtm.py |  Functions for processing the raster DTM data 

# settings.py
Global settings file with:
- paths to system excutables (python, gdal)
- paths to working directories
- paths to input / output folders

# common.py
Functions for logging process manamgnet etc.
Function name | Description
--- | ---
init_log_folder | Initialises log folder for a processing script
update_progress_df | Updates progress data frame for process managment
gather_logs | Gathers logs for a tile after a porcessing step is completed

# points.py
Functions for porcessing point cloud data
Function name | Description
--- | ---
odm_create_mosaic | Creates odm tile mosaic by importing a neighbourhood of pointclouds
odm_generate_footprint | Generates the footprint for the odm of a single tile
odm_validate_crs | validates the crs for single tile odm or neigbourhood mosaic odm

# dtm.py
Functions for processing raster DTM data
Function name | Description
--- | ---
dtm_generate_footpring | Generates footpring for a single dtm tile
dtm_creat_mosaic | Creates neigbhourhood mosaic of dtm tiles
dtm_calculate_slope | Calculates the slope from a dtm neighbourhood mosaic and crops oupput to single tile raster
