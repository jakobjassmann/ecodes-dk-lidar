# This is a simple script to explore data handling options with OPALS
# Jakob Assmann j.assmann@bios.au.dk 17 January 2020

# Imports
import glob
import time
import sys
import re
import os
import subprocess
import datetime
import multiprocessing

#### Preparations

# Set folder locations
wd = 'D:/Jakob/dk_nationwide_lidar'
laz_folder = 'data/laz'
dtm_folder = 'data/dtm'
dtm_footprint_folder = 'data/dtm_footprints'
dtm_mosaics_folder = 'data/dtm_mosaics'
output_folder = 'data/outputs'

# Set paths to gdal executables / binaries (here we use OSGE4W64) as the OPALS gdal binaries do not work reliably
# remember the trailing spaces at the end!
# simply set to the gdal command e.g. 'gdalwarp ' if you want to use the OPALS gdal binaries (gdaldem slope won't work)
gdalwarp_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdalwarp '
gdaldem_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdaldem '
gdaltlindex_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdaltindex '

# Set working directory
os.chdir(wd)

# Confirm folders exist
if not os.path.exists(wd):
    print('Working Directory ' + wd + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(laz_folder):
    print('laz_folder ' + laz_folder + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(dtm_folder):
    print('dtm_folder ' + dtm_folder + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(dtm_footprint_folder):
    os.mkdir(dtm_footprint_folder)
if not os.path.exists(dtm_mosaics_folder):
    os.mkdir(dtm_mosaics_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)


#### Function definitions

## Generate tile footprint
def dtm_generate_footprint(tile_id):
    """
    Generates a footprint file using gdal
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return stdout and stderr command line output of gdal command execution.
    """
    print(tile_id + ' '),
    cmd = gdaltlindex_bin + \
          wd + '/' + dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          wd + '/' + dtm_folder + '/DTM_1km_' + tile_id + '.tif'
    return '\n' + tile_id + ' footprint generation... \n' + subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT)


## Mosaic tile neighbours
def dtm_mosaic_neighbours(tile_id):
    """
    Generates a tif mosaic with all existing 8 neighbouring cells
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: stdout and stderr command line output of gdal command execution.
    """
    # Retrieve row and col numbers for the current tile_id
    tile_id_rowcol = tile_ids[tile_id]

    # Determine row and column numbers for tiles in the 3 x 3 window
    rows_to_load = [tile_id_rowcol['row'] - 1, tile_id_rowcol['row'], tile_id_rowcol['row'] + 1]
    cols_to_load = [tile_id_rowcol['col'] - 1, tile_id_rowcol['col'], tile_id_rowcol['col'] + 1]

    # Generate list of tile_ids for tiles to load
    tiles_to_load = []
    for row in rows_to_load:
        for col in cols_to_load:
            tile_to_load = str(row) + '_' + str(col)
            tiles_to_load.extend([tile_to_load])

    # Mosaic files using subprocess and gdal_mosaic
    print(tile_id + ' '),

    # Prep filenames and check if files exists:
    tile_file_names = []
    for tile_to_load in tiles_to_load:
        tile_file_name = wd + '/' + dtm_folder + '/DTM_1km_' + tile_to_load + '.tif'
        if os.path.exists(tile_file_name):
            tile_file_names.append(tile_file_name)
    n_neigh = len(tile_file_names)
    tile_file_names = ' '.join(tile_file_names)

    if n_neigh == 9:
        output = '\n' + tile_id + ' mosaicing... \n' + 'Number of neighbours = ' + str(n_neigh) + '. Complete!\n'
    else:
        output = '\n' + tile_id + ' mosaicing... \n' + 'Warning! Number of neighbours = ' + str(n_neigh) + '. Incomplete. Edge effects possible!\n'

    # Construct command:
    cmd = gdalwarp_bin + ' ' + tile_file_names + ' ' + \
          wd + '/' + dtm_mosaics_folder + '/DTM_' + \
          tile_id + '_mosaic.tif '
    # Execute command and return output:
    return  output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)


## Calculate slope parameter for file
def dtm_calculate_slope(tile_id):
    """
    Calculates the slope parameter for a DTM neighbourhood mosaic and crops to original tile_size
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: stdout and stderr command line output of gdal command execution.
    """
    print(tile_id + ' '),

    # Check whether DTM mosaic exists
    if not os.path.exists(wd + '/' + dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif '):
        print('\n' + tile_id + ' Warning: DTM mosaic does not exist!\n')
        return '\n' + tile_id + ' Warning: DTM mosaic does not exist!'

    # Check whether slope has already been calculated
    #if os.path.exists(wd + '/' + output_folder + '/dtm_slope/slope_' + tile_id + '.tif '):
    #    print('\n' + tile_id + ' slope has already been calculated. Skipping tile...\n')
    #    return '\n' + tile_id + ' slope has already been calculated. Skipping tile...'

    # Calculate slope parameter
    cmd = gdaldem_bin + ' slope ' + \
          wd + '/' + dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
          wd + '/' + output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif '
    output = '\n' + tile_id + ' slope calculation... \n ' + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Croping slope output to original tile size:
    cmd = gdalwarp_bin + \
          ' -cutline ' + wd + '/' + dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          '-crop_to_cutline -overwrite ' + \
          wd + '/' + output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif ' + \
          wd + '/' + output_folder + '/dtm_slope/slope_' + tile_id + '.tif '
    output = output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Remove temporary file
    os.remove(wd + '/' + output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif ')

    return(output)

# prepare global environmental variables

## Load tile_ids from file names

# Load file names
dtm_files = glob.glob(dtm_folder + '/*.tif')
# laz_files = glob.glob(laz_folder + '/*.laz')

# initiate dictionary for tile_ids
tile_ids = {}

# fill dictionary with tile_id, as well as row number and column number for each file name:
for file_name in dtm_files:
    tile_id = re.sub('.*DTM_1km_(\d*_\d*).tif', '\g<1>', file_name)
    row = int(re.sub('.*DTM_1km_(\d+)_\d+.tif', '\g<1>', file_name))
    col = int(re.sub('.*DTM_1km_\d+_(\d+).tif', '\g<1>', file_name))
    tile_ids[tile_id] = {'row': row, 'col': col}
    #     tile_id = re.sub('.*PUNKTSKY_1km_(\d*_\d*).laz', '\g<1>', file_name)
    #     row = int(re.sub('.*PUNKTSKY_1km_(\d+)_\d+.laz', '\g<1>', file_name))
    #     col = int(re.sub('.*PUNKTSKY_1km_\d+_(\d+).laz', '\g<1>', file_name))
    #     tile_ids[tile_id] = {'row': row, 'col': col}

#### Main body of script

if __name__ == '__main__':

    ## Start timer
    startTime = datetime.datetime.now()

    # open log file
    log_file = open('log/slope_calc_'+ startTime.strftime('%Y%m%d-%H-%M-%S') + '.log', 'w+')

    ## Sequential processing code
    # for tile_id in tile_ids.keys():
    #     dtm_process_tile(tile_id)

    ## Parallel processing code
    # Avoid spawning behaviour error on windows

    # Set up processing pool
    print(sys.executable)
    multiprocessing.set_executable('C:/Program Files/opals_nightly_2.3.2/opals/python.exe')
    pool = multiprocessing.Pool(processes = 52)

    # Generate footprints for all files
    print('\nGenerating tile footprints: ...')
    #output = pool.map(dtm_generate_footprint, tile_ids.keys())
    #log_file.write(' '.join(output))

    ## Generate neighbourhood mosaics for all files
    print('\nGenerating neighbourhood mosaics: ...')
    #output = pool.map(dtm_mosaic_neighbours, tile_ids.keys())
    #log_file.write(' '.join(output))

    ## Generate calculate slopes for all files
    print('\nGenerating slopes: ...')
    output = pool.map(dtm_calculate_slope, tile_ids.keys()[0:106])

    # Pause for 10 seconds to allow for pool to finish up processing
    log_file.write(' '.join(output))

    # Tidy up environment
    log_file.close()
    pool.close()

    print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))

