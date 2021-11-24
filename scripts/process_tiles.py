### Script to rasterise point clouds for the DK nationwide lidar re-processing
### Jakob Assmann j.assann@bios.au.dk 29 January 2019

## Imports
import glob
import re
import os
import shutil
import datetime
import time
import multiprocessing
import pandas
import opals

from dklidar import points
from dklidar import dtm
from dklidar import settings
from dklidar import common

#### Prepare the environment

# Set working directory
os.chdir(settings.wd)

# Set number of parallel processes:
n_processes = 62 # 54

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
for folder in [settings.dtm_mosaics_folder, settings.dtm_footprint_folder,
               settings.odm_folder, settings.odm_footprint_folder, settings.output_folder]:
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

    # Stagger processing if this is the first turn during a processing id
    # This is a crucial step to reduce the chance of the functions using gdal_rasterize to run directly in parallel
    # (generate mask function), if more than 10 gdla_rasterize instances run in parallel there is a massive drop in
    # performance for some reason
    if not os.path.exists(temp_wd + '/first_go_complete.txt'):
        # sleep for 5 seconds. Providing the maximum performance gain for all full integers < 6s = sequential
        time.sleep(5 * int(re.sub('[(),]', '', str(multiprocessing.current_process()._identity))))
        lock_file = open(temp_wd + '/first_go_complete.txt', 'w')
        lock_file.close()
    # opals loadModules
    opals.loadAllModules()

    ## Logging: Keep track of progress for each step and overall progress
    # Initiate progress variables
    steps = ['processing']
    status_steps = [['complete']]

    ## Generate masks
    return_value = common.generate_water_masks(tile_id)
    # Update progress variables
    steps.append('generate_water_masks')
    status_steps.append([return_value])
    # gather logs for step and tile
    common.gather_logs('process_tiles', 'generate_water_masks', tile_id)

    ## Import tile to ODM
    return_value = points.odm_import_single_tile(tile_id)
    # Update progress variables
    steps.append('odm_import_single_tile')
    status_steps.append([return_value])
    # gather logs for step and tile
    common.gather_logs('process_tiles', 'odm_import_single_tile', tile_id)

    ## Validate CRS of odm files
    return_value = points.odm_validate_crs(tile_id)
    # Update progress variables
    steps.append('odm_validate_crs')
    status_steps.append([return_value])

    ## Export footprint
    return_value = points.odm_generate_footprint(tile_id)
    # Update progress variables
    steps.append('odm_generate_footprint')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_generate_footprint', tile_id)

    ## Normalise height
    return_value = points.odm_add_normalized_z(tile_id)
    # Update progress variables
    steps.append('odm_add_normalized_z')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_add_normalized_z', tile_id)

    ## Export mean normalised height for 10 m x 10 m cell
    return_value = points.odm_export_normalized_z(tile_id)
    # Update progress variables
    steps.append('odm_export_normalized_z')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_normalized_z', tile_id)

    ## Export canopy height
    return_value = points.odm_export_canopy_height(tile_id)
    # Update progress variables
    steps.append('odm_export_canopy_height')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_canopy_height', tile_id)

    ## Export point counts for pre-defined intervals and classess
    return_value = points.odm_export_point_counts(tile_id)
    # Update progress variables
    steps.append('odm_export_point_counts')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_point_counts', tile_id)

    ## Export proportions based on point counts
    return_value = points.odm_export_proportions(tile_id)
    # Update progress variables
    steps.append('odm_export_proportions')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_proportions', tile_id)

    ## Export point source information
    return_value = points.odm_export_point_source_info(tile_id)
    # Update progress variables
    steps.append('odm_export_point_source_info')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_point_source_info', tile_id)

    ## Export amplitude mean and sd
    return_value = points.odm_export_amplitude(tile_id)
    # Update progress variables
    steps.append('odm_export_amplitude')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_amplitude', tile_id)

    ## Export date stamps
    return_value = points.odm_export_date_stamp(tile_id)
    # Update progress variables
    steps.append('odm_export_date_stamp')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_export_date_stamp', tile_id)
    
    ## Remove unneeded odm files
    return_value = points.odm_remove_temp_files(tile_id)
    # Update progress variables
    steps.append('odm_remove_temp_files')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'odm_remove_temp_files', tile_id)


    ## Terrain model derived variables

    ## Generate tile footprint
    return_value = dtm.dtm_generate_footprint(tile_id)
    # Update progress variables
    steps.append('dtm_generate_footprint')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_generate_footprint', tile_id)

    ## Generate neighbourhood mosaic
    return_value = dtm.dtm_neighbourhood_mosaic(tile_id)
    # Update progress variables
    steps.append('dtm_neighbourhood_mosaic')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_neighbourhood_mosaic', tile_id)

    ## Validate CRS
    return_value = dtm.dtm_validate_crs(tile_id)
    # Update progress variables
    steps.append('dtm_validate_crs')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_validate_crs', tile_id)

    ## Generate 10 m aggregate of DEM
    return_value = dtm.dtm_aggregate_tile(tile_id)
    # Update progress variables
    steps.append('dtm_aggregate_tile')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_aggregate_tile', tile_id)

    ## Generate 10 m aggregate of neighbourhood mosaic
    return_value = dtm.dtm_aggregate_mosaic(tile_id)
    # Update progress variables
    steps.append('dtm_aggregate_mosaic')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_aggregate_mosaic', tile_id)
    
    ## Calculate slope
    return_value = dtm.dtm_calc_slope(tile_id)
    # Update progress variables
    steps.append('dtm_calc_slope')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_calc_slope', tile_id)

    ## Calculate aspect
    return_value = dtm.dtm_calc_aspect(tile_id)
    # Update progress variables
    steps.append('dtm_calc_aspect')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_calc_aspect', tile_id)

    ## Calculate heat index
    return_value = dtm.dtm_calc_heat_index(tile_id)
    # Update progress variables
    steps.append('dtm_calc_heat_index')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_calc_heat_index', tile_id)

    ## Calculate solar radiation
    return_value = dtm.dtm_calc_solar_radiation(tile_id)
    # Update progress variables
    steps.append('dtm_calc_solar_radiation')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_calc_solar_radiation', tile_id)

    ## Calculate landscape openness mean
    return_value = dtm.dtm_openness_mean(tile_id)
    # Update progress variables
    steps.append('dtm_openness_mean')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_openness_mean', tile_id)

    ## Calculate landscape openness difference
    return_value = dtm.dtm_openness_difference(tile_id)
    # Update progress variables
    steps.append('dtm_openness_difference')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_openness_difference', tile_id)

    ## Calculate Kopecky TWI
    return_value = dtm.dtm_kopecky_twi(tile_id)
    # Update progress variables
    steps.append('dtm_kopecky_twi')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_kopecky_twi', tile_id)

    ## Remove unneeded dtm files
    return_value = dtm.dtm_remove_temp_files(tile_id)
    # Update progress variables
    steps.append('dtm_remove_temp_files')
    status_steps.append([return_value])
    # gather logs for step and tile]
    common.gather_logs('process_tiles', 'dtm_remove_temp_files', tile_id)

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

    ## If processing of a specific subset of tiles is needed 
    ## the following lines can be helpful in achieving the task
    ## Remove comments as needed. 
