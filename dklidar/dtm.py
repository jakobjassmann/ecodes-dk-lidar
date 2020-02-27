### Functions for DTM raster file handling for DK Lidar project
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

import os
import subprocess
import multiprocessing
import re
import pandas

from typing import Union

from dklidar import settings

#### Function definitions

## Generate tile footprint
def dtm_generate_footprint(tile_id):
    """
    Generates a footprint file using gdal
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return execution status
    """

    # Initiate return value and log output
    return_value = ''
    log_output = ''

    try:
        cmd = settings.gdaltlindex_bin + \
          settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif'
        cmd_return = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        log_output = log_output + '\n' + tile_id + ' footprint generation... \n' + cmd_return + \
                     '\n' + tile_id + ' successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' footprint generation failed. \n' + cmd_return
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Change back to original working directory
    os.chdir(wd)

    return return_value


## Create neighbourhood mosaic
def dtm_mosaic_neighbours(tile_id):
    """
    Generates a tif mosaic with all existing 8 neighbouring cells
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    input_folder: folder location for input dtm files. ouput_folder ouput location for dtm mosaics.
    :return: execution status
    """

    # Initate return value
    return_value = ''

    # Generate temporay wd for parallel worker, this will allow for smooth logging and opals sessions to run in parallel
    wd = os.getcwd()
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = settings.scratch_folder + '/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)

    # Retrieve row and col numbers for the current tile_id
    center_row = int(re.sub('(\d+)_\d+', '\g<1>', tile_id))
    center_col = int(re.sub('\d+_(\d+)', '\g<1>', tile_id))

    # Determine row and column numbers for tiles in the 3 x 3 window
    rows_to_load = [center_row - 1, center_row, center_row + 1]
    cols_to_load = [center_col - 1, center_col, center_col + 1]

    # Generate list of tile_ids for tiles to load
    tiles_to_load = []
    for row in rows_to_load:
        for col in cols_to_load:
            tile_to_load = str(row) + '_' + str(col)
            tiles_to_load.extend([tile_to_load])

    # Prep filenames and check if files exists:
    tile_file_names = []
    for tile_to_load in tiles_to_load:
        tile_file_name = settings.dtm_folder + '/DTM_1km_' + tile_to_load + '.tif'
        if os.path.exists(tile_file_name):
            tile_file_names.append(tile_file_name)
    n_neighbours = len(tile_file_names)
    tile_file_names = ' '.join(tile_file_names)

    if n_neighbours == 9:
        log_output = tile_id + ' mosaicing...\n' + 'Number of neighbours = ' + str(n_neighbours) + '. Complete!\n'
    else:
        log_output = tile_id + ' mosaicing...\n' + 'Warning! Number of neighbours = ' + str(n_neighbours) + '. Incomplete. Edge effects possible!\n'

    # Construct command:
    cmd = settings.gdalwarp_bin + ' ' + tile_file_names + ' ' + \
        settings.dtm_mosaics_folder + '/dtm_mosaic' + \
        tile_id + '.tif '

    # Execute command as subprocess and return message:
    try:
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        log_output = log_output + tile_id + ' successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + tile_id + ' failed.\n\n'
        return_value = "gdalError"

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Change back to original working directory
    os.chdir(wd)

    return return_value


## Calculcate heat index
def dtm_calc_heat_index(tile_id):
    """
    Calculates the aspect from DTM neighbourhood mosaic and crops to original tile_size
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Intialise return value and log
    return_value = ''
    log_output = ''

    # Calculate slope parameter
    cmd = settings.gdaldem_bin + ' aspect ' + \
        settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
        settings.output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif '
    log_output = log_output + '\n' + tile_id + ' slope calculation... \n ' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Croping slope output to original tile size:
    cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          '-crop_to_cutline -overwrite ' + \
          settings.output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif ' + \
          settings.output_folder + '/dtm_slope/slope_' + tile_id + '.tif '
    log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 tile_id + ' successful.\n\n'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    os.remove(settings.output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif ')

def dtm_calc_solar_radiation(tile_id):
    """
    Returns cell by cell solar radiation following McCune and Keon 2002. Slope and aspect must have been calculated
    beforehand using dtm_calc_slope and dtm_valc_aspect
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # The calculation of the solar radiation is a thre step process
    # 1) Obtain a raster with the latitude of the centre of the cell in radians
    # 2) Fold the aspect around the North-South line (see McCune and Keon).
    # 3) Calculate the solar radiation using the formula form McCune and Keom

    # initiate return value and log ouptut
    return_value = ''
    log_output = ''

    # Get current wd
    wd = os.getcwd()

    try:
        # 1) Create raster with latitude of the centre of a cell
        # Construct gdal command to export xyz file in utm

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
        out_file = 'xy_' + tile_id + '_latlong.csv'
        cmd = '(' + settings.gdaltransform_bin + ' -s_srs EPSG:25832 -t_srs WGS84 ' + \
              ' < ' + in_file + ') > ' + out_file
        # And execute the gdal command
        log_output = tile_id + ' transforming to lat long... \n ' + subprocess.check_output(cmd, shell=True)

        # Load lat long file
        xy_latlong = pandas.read_csv('xy_' + tile_id + '_latlong.csv', sep='\s+', names=['X', 'Y', 'return_status'],
                                     skiprows=1)

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





## Calculate slope parameter for file
def dtm_calc_slope(tile_id):
    """
    Calculates the slope parameter for a DTM neighbourhood mosaic and crops to original tile_size
    Requires dtm_generate_mosaic to be executed.
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: stdout and stderr command line output of gdal command execution.
    """

    # Initiate return value and log output
    return_value = ''
    log_output = ''

    # Get current wd
    wd = os.getcwd()

    try:
        # Calculate slope parameter
        cmd = settings.gdaldem_bin + ' slope ' + \
            settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
            wd + '/slope_' + tile_id + '_mosaic.tif '
        log_output = tile_id + ' slope calculation... \n ' + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Croping slope output to original tile size:
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
              '-crop_to_cutline -overwrite ' + \
              wd + '/slope_' + tile_id + '_mosaic.tif ' + \
              settings.output_folder + '/slope/slope_' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' slope calculation successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' slope calculation failed. \n\n'
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    os.remove(wd + '/slope_' + tile_id + '_mosaic.tif ')

    # Return return value
    return return_value


## Calculate slope parameter for file
def dtm_calc_aspect(tile_id):
    """
    Calculates the slope parameter for a DTM neighbourhood mosaic and crops to original tile_size
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: stdout and stderr command line output of gdal command execution.
    """

    # Initiate return valule and log output
    return_value = ''
    log_output = ''

    # get temporary work directory
    wd = os.getcwd()

    try:
        # Calculate slope parameter
        cmd = settings.gdaldem_bin + ' aspect -zero_for_flat ' + \
        settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
        wd + '/aspect_' + tile_id + '_mosaic.tif '
        log_output = tile_id + ' aspect calculation... \n ' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Crop slope output to original tile size:
        cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          '-crop_to_cutline -overwrite ' + \
          wd + '/aspect_' + tile_id + '_mosaic.tif ' + \
          settings.output_folder + '/aspect/aspect_' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aspect calculation successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' slope calculation failed.\n\n'
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    os.remove(wd + 'aspect_' + tile_id + '_mosaic.tif ')

    return return_value

