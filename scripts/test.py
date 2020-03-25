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
tile_id = '6210_575'
## Start timer
startTime = datetime.datetime.now()
return_value = ''
log_output = ''
#-------------------------------
"""
Returns cell by cell solar radiation following McCune and Keon 2002. Slope and aspect must have been calculated
beforehand using dtm_calc_slope and dtm_calc_aspect.
:param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
:return: execution status
"""

# The calculation of the solar radiation is a two step process
# 1) Obtain a raster with the latitude of the centre of the cell in radians
# 2) Calculate the solar radiation using the formula form McCune and Keon 2002

# initiate return value and log ouptut
return_value = ''
log_output = ''

# Get current wd
wd = os.getcwd()

# Prepare output folder
out_folder = settings.output_folder + '/solar_radiation'
if not os.path.exists(out_folder): os.mkdir(out_folder)

try:
    # 1) Create raster with latitude of the centre of a cell
    # Construct gdal command to export xyz file in utm
    dtm_file = settings.output_folder + '/slope/slope_' + tile_id + '.tif'
    out_file = wd + '/xyz_' + tile_id + '.xyz'
    cmd = settings.gdal_translate_bin + \
          ' -of xyz -co COLUMN_SEPARATOR="," -co ADD_HEADER_LINE=YES ' + \
          dtm_file + ' ' + \
          out_file
    # Execute gdal command and log
    log_output = log_output + '\n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' generated xyz. \n\n '

    # Read in xyz as a pandas dataframe
    xyz = pandas.read_csv('xyz_' + tile_id + '.xyz')
    xy = xyz[["X", "Y"]]
    xy.to_csv('xy_' + tile_id + '.csv', index=False, header=False, sep=' ')

    # Construct gdal commands to transform cell coordinates from utm to lat long
    in_file = wd + '/xy_' + tile_id + '.csv'
    out_file = 'xy_' + tile_id + '_latlong.csv'
    cmd = '(' + settings.gdaltransform_bin + ' -s_srs EPSG:25832 -t_srs WGS84 ' + \
          ' < ' + in_file + ') > ' + out_file
    # And execute the gdal command
    log_output = log_output + '\n' + \
                 subprocess.check_output(cmd, shell=True) + \
                 '\n' + tile_id + ' transformed to lat long. \n\n '

    # Load lat long file as pandas df
    xy_latlong = pandas.read_csv('xy_' + tile_id + '_latlong.csv', sep='\s+', names=['X', 'Y', 'return_status'],
                                 skiprows=1)

    # check data frames are of the same length
    if len(xyz.index) != len(xy_latlong.index):
        log_output = log_output + '\n lenght of dataframes did not match \n'
        raise Exception("")

    # Assign lat (deg) to UTM z coordinate
    xyz["Z"] = xy_latlong["Y"]
    xyz.to_csv('xyz_' + tile_id + '.xyz', index=False, header=False, sep=' ')

    # Convert back to geotiff, prepare gdal translate command
    in_file = wd + '/xyz_' + tile_id + '.xyz'
    out_file = wd + '/lat_' + tile_id + '.tif'
    cmd = settings.gdal_translate_bin + \
          ' -of GTiff -a_srs EPSG:25832 ' + \
          in_file + ' ' + \
          out_file
    # Execute command and log
    log_output = log_output + '\n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' generated lat tif. \n\n'
    # Intermediate clean up
    os.remove(wd + '/xyz_' + tile_id + '.xyz')
    os.remove(wd + '/xy_' + tile_id + '.csv')
    os.remove(wd + '/xy_' + tile_id + '_latlong.csv')
    del (xy)
    del (xy_latlong)
    del (xyz)

    ## 2) Calculate Solar radiation

    # The equation from McCune and Keon goes as follows:
    # solar radiation =  0.339 +
    #                    0.808 x cos(lat) x cos(slope) +
    #                   -0.196 x sin(lat) x sin(slope) +
    #                   -0.482 x cos(asp) x sin(slope)
    # Aspect must be foldered around the S-N line:
    # asp = 180 - |180 - asp|
    # and all values mus be in radians:
    # rad = deg * pi / 180 or using numpy simply: rad = radians(deg)
    # Finally, the result needs to be stretched by 1000 and rounded for storage as an Int16

    # Specify path to latitude raster L
    lat_file = '-L ' + wd + '/lat_' + tile_id + '.tif '

    # Specify path to slope raster as raster S
    slope_file = '-S ' + settings.output_folder + '/slope/slope_' + tile_id + '.tif '

    # Specify path to aspect raster A
    aspect_file = '-A ' + settings.output_folder + '/aspect/aspect_' + tile_id + '.tif '

    # Construct numpy equation (based on McCune and Keon 2002) and stretch by 1000 and round to nearest int.
    solar_rad_eq = 'rint(1000*(0.339+0.808*cos(radians(L))*cos(radians(S))-0.196*sin(radians(L))*sin(radians(S))-0.482*cos(radians(180-absolute(180-A)))*sin(radians(S))))'

    # Specify output path
    out_file = out_folder + '/solar_rad_' + tile_id + '.tif '

    # Construct gdal command:
    cmd = settings.gdal_calc_bin + \
          lat_file + \
          slope_file + \
          aspect_file + \
          '--outfile=' + out_file + \
          '--calc=' + solar_rad_eq + ' ' + \
          '--type=Int16 --NoDataValue=-9999 --overwrite'

    # Execute gdal command
    log_output = log_output + '\n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' calculated solar radiation. \n\n'

    # Remove latitude tif
    os.remove(wd + '/lat_' + tile_id + '.tif')
    return_value = 'success'
except:
    log_output = log_output + '\n\n' + tile_id + ' calculating solar radiation failed. \n '
    return_value = 'gdal_error'

#--------------
print '#' * 80
print log_output
# Print out time elapsed:
print '#' * 80
print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))


