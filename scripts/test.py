import opals
import os
from dklidar import settings
import glob
import subprocess
import re
import pandas
#opals.loadAllModules()
tile_id = '6210_570'

# Initiate return valule and log output
return_value = ''
log_output = ''

# get temporary work directory
wd = os.getcwd()

# Prepare output folder
out_folder = settings.output_folder + '/landscape_openness'
if not os.path.exists(out_folder): os.mkdir(out_folder)

try:

    ## Aggregate dtm mosaic to temporary file:
    # Specify gdal command
    cmd = settings.gdalwarp_bin + \
          '-tr 10 10 -r average ' + \
          settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
          wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '

    # Execute gdal command
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aggregating dtm_10m successful.\n\n'

    # Use saga gis openness module for calculating the openness in 150 m
    cmd = settings.saga_openness_bin + \
          '-DEM ' + wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ' + \
          '-POS ' + wd + '/openness_10m_' + tile_id + '_mosaic.sdat ' + \
          '-RADIUS 150 -METHOD 1'

    # Execute gdal command
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' calculating openness successful.\n\n'

    # Obtain file extent for cropping (remove outer 15 m of mosaic)
    cmd = settings.gdalinfo_bin + wd + '/openness_10m_' + tile_id + '_mosaic.sdat '

    mosaic_info = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
    upper_left = re.search("Upper *Left *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
    lower_right = re.search("Lower *Right *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
    xmin = float(upper_left.group(1)) + 150
    ymax = float(upper_left.group(2)) - 150
    xmax = float(lower_right.group(1)) - 150
    ymin = float(lower_right.group(2)) + 150

    # remove 150 m on outer edge using gdal warp
    cmd = settings.gdalwarp_bin + \
          '-te ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + ' -overwrite ' + \
          wd + '/openness_10m_' + tile_id + '_mosaic.sdat ' + \
          wd + '/openness_10m_' + tile_id + '_mosaic.tif '

    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' cropping wetness index mosaic.\n\n'

    # Convert to degrees, round and store as int16
    # Specify gdal command
    cmd = settings.gdal_calc_bin + \
          '-A ' + wd + '/openness_10m_' + tile_id + '_mosaic.tif ' + \
          ' --outfile=' + wd + '/openness_10m_' + tile_id + '_mosaic_deg.tif ' + \
          ' --calc=rint(degrees(A))' + ' --type=Int16' + ' --NoDataValue=-9999'

    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' converting dtm_10m to int16... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Crop slope output to original tile size:
    cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          '-crop_to_cutline -overwrite ' + \
          wd + '/openness_10m_' + tile_id + '_mosaic_deg.tif ' + \
          out_folder + '/openness_10m_' + tile_id + '.tif '
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aspect calculation successful.\n\n'
    return_value = 'success'
except:
    log_output = log_output + '\n' + tile_id + ' dtm_10m aggregation failed.\n\n'
    return_value = 'gdalError'

    # Write log output to log file
log_file = open('log.txt', 'a+')
log_file.write(log_output)
log_file.close()

# Remove temporary files
try:
    os.remove(wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif')
    os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.sdat')
    os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.sgrd')
    os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.prj')
    os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.mgrd')
    os.remove(wd + wd + '/openness_10m_' + tile_id + '_mosaic.tif')
    os.remove(wd + '/openness_10m_' + tile_id + '_mosaic_deg.tif')
except:
    pass


print log_output
