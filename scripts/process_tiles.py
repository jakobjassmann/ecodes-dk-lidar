### Script to rasterise point clouds for the DK nationwide lidar re-processing
### Jakob Assmann j.assann@bios.au.dk 29 January 2019

## Imports
from dklidar import points
from dklidar import settings
from dklidar import common
import glob
import sys
import re
import os
import datetime
import time
import multiprocessing
import opals
import pandas

#### Prepare the environment

# Set working directory
os.chdir(settings.wd)

# Confirm essential folders exist
if not os.path.exists(settings.wd):
    print('Working Directory ' + settings.wd + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(settings.laz_folder):
    print('laz_folder ' + settings.laz_folder + ' does not exist. Exiting script...')
    exit()
if not os.path.exists(settings.dtm_folder):
    print('dtm_folder ' + settings.dtm_folder + ' does not exist. Exiting script...')
    exit()
# Conmfirm other folders exists and if not create them
for folder in [settings.dtm_mosaics_folder, settings.odm_folder, settings.odm_mosaics_folder,
               settings.odm_footprint_folder, settings.output_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)

# Load file names
dtm_files = glob.glob(settings.dtm_folder + '/*.tif')
laz_files = glob.glob(settings.laz_folder + '/*.laz')

# initiate empty lists for tile_ids
dtm_tile_ids = []
laz_tile_ids = []

# fill dictionaries with tile_id, as well as row number and column number for each file name:
for file_name in dtm_files:
    tile_id = re.sub('.*DTM_1km_(\d*_\d*).tif', '\g<1>', file_name)
    dtm_tile_ids.append(tile_id)

for file_name in laz_files:
    tile_id = re.sub('.*PUNKTSKY_1km_(\d*_\d*).laz', '\g<1>', file_name)
    laz_tile_ids.append(tile_id)


## Define processing steps for each tile to be carried out in parallel
def process_tile(tile_id):

    # Generate temporary wd for parallel worker, this will allow for smooth logging and opals sessions to run in parallel
    wd = os.getcwd()
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = settings.scratch_folder + '/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)

    # Create folder for logging
    tile_log_folder = settings.log_folder + '/process_tiles/' + tile_id
    if not os.path.exists(tile_log_folder):
        os.mkdir(tile_log_folder)

    # Load all (available) OPALS modules
    #opals.loadAllModules()

    # Create tile neighbourhood mosaic
    # points.create_tile_mosaic(tile_id)

    # Write status update into status.csv file
    colnames = ['tile_id', 'processing']
    columns = [[tile_id], ['completed']]
    # Zip into pandas data frame
    status_df = pandas.DataFrame(zip(*columns), columns=colnames)
    # Export as CSV
    status_df.to_csv(tile_log_folder + '/status.csv', index=False, header=True)

    # Change back to original working directory
    os.chdir(wd)

    # Print tile_id to console to update on status
    print(tile_id)


#### Main body of script

if __name__ == '__main__':

    ## Start timer
    startTime = datetime.datetime.now()

    ## Status output to console
    print('\n' + '-' * 80 + 'Starting process_tiles.py at ' + str(startTime) + '\n')

    ## Prepare process managment and logging
    # Specify list of processing steps to be carried out
    step_list = ['create_tile_moasic']
    progress_df = common.init_log_folder('process_tiles', laz_tile_ids, step_list)
    tiles_to_process = set(progress_df['tile_id'].tolist())
    # Set up processing pool
    multiprocessing.set_executable(settings.python_exec_path)
    n_processes = 10
    pool = multiprocessing.Pool(processes = n_processes)

    # Execute processing of tiles
    print('Processing tiles: ...')
    tile_processing = pool.map_async(process_tile, tiles_to_process)
    # Make sure all processes finish before carrying on.
    tile_processing.wait()

    # Print out time elapsed:
    print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))