### DK Nationwide LiDAR - A short R script to generate the tile footprints file.
### Jakob Assmann j.assann@bios.au.dk 27 October 2021

import os
import subprocess
import re
import ogr

from dklidar import settings

# Status update
print('#' * 80)
print(' EcoDes-DK15 generating tile_footprint variable\n')
print(' 1. Creating output folder ...'),

# Check whether output folder exists if not create
if not os.path.exists(settings.output_folder + '/tile_footprints/'):
    os.mkdir(settings.output_folder + '/tile_footprints/')
print('Done.')

# Set variable to base the footprints on
base_var = 'dtm_10m'

# Export tile footprints using gdaltlindex
print(' 2. Exporting tile footprints using gdaltindex based on "' + base_var + '" ...'),
cmd = settings.gdaltlindex_bin + \
          settings.output_folder + '/tile_footprints/tile_footprints.shp ' + \
          settings.output_folder + '/' + base_var + '/*.tif'
subprocess.check_output(cmd, stderr=subprocess.STDOUT)
print('Done.')

# Status
print(' 3. Extracting tile_ids from file name attributes ...'),

# Load shapefile
shp_driver = ogr.GetDriverByName('ESRI Shapefile')
tile_footprints = shp_driver.Open(settings.output_folder + '/tile_footprints/tile_footprints.shp', 1)

# Open layer and get attribute name
tile_layer = tile_footprints.GetLayer()
tile_attribute_name = tile_layer.GetLayerDefn().GetFieldDefn(0).name

# Set new attribute name
new_attribute = ogr.FieldDefn('tile_id', ogr.OFTString)
new_attribute.SetWidth(8) #16 char string width
tile_layer.CreateField(new_attribute)

# Convert file names to tile_id
for feature in tile_layer:
    tile_id = feature.GetField(tile_attribute_name)
    tile_id = re.sub('.*(\d{4}_\d{3}).tif', '\g<1>', tile_id)
    feature.SetField('tile_id', tile_id)
    tile_layer.SetFeature(feature)
    feature = None
    tile_id = None

# Delete file name field
tile_layer.DeleteField(0)

# Close file connection and tidy up
tile_footprints.Destroy()
tile_layer = None
new_attribute = None
tile_attribute_name = None

# Status
print('Done.\n')
print(' Export of "tile_footprints" complete.\n')
print('#' * 80),
