import opals
import os
from dklidar import settings
from dklidar import points
import glob
import subprocess
import re
import pandas
import datetime
opals.loadAllModules()
#tile_id = '6210_570'
#tile_id = '6214_574'
tile_id = '6219_575'
## Start timer
startTime = datetime.datetime.now()
log_output = ''
return_value = ''
#-------------------------------

# Initiate return value
return_value = ''
log_output = ''

# Get working directory
wd = os.getcwd()

# Generate folder paths
out_folder = settings.output_folder + '/openness_difference'
if not os.path.exists(out_folder): os.mkdir(out_folder)

# Attempt openness difference calculation
try:

    ## Aggregate dtm mosaic to temporary file:
    # Specify gdal command
    cmd = settings.gdalwarp_bin + \
          '-tr 10 10 -r average -overwrite ' + \
          settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
          wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '

    # Execute gdal command
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aggregated dtm_10m mosaic.\n\n'

    # Initialise Opals Openness Module
    export_openness = opals.Openness.Openness()

    # Export minimum positive openness for a given cell cell with a kernel size of 50 m x 50 m
    export_openness.inFile = wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '
    export_openness.outFile = wd + '/openness_50m_min_' + tile_id + '_mosaic.tif '
    export_openness.feature = opals.Types.OpennessFeature.positive
    export_openness.kernelSize = 5  # 5 x 10 m = 50 m
    export_openness.selMode = 1
    export_openness.commons.screenLogLevel = opals.Types.LogLevel.none
    export_openness.commons.nbThreads = settings.nbThreads
    export_openness.run()

    # Export maximum positive openness for a given cell with a kernel size of 50 m x 50 m
    export_openness.inFile = wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '
    export_openness.outFile = wd + '/openness_50m_max_' + tile_id + '_mosaic.tif '
    export_openness.feature = opals.Types.OpennessFeature.positive
    export_openness.kernelSize = 5  # 5 x 10 m = 50 m
    export_openness.selMode = 2
    export_openness.commons.screenLogLevel = opals.Types.LogLevel.none
    export_openness.commons.nbThreads = settings.nbThreads
    export_openness.run()

    # Calculate difference, round and store as int16
    # Specify gdal command
    cmd = settings.gdal_calc_bin + \
          '-A ' + wd + '/openness_50m_min_' + tile_id + '_mosaic.tif ' + \
          '-B ' + wd + '/openness_50m_max_' + tile_id + '_mosaic.tif ' + \
          ' --outfile=' + wd + '/diff_openness_' + tile_id + '_mosaic.tif ' + \
          ' --calc=rint(degrees(B)-degrees(A))' + \
          ' --type=Int16 --NoDataValue=-9999'

    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' calculated difference openness. \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Obtain file extent for cropping (remove outer 50 m of mosaic)
    cmd = settings.gdalinfo_bin + wd + '/diff_openness_' + tile_id + '_mosaic.tif '

    mosaic_info = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
    upper_left = re.search("Upper *Left *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
    lower_right = re.search("Lower *Right *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
    xmin = float(upper_left.group(1)) + 50
    ymax = float(upper_left.group(2)) - 50
    xmax = float(lower_right.group(1)) - 50
    ymin = float(lower_right.group(2)) + 50

    # Remove 50 m on outer edge using gdalwarp
    cmd = settings.gdalwarp_bin + \
          '-te ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + ' -overwrite ' + \
          wd + '/diff_openness_' + tile_id + '_mosaic.tif ' + \
          wd + '/diff_openness_' + tile_id + '_mosaic_cropped.tif '

    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' cropped openness difference mosaic.\n\n'

    # Crop diff openness to original tile size (this will set all edges removed earlier to NA)
    cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          '-crop_to_cutline -overwrite ' + \
          wd + '/diff_openness_' + tile_id + '_mosaic_cropped.tif ' + \
          out_folder + '/openness_difference' + tile_id + '.tif '
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' openness calculation successful.\n\n'

    return_value = 'success'

except:
    return_value = 'opals/gdal/Error'

# Remove temporary files
try:
    os.remove(wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ')
    os.remove(wd + '/openness_50m_min_' + tile_id + '_mosaic.tif ')
    os.remove(wd + '/openness_50m_max_' + tile_id + '_mosaic.tif ')
    os.remove(wd + '/diff_openness_' + tile_id + '_mosaic.tif ')
    os.remove(wd + '/diff_openness_' + tile_id + '_mosaic_cropped.tif ')
    # and are super random files created by OPALS
    for temp_file in glob.glob(wd + '/../*' + tile_id + '_mosaic_dz._dz.tif'):
        os.remove(temp_file)
except:
    pass
#--------------
print '#' * 80

print log_output
print return_value

# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


