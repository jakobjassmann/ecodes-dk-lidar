# Script for debugging of dklidar module functons
# Jakob Assmann j.assmann@bio.au.dk 18 February 2021

# This script requires the input files (dtms and laz) to be stored
# in the folders specified in dklidar/settings.py
# This also applies to the binaries specified in the same file

## Preparations
print('Preparing environment\n')
# Dependencies
import os
import sys
import opals
import datetime

# Load dklidar module parts for direct access
from dklidar import points
from dklidar import dtm
from dklidar import settings
from dklidar import common

# Set temporary workdirectory
temp_wd = 'D:/Jakob/ecodes-dk-lidar/scratch/debug'

# Set temporary out directory
settings.output_folder = 'D:/Jakob/ecodes-dk-lidar/scratch/debug/output'

# Create folders if needed
for folder in [temp_wd, settings.output_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)

# Change to temporary work dir
os.chdir(temp_wd)

# Set tile_id if not set as argument (default a tile in Western Denmark)
args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
if len(args) == 0:
    tile_id = '6255_594'
else:
    tile_id = args[0]
print('Processing tile_id: ' + tile_id + '\n')

### Load opals modules
opals.loadAllModules()

# Confirm essential folders exist
if not os.path.exists(settings.wd):
    print('Working Directory ' + settings.wd + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(settings.laz_folder):
    print('laz_folder ' + settings.laz_folder + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(settings.dtm_folder):
    print('dtm_folder ' + settings.dtm_folder + ' does not exist. Exiting script...')
    exit()
# Conmfirm other folders exists and if not create them
for folder in [settings.dtm_mosaics_folder, settings.dtm_footprint_folder,
               settings.odm_folder, settings.odm_footprint_folder, settings.output_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)

## -------------------
## Start timer
print('\nStarting Timer\n')
startTime = datetime.datetime.now()

## -------------------
## Test dtm functions
print('#' * 60)
print('\nTesting DTM Functions\n')

# Generate tile footprint
print('=> Generate Tile Footprint')
print(dtm.dtm_generate_footprint(tile_id))

# Generate tile neighbourhood mosaic
print('=> Generate Neighbourhood Mosaic')
print(dtm.dtm_neighbourhood_mosaic(tile_id))

# Validate CRS
print('=> Validate CRS')
print(dtm.dtm_validate_crs(tile_id))

# Aggregate tile to 10 m
print('=> Aggregate tile to 10 m')
print(dtm.dtm_aggregate_tile(tile_id))

# Aggregate neighbourhood mosaic to 10 m
print('=> Aggregate Neighbourhood Mosaic to 10 m')
print(dtm.dtm_aggregate_mosaic(tile_id))

# Calculate slope
print('=> Calculate Slope')
print(dtm.dtm_calc_slope(tile_id))

# Calculate aspect
print('=> Calculate Aspect')
print(dtm.dtm_calc_aspect(tile_id, -1))

# Calculate heat index
print('=> Calculate Heat Index')
print(dtm.dtm_calc_heat_index(tile_id, -10))

# Calculate solar radiation
print('=> Calculate Solar Radiation')
print(dtm.dtm_calc_solar_radiation(tile_id))

# Calculate landscape openness mean
print('=> Calculate Openness Mean')
print(dtm.dtm_openness_mean(tile_id))

# Calculate landscape openness difference
print('=> Calculate Openness Difference')
print(dtm.dtm_openness_difference(tile_id))

## Calculate Kopecky TWI
print('=> Calculating Kopecky TWI')
print(dtm.dtm_kopecky_twi(tile_id))

# Remove old temp dtm files
print('=> Removing DTM temp files')
print(dtm.dtm_remove_temp_files(tile_id))

## -------------------
## Test common functions
print('\n')
print('#' * 60)
print('\nTesting Common Functions\n')

## Generate Masks
print('=> Generating Masks')
print(common.generate_water_masks(tile_id))

## -------------------
## Test points functions
print('\n')
print('#' * 60)
print('\nTesting Point Cloud Functions\n')

## Import tile to ODM
print('=> Importing ODM')
print(points.odm_import_single_tile(tile_id))

## Validate CRS of odm files
print('=> Validate CRS of ODMs')
print(points.odm_validate_crs(tile_id))

## Export footprint
print('=> Generating footprints from ODM')
print(points.odm_generate_footprint(tile_id))

## Normalise height
print('=> Normalize Height')
print(points.odm_add_normalized_z(tile_id))

## Export mean normalised height for 10 m x 10 m cell
print('=> Export Normalize Height')
print(points.odm_export_normalized_z(tile_id))

## Export canopy height
print('=> Export Canopy Height')
print(points.odm_export_canopy_height(tile_id))

## Export point counts for pre-defined intervals and classess
print('=> Export Point Counts')
print(points.odm_export_point_counts(tile_id))

## Export proportions based on point counts
print('=> Export Proportions')
print(points.odm_export_proportions(tile_id))

## Export point source information
print('=> Export Point Source Information')
print(points.odm_export_point_source_info(tile_id))

## Export amplitude mean and sd
print('=> Export Amplitude Mean and SD')
print(points.odm_export_amplitude(tile_id))

## Export date stamp
print('=> Exporting Date Stamps')
print(points.odm_export_date_stamp(tile_id))

#### Export total point count
##print('=> Export Total Point Count')
##print(points.odm_export_point_count(tile_id, 'total_point_count', -1, 50, [2,3,4,5,6,9]))

## Remove unneeded odm files
print('=> Remove ODM Temp Files')
print(points.odm_remove_temp_files(tile_id))


## -------------------
# Report time elapsed
print('\n')
print('#' * 60)
print('Debug Complete\nTime elapsed: ' + str(datetime.datetime.now() - startTime))
print("Run debug.Rmd for visual analysis")
print('\n')
