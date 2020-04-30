import opals
import os
from dklidar import settings
from dklidar import points
from dklidar import dtm
from dklidar import points
from dklidar import points
import glob
import subprocess
import re
import pandas
import shutil
import datetime
from dklidar import common
opals.loadAllModules()
tile_id = '6211_579'
## Start timer
startTime = datetime.datetime.now()
return_value = ''
log_output = ''
#-------------------------------
print points.odm_import_single_tile(tile_id)
print points.odm_validate_crs(tile_id)
print points.odm_add_normalized_z(tile_id)
print points.odm_generate_footprint(tile_id)
print points.odm_export_canopy_height(tile_id)
#points.odm_export_point_counts(tile_id)
#points.odm_export_proportions(tile_id)
#--------------
print '#' * 80
print log_output
# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


