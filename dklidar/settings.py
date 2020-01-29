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
# odm_folder = 'O:/ST_Ecoinformatics/B_Read/Projects/LIDAR_ANDRAS_Project/DK_nationwide_output/dk_nationwide_odms'

# ODM Mosaics and footprint
odm_mosaics_folder = wd +'/data/sample/odm_mosaics'
odm_footprint_folder = wd + '/data/sample/odm_footprint/'

# Folder for ouptuts
output_folder = wd + '/data/sample/outputs/'

# Scratch folder for temporary data storage
scratch_folder =  wd + '/scratch'

# Log folder for global log ouptus
log_folder = wd + '/log'
