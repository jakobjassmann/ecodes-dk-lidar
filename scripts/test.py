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
#opals.loadAllModules()
tile_id = '6210_570'
## Start timer
startTime = datetime.datetime.now()
return_value = ''
log_output = ''
#-------------------------------
dtm.dtm_neighbourhood_mosaic(tile_id)
dtm.dtm_generate_footprint(tile_id)
dtm.dtm_calc_slope(tile_id)
dtm.dtm_calc_aspect(tile_id)
dtm.dtm_calc_solar_radiation(tile_id)
#--------------
print '#' * 80
print log_output
# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


