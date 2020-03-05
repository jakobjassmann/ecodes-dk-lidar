import opals
import os
from dklidar import settings
import glob
import subprocess
import re
import pandas
import datetime
#opals.loadAllModules()
tile_id = '6212_573'
## Start timer
startTime = datetime.datetime.now()

#-------------------------------

# Initiate return valule and log output
return_value = ''
log_output = ''

# get temporary work directory
wd = os.getcwd()

# Prepare output folder
out_folder = settings.output_folder + '/wetness_index'
if not os.path.exists(out_folder): os.mkdir(out_folder)

try:
    # Calculate wetness index at DTM scale
    cmd = settings.saga_wetness_bin + '-DEM ' + \
          settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
          '-TWI ' + wd + '/wetness_index_' + tile_id + '_mosaic.tif'
    log_output = tile_id + ' wetness index calculation... \n ' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Crop output to original tile size:
    cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          '-tr 10 10 -r med ' + '-crop_to_cutline -overwrite ' + \
          wd + '/wetness_index_' + tile_id + '_mosaic.sdat ' + \
          wd + '/wetness_index_' + tile_id + '.tif '

    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' cropping wetness index mosaic.\n\n'
    return_value = 'success'

    # Set input file path
    in_file = wd + '/wetness_index_' + tile_id + '.tif '
    # Set output file path
    out_file = out_folder + '/wetness_index_' + tile_id + '.tif '

    # Stretch to by 1000, round and convert to int 16
    # Construct gdal command:
    cmd = settings.gdal_calc_bin + '-A ' + wd + '/wetness_index_' + tile_id + '.tif ' + '--outfile=' + out_file + \
          ' --calc=rint(1000*A) --type=Int16' + ' --NoDataValue=-9999 --overwrite'

    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' rounding and converting to integer... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

except:
    log_output = log_output + '\n' + tile_id + ' wetness index calculation failed.\n\n'
    return_value = 'gdalError'

# Write log output to log file
log_file = open('log.txt', 'a+')
log_file.write(log_output)
log_file.close()

# Remove temporary file
try:
    os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.sdat ')
    os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.prj ')
    os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.sgrd ')
    os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.mgrd ')
    os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.tif ')
    os.remove(wd + '/wetness_index_' + tile_id + '.tif ')
except:
    pass

#--------------
print '#' * 80
print log_output
# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


