import opals
import os
from dklidar import settings
from dklidar import points
from dklidar import dtm
from dklidar import points
import glob
import subprocess
import re
import pandas
import shutil
import datetime
#opals.loadAllModules()
tile_id = '6210_571'
## Start timer
startTime = datetime.datetime.now()
return_value = ''
log_output = ''
#-------------------------------
sea_mask = True
inland_water_mask = True
target_raster = 'D:/Jakob/dk_nationwide_lidar/data/sample/outputs/aspect/aspect_6212_579.tif'
"""
For a given target raster, this function masks all sea off the coastline of Denmark (sea_mask = True) or all inland water
bodies such as lakes or ponds (inland_water_mask = True) or both.
:param sea_mask: Boolean switch for applying sea mask
:param inland_water_mask: Boolean switch for applying the inland water mask
:param target_raster: target raster file path
:return: execution status
"""
# initiate return value and log ouptut
return_value = ''
log_output = ''

# Check whether input raster was provided
if (target_raster == ''): raise Exception('No input raster provided.')

# Apply sea mask
if (sea_mask == True):
    try:
        # Construct gdal command
        cmd = settings.gdal_rasterize_bin + \
              '-b 1 ' + '-burn -9999 ' + '-i ' + '-at '+ \
              settings.dk_coastline_poly + ' '+ \
              target_raster

        log_output = log_output + '\n' + \
                     subprocess.check_output(
                         cmd,
                         shell=False,
                         stderr=subprocess.STDOUT) + \
                     '\n' + target_raster + ' sea mask applied. \n\n '

        return_value = 'success'
    except:
        log_output = log_output + '\n' + target_raster + ' applying sea mask failed. \n\n '
        return_value = 'gdalError'

# Apply lake mask
if (inland_water_mask == True):
    try:
        # Construct gdal command
        cmd = settings.gdal_rasterize_bin + \
              '-b 1 ' + '-burn -9999 ' + '-at ' + \
              settings.dk_lakes_poly + ' ' + \
              target_raster

        log_output = log_output + '\n' + \
                     subprocess.check_output(
                         cmd,
                         shell=False,
                         stderr=subprocess.STDOUT) + \
                     '\n' + target_raster + ' inland water mask applied. \n\n '

        return_value = 'success'
    except:
        log_output = log_output + '\n' + target_raster + ' applying inland water mask failed. \n\n '
        return_value = 'gdalError'
#--------------
print '#' * 80
print log_output
# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


