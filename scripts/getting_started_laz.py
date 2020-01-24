# This is a simple script to explore data handling of LAZ files with OPALS
# Jakob Assmann j.assmann@bios.au.dk 17 January 2020

# Imports
import glob
import sys
import re
import os
import opals
import subprocess
import datetime
import multiprocessing

#### Preparations
# Load all opals modules
opals.loadAllModules()


# Set paths to gdal executables / binaries (here we use OSGE4W64) as the OPALS gdal binaries do not work reliably
# remember the trailing spaces at the end!
# simply set to the gdal command e.g. 'gdalwarp ' if you want to use the OPALS gdal binaries (gdaldem slope won't work)
gdalwarp_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdalwarp '
gdaldem_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdaldem '
gdaltlindex_bin = 'C:/OSGeo4W64/OSGeo4W.bat gdaltindex '

# Set folder locations
wd = 'D:/Jakob/dk_nationwide_lidar'
laz_folder = 'data/sample/laz'
dtm_folder = 'data/sample/dtm'
dtm_mosaics_folder = 'data/sample/dtm'
odm_folder = 'data/sample/odm'
odm_mosaics_folder = 'data/sample/odm_mosaics'
odm_footprint_folder = 'data/sample/odm_footprint'
output_folder = 'data/sample/outputs'

# Set working directory
os.chdir(wd)

# Confirm essential folders exist
if not os.path.exists(wd):
    print('Working Directory ' + wd + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(laz_folder):
    print('laz_folder ' + laz_folder + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(dtm_folder):
    print('dtm_folder ' + dtm_folder + ' does not exist. Exiting script...')
    exit()
# Conmfirm other folders exists and if not create them
for folder in [dtm_mosaics_folder, odm_folder, odm_mosaics_folder, odm_footprint_folder, output_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)

# Load file names
dtm_files = glob.glob(dtm_folder + '/*.tif')
laz_files = glob.glob(laz_folder + '/*.laz')

# initiate dictionaries for tile_ids
dtm_tile_ids = {}
laz_tile_ids = {}

# fill dictionaries with tile_id, as well as row number and column number for each file name:
for file_name in dtm_files:
    tile_id = re.sub('.*DTM_1km_(\d*_\d*).tif', '\g<1>', file_name)
    row = int(re.sub('.*DTM_1km_(\d+)_\d+.tif', '\g<1>', file_name))
    col = int(re.sub('.*DTM_1km_\d+_(\d+).tif', '\g<1>', file_name))
    dtm_tile_ids[tile_id] = {'row': row, 'col': col}

for file_name in laz_files:
    tile_id = re.sub('.*PUNKTSKY_1km_(\d*_\d*).laz', '\g<1>', file_name)
    row = int(re.sub('.*PUNKTSKY_1km_(\d+)_\d+.laz', '\g<1>', file_name))
    col = int(re.sub('.*PUNKTSKY_1km_\d+_(\d+).laz', '\g<1>', file_name))
    laz_tile_ids[tile_id] = {'row': row, 'col': col}

# # find tiles present only in one but no the other
# tile_ids_diff = set(laz_tile_ids.keys()).difference(set(dtm_tile_ids.keys()))
# print('Tile difference:')
# print(tile_ids_diff)
# print('Tiles only with dtm:')
# print(tile_ids_diff.difference(set(laz_tile_ids.keys())))
# print('Tiles only with laz:')
# print(tile_ids_diff.difference(set(dtm_tile_ids.keys())))
# print('No tiles: ' + str(len((tile_ids_diff.difference(set(dtm_tile_ids.keys()))))))

### Function definitions

## Def: Export tile footprint
def laz_grid_footprint(laz_tile_id):
    """
    Exports footprint from a laz file based on the tile_id in the DK nationwide dataset
    :param laz_tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns nothing, but creates a
    """

    # Generate temporay wd for parallel worker this will allow opals sessions to run in parallel
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = wd + '/data/scratch/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)
    print(os.getcwd())

    # Generate relevant file names:
    laz_file = wd + '/' + laz_folder + '/PUNKTSKY_1km_' + laz_tile_id + '.laz'
    odm_file = wd + '/' + odm_folder + '/odm_' + laz_tile_id + '.odm'
    temp_tif_file = wd + '/data/scratch/temp_' + laz_tile_id + '.tif'
    footprint_file = wd + '/' + odm_footprint_folder + '/footprint_' + laz_tile_id + '.shp'

    # Import tile id
    import_tile = opals.Import.Import()
    import_tile.inFile = laz_file
    import_tile.outFile = odm_file
    import_tile.run()

    # Export temporary tif
    export_tif = opals.Cell.Cell()
    export_tif.inFile = odm_file
    export_tif.outFile = temp_tif_file
    export_tif.feature = 'min'
    export_tif.cellSize = 10 # This is also the default cell size, so technically not needed.
    export_tif.run()

    # Generate footprint for temp tif
    cmd = gdaltlindex_bin + ' ' + footprint_file + ' ' + temp_tif_file
    output = '\n' + tile_id + ' footprint generation... \n' + \
           subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT)

    # Remove temp raster file
    os.remove(temp_tif_file)

    # change back to main workdir
    os.chdir(wd)

    return output


## Def: Retrieve CRS
def laz_validate_crs(laz_tile_id):
    """
    Function to validate the crs of a dk nationwide LiDAR
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return:
    """
    # Generate temporay wd for parallel worker this will allow opals sessions to run in parallel
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = wd + '/data/scratch/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)
    print(os.getcwd())

    # Generate odm file pathname
    odm_file = wd + '/' + odm_folder + '/odm_' + laz_tile_id + '.odm'

    file_info = opals.Info.Info()
    file_info.inFile = odm_file
    output = file_info.run()
    print(output)

    os.chdir(wd)

def test_function(laz_tile_id):
    print(laz_tile_id)
    process_id = multiprocessing.current_process()._identity
    print(process_id)

#### Main body of script

if __name__ == '__main__':

    ## Start timer
    startTime = datetime.datetime.now()

    # open log file
    #log_file = open('log/slope_calc_'+ startTime.strftime('%Y%m%d-%H-%M-%S') + '.log', 'w+')

    ## Sequential processing code
    # for tile_id in laz_tile_ids.keys():
    #     laz_grid_footprint(tile_id)

    ## Parallel processing code

    # # Set up processing pool
    multiprocessing.set_executable('C:/Program Files/opals_nightly_2.3.2/opals/python.exe')
    pool = multiprocessing.Pool(processes=9)
    print(laz_tile_ids.keys())
    #pool.map(laz_grid_footprint, laz_tile_ids.keys())
    pool.map(laz_validate_crs, [laz_tile_ids.keys()[1]])
    pool.close()

    print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))

