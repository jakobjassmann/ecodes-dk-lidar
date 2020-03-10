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
import datetime
opals.loadAllModules()
tile_id = '6210_572'
## Start timer
startTime = datetime.datetime.now()
return_value = ''
log_output = ''
#-------------------------------
points.odm_import_single_tile(tile_id)
points.odm_export_amplitude(tile_id)
#--------------
print '#' * 80
print log_output
# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


