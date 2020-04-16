### Settings file for the DK Lidar project
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

# This file is used to provide global variables to all scripts in the DK nationwide lidar project.

# Path to python executable
python_exec_path = 'C:/Program Files/opals_nightly_2.3.2/opals/python.exe'

# Set paths to gdal executables / binaries (here we use OSGE4W64) as the OPALS gdal binaries do not work reliably
# remember the trailing spaces at the end!
# simply set to the gdal command e.g. 'gdalwarp ' if you want to use the OPALS gdal binaries (gdaldem slope won't work)

gdalwarp_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdalwarp '
gdaldem_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdaldem '
gdaltlindex_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdaltindex '
gdal_translate_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdal_translate '
gdal_calc_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdal_calc '
gdal_merge_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdal_merge '
gdaltransform_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdaltransform '
gdalinfo_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdalinfo '
gdal_rasterize_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdal_rasterize '

# Saga binary commands
saga_wetness_bin = 'C:/OSGeo4W64/apps/saga-ltr/saga_cmd.exe --cores=1 ta_hydrology 15 '
saga_openness_bin = 'C:/OSGeo4W64/apps/saga-ltr/saga_cmd.exe --cores=1 ta_lighting 5 '

### Set folder locations
# Main working directory
wd = 'D:/Jakob/dk_nationwide_lidar'

# Point cloud folder
laz_folder = wd + '/data/sample/laz/'
# DTM folder
dtm_folder = wd + '/data/sample/dtm'

# DTM mosaics and footprints
dtm_mosaics_folder = wd + '/data/sample/dtm_mosaics'
dtm_footprint_folder = wd + '/data/sample/dtm_footprints'

# ODM folder
odm_folder = wd + '/data/sample/odm/'

# ODM Mosaics and footprint
odm_mosaics_folder = wd +'/data/sample/odm_mosaics'
odm_footprint_folder = wd + '/data/sample/odm_footprint/'

# Folder for ouptuts
output_folder = wd + '/data/sample/outputs/'

# Scratch folder for temporary data storage
scratch_folder =  wd + '/scratch'

# Log folder for global log ouptus
log_folder = wd + '/log'

# Mask files
dk_coastline_poly = 'D:/Jakob/dk_nationwide_lidar/data/masks/dk_bounds_jesper_poly.shp'
dk_lakes_poly = 'D:/Jakob/dk_nationwide_lidar/data/masks/lake_mask_jesper.shp'

## Spatial reference settings

# common crs as WKT string
crs_wkt_opals = r'PROJCS["ETRS89 / UTM 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25832"]]'
crs_wkt_gdal = r'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25832"]]'

## Multiprocessing settings

# common nbThreads parameter - a throttle limiter for OPALS, ensures Opals subprocesses use only a single core
nbThreads = 1

## Processing Options

# Output cell size
out_cell_size = 10

## Filter Strings

# point filter for all three vegetation classes as OPALS WKT
veg_classes_filter = "Generic[Classification == 3 OR Classification == 4 OR Classification == 5]"
ground_and_veg_classes_filter = "Generic[Classification == 2 OR Classification == 3 OR Classification == 4 OR Classification == 5]"
all_classes = "Generic[Classification == 2 OR Classification == 3 OR Classification == 4 OR Classification == 5 OR Classification == 6 OR Classification == 9]"