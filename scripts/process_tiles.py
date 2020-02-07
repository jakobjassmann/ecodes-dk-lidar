### Script to rasterise point clouds for the DK nationwide lidar re-processing
### Jakob Assmann j.assann@bios.au.dk 29 January 2019

## Imports
from dklidar import points
from dklidar import settings
from dklidar import common
import glob
import re
import os
import datetime
import multiprocessing
import pandas
import opals

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

    ## Prepare environment
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

    # opals loadModules
    opals.loadAllModules()

    ## Logging: Keep track of progress for each step and overall progress
    # Initiate progress variables
    steps = ['processing']
    status_steps = [['complete']]

    # ## Import tile to ODM
    # return_value = points.odm_import_single_tile(tile_id)
    # # Update progress variables
    # steps.append('odm_import_single_tile')
    # status_steps.append([return_value])
    # # gather logs for step and tile
    # common.gather_logs('process_tiles', 'odm_import_single_tile', tile_id)
    #
    # ## Import tile neighbourhood mosaic
    # return_value = points.odm_import_mosaic(tile_id)
    # # Update progress variables
    # steps.append('odm_import_mosaic')
    # status_steps.append([return_value])
    # # gather logs for step and tile
    # common.gather_logs('process_tiles', 'odm_import_mosaic', tile_id)
    #
    # ## Validate CRS of odm files
    # return_value = points.odm_validate_crs(tile_id)
    # # Update progress variables
    # steps.append('odm_validate_crs')
    # status_steps.append([return_value])

    # ## Export footprint
    # return_value = points.odm_generate_footprint(tile_id)
    # # Update progress variables
    # steps.append('odm_generate_footprint')
    # status_steps.append([return_value])
    # # gather logs for step and tile]
    # common.gather_logs('process_tiles', 'odm_generate_footprint', tile_id)

    # ## Normalise height
    # return_value = points.odm_add_normalized_z(tile_id)
    # # Update progress variables
    # steps.append('odm_add_normalized_z')
    # status_steps.append([return_value])
    # # gather logs for step and tile]
    # common.gather_logs('process_tiles', 'odm_add_normalized_z', tile_id)
    #
    # ## Export mean normalised height for 10 m x 10 m cell
    # return_value = points.odm_export_normalized_z(tile_id)
    # # Update progress variables
    # steps.append('odm_export_normalized_z')
    # status_steps.append([return_value])
    # # gather logs for step and tile]
    # common.gather_logs('process_tiles', 'odm_export_normalized_z', tile_id)

    ## Export point count for pre-defined intervals
    return_value = points.odm_export_point_counts(tile_id)
    # Update progress variables
    steps.append('odm_export_point_counts')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_point_counts', tile_id)

    ## Logging: finalise log outputs
    # Zip into pandas data frame
    status_df = pandas.DataFrame(zip(*status_steps), index = [tile_id], columns=steps)
    status_df.index.name = 'tile_id'
    # Export as CSV
    status_df.to_csv(tile_log_folder + '/status.csv', index=True, header=True)

    # Change back to original working directory
    os.chdir(wd)

    # Print tile_id to console to update on status
    print(datetime.datetime.now().strftime('%X') + ' ' + tile_id + ' '),


#### Main body of script
if __name__ == '__main__':

    ## Start timer
    startTime = datetime.datetime.now()

    ## Status output to console
    print('\n' + '-' * 80 + 'Starting process_tiles.py at ' + str(startTime.strftime('%c')) + '\n')

    ## Prepare process managment and logging
    progress_df = common.init_log_folder('process_tiles', laz_tile_ids)

    ## Identify which tiles still require processing
    tiles_to_process = set(progress_df.index.values[progress_df['processing'] != 'complete'].tolist())
    # Set up processing pool
    multiprocessing.set_executable(settings.python_exec_path)
    n_processes = 54
    pool = multiprocessing.Pool(processes=n_processes)

    # Execute processing of tiles
    print(datetime.datetime.now().strftime('%X') + ' Processing tiles: ... '),
    tile_processing = pool.map_async(process_tile, tiles_to_process)
    # Make sure all processes finish before carrying on.
    tile_processing.wait()
    print('... done.')

    # Update progress status
    progress_df = common.update_progress_df('process_tiles', progress_df)
    # Export progress_df as CSV
    progress_file = settings.log_folder + '/process_tiles/' + 'overall_progress.csv'
    progress_df.to_csv(progress_file, index=True, header=True)

    # Print out time elapsed:
    print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))