### Functions for DTM raster file handling for DK Lidar project
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

import os
import subprocess
import multiprocessing
import re
from dklidar import settings

#### Function definitions

## Generate tile footprint
def dtm_generate_footprint(tile_id):
    """
    Generates a footprint file using gdal
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return stdout and stderr command line output of gdal command execution.
    """

    # Generate temporay wd for parallel worker, this will allow for smooth logging and opals sessions to run in parallel
    wd = os.getcwd()
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = settings.scratch_folder + '/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)


    cmd = settings.gdaltlindex_bin + \
          settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif'
    cmd_return = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    log_output = '\n' + tile_id + ' footprint generation... \n' + cmd_return + \
                    '\n' + tile_id + ' successful.\n\n'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Change back to original working directory
    os.chdir(wd)



def dtm_mosaic_neighbours(tile_id):
    """
    Generates a tif mosaic with all existing 8 neighbouring cells
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    input_folder: folder location for input dtm files. ouput_folder ouput location for dtm mosaics.
    :return: stdout and stderr command line output of gdal command execution.
    """

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
    except:
        log_output = log_output + tile_id + ' failed.\n\n'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Change back to original working directory
    os.chdir(wd)

## Calculate slope parameter for file
def dtm_calculate_slope(tile_id):
    """
    Calculates the slope parameter for a DTM neighbourhood mosaic and crops to original tile_size
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: stdout and stderr command line output of gdal command execution.
    """

    # Generate temporay wd for parallel worker, this will allow for smooth logging and opals sessions to run in parallel
    wd = os.getcwd()
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = settings.scratch_folder + '/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)

    # Check whether DTM mosaic exists
    if not os.path.exists(settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif '):
        print('\n' + tile_id + ' Warning: DTM mosaic does not exist!\n')
        return '\n' + tile_id + ' Warning: DTM mosaic does not exist!'

    # Check whether slope has already been calculated
    #if os.path.exists(wd + '/' + output_folder + '/dtm_slope/slope_' + tile_id + '.tif '):
    #    print('\n' + tile_id + ' slope has already been calculated. Skipping tile...\n')
    #    return '\n' + tile_id + ' slope has already been calculated. Skipping tile...'

    # Calculate slope parameter
    cmd = settings.gdaldem_bin + ' slope ' + \
        settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
        settings.output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif '
    log_output = tile_id + ' slope calculation... \n ' + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

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

    # Switch back to original working directory
    os.chdir(wd)
