import opals
import os
from dklidar import settings
import glob
import subprocess
import pandas
#opals.loadAllModules()
tile_id = '6210_570'

"""
Aggregates the 0.4 m DTM to 10 m size for final output and other calculations.
:param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
:return: execution status
"""

# Initiate return valule and log output
return_value = ''
log_output = ''

# get temporary work directory
wd = os.getcwd()

# Prepare output folder
out_folder = settings.output_folder + '/dtm_10m'
if not os.path.exists(out_folder): os.mkdir(out_folder)

try:
    ## Aggregate dtm to temporary file:
    # Specify gdal command
    cmd = settings.gdalwarp_bin + \
          '-tr 10 10 -r average ' + \
          settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif ' + \
          wd + '/dtm_10m_' + tile_id + '_float.tif '
    print cmd
    # Execute gdal command
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aggregating dtm_10m successful.\n\n'

    out_file = out_folder + '/dtm_10m_' + tile_id + '.tif'

    # Multiply by 100 and store as int16
    # Specify gdal command
    cmd = settings.gdal_calc_bin + '-A ' + wd + '/dtm_10m_' + tile_id + '_float.tif ' + ' --outfile=' + out_file + \
          ' --calc=100*A' + ' --type=Int16' + ' --NoDataValue=-9999'
    print cmd
    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' converting dtm_10m to int16... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

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
    os.remove(wd + '/dtm_10m_' + tile_id + '_float.tif')
except:
    pass

print log_output