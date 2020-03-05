import opals
import os
from dklidar import settings
import glob
import subprocess
import re
import pandas
import datetime
opals.loadAllModules()
tile_id = '6210_570'
## Start timer
startTime = datetime.datetime.now()

#-------------------------------
# Initiate return value
return_value = ''
log_output = ''

# Get working directory
wd = os.getcwd()

# Generate folder paths
out_folder = settings.output_folder + '/landscape_openness'
if not os.path.exists(out_folder): os.mkdir(out_folder)

# Export canopy height
try:

    ## Aggregate dtm mosaic to temporary file:
    # Specify gdal command
    cmd = settings.gdalwarp_bin + \
          '-tr 10 10 -r average ' + \
          settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
          wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ' + ' -overwrite'

    # Execute gdal command
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aggregating dtm_10m mosaic successful.\n\n'

    # Initialise Opals Openness Module
    export_openness = opals.Openness.Openness()

    # Export positive openness for a given cell cell with a search radius of 150 m (15 cells)
    export_openness.inFile = wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '
    export_openness.outFile = wd + '/openness_150m_' + tile_id + '_mosaic.tif '
    export_openness.feature = opals.Types.OpennessFeature.positive
    export_openness.kernelSize = 10  # 5 x 50 m
    export_openness.selMode = 0
    export_openness.commons.screenLogLevel = opals.Types.LogLevel.none
    export_openness.commons.nbThreads = settings.nbThreads
    export_openness.run()

    # Calculate difference, round and store as int16
    # Specify gdal command
    cmd = settings.gdal_calc_bin + \
          '-A ' + wd + '/openness_150m_' + tile_id + '_mosaic.tif ' + \
          ' --outfile=' + wd + '/landscape_openness_' + tile_id + '_mosaic.tif ' + \
          ' --calc=rint(degrees(A))' + ' --type=Int16' + ' --NoDataValue=-9999'

    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' converting and rounding to degreees. \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Obtain file extent for cropping (remove outer 50 m of mosaic)
    cmd = settings.gdalinfo_bin + wd + '/landscape_openness_' + tile_id + '_mosaic.tif '

    mosaic_info = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
    upper_left = re.search("Upper *Left *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
    lower_right = re.search("Lower *Right *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
    xmin = float(upper_left.group(1)) + 150
    ymax = float(upper_left.group(2)) - 150
    xmax = float(lower_right.group(1)) - 150
    ymin = float(lower_right.group(2)) + 150

    # remove 50 m on outer edge using gdalwarp
    cmd = settings.gdalwarp_bin + \
          '-te ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + ' -overwrite ' + \
          wd + '/landscape_openness_' + tile_id + '_mosaic.tif ' + \
          wd + '/landscape_openness_' + tile_id + '_mosaic_cropped.tif '

    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' cropping landscape openness mosaic finished.\n\n'

    # Crop diff openness to original tile size (this will set all edges removed earlier to NA)
    cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          '-crop_to_cutline -overwrite ' + \
          wd + '/landscape_openness_' + tile_id + '_mosaic_cropped.tif ' + \
          out_folder + '/landscape_openness_' + tile_id + '.tif '
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' landscape openness calculation successful.\n\n'

    return_value = 'success'

except:
    return_value = 'opals/gdal/Error'

try:
    os.remove(wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ')
    os.remove(wd + '/openness_150m_' + tile_id + '_mosaic.tif ')
    os.remove(wd + '/landscape_openness_' + tile_id + '_mosaic.tif ')
    os.remove(wd + '/landscape_openness_' + tile_id + '_mosaic_cropped.tif ')
except:
    pass
#--------------
print '#' * 80
#print log_output
# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


