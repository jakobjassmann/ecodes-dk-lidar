# dklidar - python package 
Functions for processing and rasterising DK's nationwide LiDAR data 'Punktsky'.

## Modules

- [settings.py](#settings.py)
- [common.py](#common.py)
- [points.py](#points.py)
- [dtm.py](#dtm.py)

----

### settings.py
Global settings file with:
- paths to system excutables (python, gdal, SAGA GIS).
- paths to working directories.
- paths to input / output folders.
- paths to mask files.
- common crs as WKT string interpretable by OPALS.
- nbThreads - number of subthreads used by OPALS.
- out_cell-size - the default cell size for raster export with OPALS.
- filter strings for commonly used OPALS filters. 

[\[to top\]](#modules)

----

### common.py
Functions for logging, process management etc.

Function | Description
--- | ---
init_log_folder | Initialises log folder for a processing script.
update_progress_df | Updates progress data frame for process managment.
gather_logs | Gathers logs for a tile after a processing step is completed.
generate_water_masks | Generates sea and inland water masks for a tile. 
apply_mask | Applies water mask(s) (sea and/or in-lane water) to a raster file. Called for each raster output. Default is to apply neither of the two mask. 

[\[to top\]](#modules)

----

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
odm_export_point_count | Exports point count for a given height bracket and point class.
odm_export_point_counts | Exports point counts for a set of pre-defined height-bins and point classes.
odm_export_proportions | Exports proportions for a pre-defined set of tuples of point counts.
odm_calc_proportions | Caluclates the proportions between two point counts.
odm_export_amplitude | Exports the mean and sd of all amplitude values in the cell.
odm_export_point_source_info | Exports point source (flight line) stats for all cells in a tile.

[\[to top\]](#modules)

----

### dtm.py
Functions for processing raster DTM data.

Function | Description
--- | ---
dtm_generate_footprint | Generates footprint for a single dtm tile.
dtm_neighbourhood_mosaic | Creates neigbhourhood mosaic of dtm tiles.
dtm_aggregate_tile | Generates a 10 m aggregate of the 0.4 m dtm tiles.
dtm_calc_slope | Calculates the slope from a dtm neighbourhood mosaic, aggregates and crops oupput to a 10 msingle tile raster.
dtm_calc_aspect | Calculates the aspect from a dtm neighbourhood mosaic, aggregates and crops oupput to a 10 msingle tile raster.
dtm_calc_heat_index | Calculates heat aspect following McCune and Keon 2002. **\[Redundant?\]**
dtm_calc_solar_radiation | Calculates solar radiaiton following McCune and Keon 2002. 
dtm_openness_mean | Calculates the mean landscape openness following Yokoyama et al. 2002 for a 150 m radius.
dtm_openness_difference | Calculates the difference between min an max landscape openness following Yokoyama et al. 2002 for a 50 m radius.
dtm_saga_wetness | Calculates the SAGA wetness index for a tile from the tile mosaic with default settings (computing intense!).
dtm_saga_landscape_openness | Calclulates landscape openness following Yokoyama et al. 2002 using SAGA GIS with a search radius of 150 m (redundant).

[\[to top\]](#modules)

----
