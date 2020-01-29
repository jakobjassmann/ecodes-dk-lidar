### Script to prepare dtm nieghbourhood mosaics for the dk nationwide lidar re-processing
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

from dklidar import dtm
from dklidar import settings
from dklidar import common
import glob
import sys
import re
import os
import datetime
import multiprocessing

#### Prepare the environment

# Set working directory
os.chdir(settings.wd)

# Confirm essential folders exist
if not os.path.exists(settings.wd):
    print('Working Directory ' + settings.wd + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(settings.dtm_folder):
    print('dtm_folder ' + settings.dtm_folder + ' does not exist. Exiting script...')
    exit()
# Conmfirm other folders exists and if not create them
for folder in [settings.dtm_mosaics_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)

# Load file names
dtm_files = glob.glob(settings.dtm_folder + '/*.tif')

# initiate dictionaries for tile_ids
dtm_tile_ids = []

# fill dictionaries with tile_id, as well as row number and column number for each file name:
for file_name in dtm_files:
    tile_id = re.sub('.*DTM_1km_(\d*_\d*).tif', '\g<1>', file_name)
    dtm_tile_ids.append(tile_id)

#### Define workflow
def prep_dtm(tile_id):
    """
    Simple function that defines steps that need to be carried out for each tile in sequence
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: nothing.
    """
    # Generate tile footprint
    dtm.generate_footprint(tile_id)
    # Generate neighbourhood mosaic
    dtm.mosaic_neighbours(tile_id)
    # Calculate slope and trim to original tile size
    dtm.calculate_slope(tile_id)
    # Print tile_id to confirm success
    print(tile_id + ' '),

#### Main body of script

if __name__ == '__main__':

    ## Start timer
    startTime = datetime.datetime.now()

    # open log file
    global_log_file = open(settings.log_folder + '/prep_dtm_'+ startTime.strftime('%Y%m%d-%H-%M-%S') + '.log', 'a+')

    # Set up processing pool
    print(sys.executable)
    multiprocessing.set_executable(settings.python_exec_path)
    n_processes = 54
    pool = multiprocessing.Pool(processes = n_processes)

    print('Processing tiles: ...')
    prep_dtms = pool.map_async(prep_dtm, dtm_tile_ids)
    prep_dtms.wait()

    ### The below code is faster than running the tasks in sqeuence for each tile... (about 1/3 of the time needed).
    # # Generate footprints for all files
    # print('\nGenerating tile footprints: ...')
    # footprints = pool.map_async(dtm.generate_footprint, dtm_tile_ids[1:10])
    # footprints.wait()
    #
    #
    # ## Generate neighbourhood mosaics for all files
    # print('\nGenerating neighbourhood mosaics: ...')
    # mosaics = pool.map_async(dtm.mosaic_neighbours, dtm_tile_ids[1:10])
    # mosaics.wait()
    #
    #
    # ## Generate calculate slopes for all files
    # print('\nGenerating slopes: ...')
    # slopes = pool.map_async(dtm.calculate_slope, dtm_tile_ids[1:10])
    # slopes.wait()

    # Gather log file from workers:
    common.gather_logs(n_processes, global_log_file)

    # Tidy up environment
    global_log_file.close()
    pool.close()

    # Print out time elapsed:
    print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))