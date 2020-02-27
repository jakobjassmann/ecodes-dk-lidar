import opals
import os
from dklidar import settings
import glob
import subprocess
import pandas
#opals.loadAllModules()
tile_id = '6210_570'

# initiate return value and log ouptut
return_value = ''
log_output = ''

# Get current wd
wd = os.getcwd()

try:
    # 1) Create raster with latitude of the centre of a cell
    #Construct gdal command to export xyz file in utm

    dtm_file = settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif'
    out_file = wd + '/xyz_' + tile_id + '.xyz'
    cmd = settings.gdal_translate_bin + ' -of xyz -co COLUMN_SEPARATOR="," -co ADD_HEADER_LINE=YES ' + \
          dtm_file + ' ' + \
          out_file
    print cmd
    log_output = tile_id + ' generating xyz... \n ' + subprocess.check_output(cmd, shell=False,
                                                                                 stderr=subprocess.STDOUT)

    # Read in xyz as a pandas dataframe
    xyz = pandas.read_csv('xyz_' + tile_id + '.xyz')
    xy = xyz[["X", "Y"]]
    xy.to_csv('xy_' + tile_id + '.csv', index=False, header=False, sep=' ')

    # Construct gdal commands to transform cell coordinates from utm to lat long
    in_file = wd + '/xy_' + tile_id + '.csv'
    out_file ='xy_' + tile_id + '_latlong.csv'
    cmd = '(' + settings.gdaltransform_bin + ' -s_srs EPSG:25832 -t_srs WGS84 ' + \
          ' < ' + in_file + ') > ' + out_file
    # And execute the gdal command
    log_output = tile_id + ' transforming to lat long... \n ' + subprocess.check_output(cmd, shell=True)

    # Load lat long file
    xy_latlong = pandas.read_csv('xy_' + tile_id + '_latlong.csv', sep='\s+', names =['X','Y','return_status'], skiprows=1)

    # check data frames are of the same lenght
    if len(xyz.index) != len(xy_latlong.index):
        log_output = log_output + '\n lenght of dataframes did not match \n'
        raise Exception("")

    # Assign lat (deg) to UTM z coordinate
    xyz["Z"] = xy_latlong["Y"]
    print xyz.head()
    print xyz.tail()
    xyz.to_csv('xyz_' + tile_id + '.xyz', index=False, header=False, sep=' ')

    # Convert back to geotiff
    in_file = wd + '/xyz_' + tile_id + '.xyz'
    out_file = wd + '/lat_' + tile_id + '.tif'
    cmd = settings.gdal_translate_bin + ' -of GTiff -a_srs EPSG:25832 ' + \
          in_file + ' ' + out_file
    print cmd
    log_output = tile_id + ' generating xyz... \n ' + subprocess.check_output(cmd, shell=False,
                                                                                 stderr=subprocess.STDOUT)
except:
    log_output = tile_id + ' generating xyz failed. \n '
    return_value = 'gdal_error'

# Write log output to log file
log_file = open('log.txt', 'a+')
log_file.write(log_output)
log_file.close()

print(return_value)