##    tiles_to_process_completed = set(progress_df.index.values[progress_df['processing'] == 'complete'].tolist())
##    tiles_to_process_dhm201415 = set(pandas.read_csv('auxillary_files/tiles_to_process_dhm201415_merger.csv')['tile_id'].tolist())
##    tiles_to_process = tiles_to_process_dhm201415 - tiles_to_process_completed
##    tiles_to_process = tiles_to_process - (tiles_to_process - set(progress_df.index.values.tolist()))
##    print('Processing ' + str(len(tiles_to_process)) + ' tiles. \n')
##    time.sleep(60)
    
    # Set up processing pool
    multiprocessing.set_executable(settings.python_exec_path)
    pool = multiprocessing.Pool(processes=n_processes)

    # Execute processing of tiles
    print(datetime.datetime.now().strftime('%X') + ' Processing tiles: ... '),
    tile_processing = pool.map_async(process_tile, tiles_to_process)
    # Make sure all processes finish before carrying on.
    tile_processing.wait()
    print('... done.')

    # Clear scratch folder
    shutil.rmtree('scratch')
    os.mkdir('scratch')
    shutil.copy('data/empty_on_purpose.txt', 'scratch/empty_on_purpose.txt') 
    
    # Update progress status
    progress_df = common.update_progress_df('process_tiles', progress_df)
    # Export progress_df as CSV
    progress_file = settings.log_folder + '/process_tiles/' + 'overall_progress.csv'
    progress_df.to_csv(progress_file, index=True, header=True)

    # Print out time elapsed:
    print('\nTime elapsed: ' + str(datetime.datetime.now() - startTime))

