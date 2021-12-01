# dklidar - Python modules 
Overview of the functions for processing and rasterising DK's nationwide ALS/LiDAR data 'DHM\Punktsky' contained in the dklidar modules. For further information on each function please see the docstrings and in-code comments. All functions are listed here in order of appearance in the relevant script.

## Overview

1. [Parameters in /dklidar/settings.py - global settings](#settingspy)

2. [Functions in /dklidar/common.py - functions for logging, process managment etc.](#commonpy)

3. [Functions in /dklidar/points.py - functions for processing point clouds](#pointspy)

4. [Functions in /dklidar/dtm.py - functions for processing the terrain model](#dtmpy)

----

### settings.py
Global settings file with:
- paths to system excutables (python, gdal, SAGA GIS).
- paths to working directories.
- paths to input / output folders.
- paths to mask shapefiles.
- common crs as WKT string / proj 4 interpretable by OPALS and gdal.
- nbThreads - number of subthreads used by OPALS.
- out\_cell\_size - the default cell size for raster export with OPALS. **NB: changing this variable will not affect raster manipulations with gdal. The gdal cell size values are defined in the respective functions in the dtm.py module.**
- filter strings for commonly used OPALS filters. 
- gdal version.

[\[to top\]](#overview)

----

### common.py
Functions for logging, process management etc. 

Function | Description
--- | ---
init_log_folder | Initialises a log folder and progress data frame for a given processing script based on the script name and tile ids supplied. 
update_progress_df | Updates a progress data frame for process managment. 
gather_logs | Gathers log files from a temporary working directory after processing is completed for a tile. 
generate_water_masks | Generates sea and inland water masks for a tile (at 10 m). 
apply_mask | Applies water mask(s) (sea and/or in-lane water) to a raster file. Called for each raster output. **NB: Default is to apply neither of the two mask.** 

[\[to top\]](#overview)

----

### points.py
Functions for processing point cloud data.

Function | Description
--- | ---
odm_import_single_tile | Imports the respective laz pointcloud into an ODM for a given tile. 
odm_import_mosaic | Creates an odm tile mosaic by importing all available laz files from the 3 x 3 neighbourhood of a given tile into an ODM. 
odm_generate_footprint | Exports the footprint for a single tile ODM to a shapefile. 
odm_validate_crs | Validates the crs for a single tile odm and optinally also the corresponding neigbourhood mosaic odm. 
odm_add_normalized_z | Adds a normalised height attribute to an ODM point cloud. This can either be a single tile ODM **or** a neighbourhood mosaic ODM. 
odm_export_normalized_z | Exports mean and sd rasters of the normalised height for a given tile. 
odm_export_canopy_height | Exports a canopy height raster based on the 0.95th-quantile of the normalised height attribute for all vegetation points in a given tile. 
odm_export_point_count | For a given tile, this function exports a point count raster for the specified height bin and set of point classes. 
odm_export_point_counts | Exports multiple point count rasters for multiple pre-defined sets of height-bins and point classes for a given tile using the odm_export_point_count() function. 
odm_calc_proportions | Caluclates the ratio between two point count rasters. 
odm_export_proportions | Exports a pre-defined set of proportions for a given tile using the odm_calc_proportions() function. 
odm_export_amplitude | Exports the mean and sd of the amplitude for a given tile. 
odm_export_point_source_info | Exports point source (i.e. flight line) statistics for a given tile. 
odm_export_date_stamp | Exports the date_stamp variables (min, max and mode) based on the respective statistics for the most common GPS time stamp in each 10 m x 10 m cell. 
odm_remove_temp_files | Cleans up the temp folder after point cloud processing has finished for a given tile. 

[\[to top\]](#overview)

----

### dtm.py
Functions for processing raster DTM data.

Function | Description
--- | ---
dtm_generate_footprint | Exports the footprint of a single dtm tile to a shapefile. 
dtm_neighbourhood_mosaic | Generates a dtm mosaic includig the given tile and all available tiles within it's 3 x 3 neighbourhood. 
dtm_validate_crs | For a given tiles, this function validates the crs for both the single tile dtm and the dtm neighbourhood mosaic. The neighbourhood validation can optionally be turned off. 
dtm_aggregate_tile | Exports a 10 m aggregate raster of the 0.4 m dtm for a given tile. 
dtm_aggregate_mosaic | Exports a 10 m aggregate raster of the 0.4 m dtm niehgbourhood mosaic for a given tile. 
dtm_calc_slope | For a given tile, this function calculates the slope from a dtm neighbourhood mosaic and then crops the output to the footprint of the tile. 
dtm_calc_aspect | For a given tile, this function calculates the aspect from a dtm neighbourhood mosaic and then crops the output to the footprint of the tile. 
dtm_calc_heat_index | Calculates the heat index following McCune and Keon 2002 for a given tile. 
dtm_calc_solar_radiation | Calculates the incident solar radiation following McCune and Keon 2002 for a given tile. 
dtm_openness_mean | For a given tile, this function calculates the mean landscape openness following Yokoyama et al. 2002 within a 150 m radius. 
dtm_openness_difference | For a given tile, this function calculates the difference between minmum and maximum landscape openness following Yokoyama et al. 2002 within a 50 m radius. 
dtm_kopecky_twi | Calculates the Topographic Wetness Index (TWI) following Kopecky et al. 2020 for a given tile. Calculations are carried out on the aggregated 10 m neighbourhood mosaic of the tile. The result is then cropped to the footprint of the tile. 
dtm_saga_wetness | Calculates the SAGA wetness index with default settings for a given tile (computing intense!). Calculations are carried out on the aggregated 10 m neighbourhood mosaic of the tile. The result is then cropped to the footprint of the tile. **NB: This function was not used in the generation of EcoDes-DK15!** 
dtm_saga_landscape_openness | Calclulates landscape openness following Yokoyama et al. 2002 using SAGA GIS with a search radius of 150 m (redundant) for a given tile. Calculations are carried out on the aggregated 10 m neighbourhood mosaic of the tile. The result is then cropped to the footprint of the tile. **NB: This function was not used in the generation of EcoDes-DK15!** 
dtm_remove_temp_files | Function to clean up temp folder after point cloud processing has finished for a given tile. 

[\[to top\]](#overview)

----
