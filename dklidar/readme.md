# dklidar - python package 
Functions for processing and rasterising DK's nationwide LiDAR data 'Punktsky'.

## Modules

### settings.py
Global settings file with:
- paths to system excutables (python, gdal).
- paths to working directories.
- paths to input / output folders.
- common crs as WKT string interpretable by OPALS.
- nbThreads - number of subthreads used by OPALS.
- out_cell-size - the default cell size for raster export with OPALS.
- OPALS filter strings that are often used.

### common.py
Functions for logging, process management etc.

Function nam| Description
--- | ---
init_log_folder | Initialises log folder for a processing script.
update_progress_df | Updates progress data frame for process managment.
gather_logs | Gathers logs for a tile after a processing step is completed.

### points.py
Functions for processing pointcloud data.

Function | Description
--- | ---
odm_import_single_tile | Imports a laz pointcloud file into ODM for a single tile.
odm_import_mosaic | Creates an odm tile mosaic by importing the whole neighbourhood of a tile.
odm_generate_footprint | Generates the footprint for the odm of a single tile.
odm_validate_crs | validates the crs for single tile odm or neigbourhood mosaic odm.
odm_add_normalized_z | Adds normalised height attribute to an ODM point cloud (single or mosaic).
odm_export_normalized_z | Exports mean and sd of normalised height for a given tile.
odm_export_canopy_height | Exports canopy height as normalised height attribute of the 0.95th-quantile.
odm_export_amplitude | Exports the mean and sd of all amplitude values in the cell.
odm_export_point_count | Exports point count for a fiven height bracket (defined by parameters).
odm_export_point_counts | Exports point counts for a pre-defined set of height brackets (using odm_expport_point_count). 

### dtm.py
Functions for processing raster DTM data.

Function | Description
--- | ---
dtm_generate_footprint | Generates footprint for a single dtm tile.
dtm_creat_mosaic | Creates neigbhourhood mosaic of dtm tiles.
dtm_calculate_slope | Calculates the slope from a dtm neighbourhood mosaic and crops oupput to single tile raster.
