### Common module for the dklidar reporcessing - general functions likely used by all scripts
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

# Imports
import os
import glob
import pandas
import re
import shutil
import datetime
import subprocess

from dklidar import settings

## Function definitons

## Logging function to initalise logging process key to progress managment.
def init_log_folder(script_name, tile_ids):
    """
    Initiates a log folder for storing the processing output and progress management
    :param script_name: name of the processing script for which to initialise the logging database / folder
    :param tile_ids: tile ids in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number
    :return: pandas DataFrame with progress data
    """

    # Check and create root folder for script
    log_folder = settings.log_folder + '/' + script_name
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    # Check whether processing status file exists
    progress_file = log_folder + '/' + 'overall_progress.csv'

    if not os.path.exists(progress_file):
        print(datetime.datetime.now().strftime('%X') +
              ' No progress file found, creating log folder and progress file...'),
        ## Initiate pandas data frame with tile_ids as rows and processing_steps as columns
        # Create empty list to hold columns
        cols = []
        # Add processing status column
        cols.append(['pending'] * len(tile_ids))
        # prepare colnames
        colnames = ['processing']
        # Zip into pandas data frame
        progress_df = pandas.DataFrame(zip(*cols), index = tile_ids, columns = colnames)
        progress_df.index.name = 'tile_id'
        # Status update
        print(' done.')
    else:
        print(datetime.datetime.now().strftime('%X') +
              ' Progress file found, loading previous processing status...'),
        ## Load progress status_file
        try:
            progress_df = pandas.read_csv(progress_file, index_col='tile_id')
            print(' done.')
            # update progress dataframe
            progress_df = update_progress_df(script_name, progress_df)
        except:
            print('\n' + datetime.datetime.now().strftime('%X') + 'Can\'t load progress file. Exiting script!')
            quit()
        # Compare tile_id column with tile_ids list
        if not progress_df.index.values.tolist() == tile_ids:
            print('\n' +datetime.datetime.now().strftime('%X') +
                  'Warning: lists of tile_ids in laz folder( ' + settings.laz_folder +
                  ') and progress file (' + progress_file + ') do not match.' +
                  '\nPlease remove manually to reset.\nExiting script!')
            quit()

    # Export progress_df as CSV
    progress_df.to_csv(progress_file, index=True, header=True)

    # return progress_df
    return(progress_df)


## Function to gather progress update, key to progress management and logging.
def update_progress_df(script_name, progress_df):
    """
    Searches a script's log folder for subfolders matching the tile_id pattern (rrrr_ccc), then crawls these folders for
    status.csv files, compiling them into a single pandas dataframe and returning it.
    :param script_name: name of the script (for folder matching)
    :param progress_df: progress dataframe to be updated
    :return: returns an updated progress_df
    """
    # Status update
    print(datetime.datetime.now().strftime('%X') + ' Updating progress management...'),

    # Check log root folder for script if not existing... quit!
    log_folder = settings.log_folder + '/' + script_name
    if not os.path.exists(log_folder):
        print('\n' + datetime.datetime.now().strftime('%X') +
              'Warning: script log folder does not exist. Exiting script')
        quit()

    # Gather list of tile folders
    tile_folders = glob.glob(log_folder + '/*/')
    # Filter only those folders matching a tile/id
    tile_id_pattern = re.compile('.*\d+_\d+.*')
    tile_folders = filter(tile_id_pattern.match, tile_folders)

    # Loop through each tile_id_folder updating the log
    for tile_folder in tile_folders:
        # set path to status csv file
        status_csv = tile_folder + '/status.csv'
        # Check whether status.csv file exists.
        if os.path.exists(status_csv):
            # load status csv
            status_df = pandas.read_csv(status_csv, index_col='tile_id')
            # get tile id from first value in index
            tile_id = status_df.index.values.tolist()[0]
            # get list of colnames
            col_names = status_df.columns.values.tolist()
            # for each col name copy cell value into progress_df
            for col_name in col_names:
                # set cell value
                status_value = status_df.at[tile_id, col_name]
                # check whether col_name exists in progress data frame if not add empty col to data frame
                if col_name in progress_df.columns.values.tolist():
                    # set cell value for col and tile id
                    progress_df.at[tile_id, col_name] = status_value
                else:
                    # create empty 'pending' colum for colname that does not exist.
                    progress_df[col_name] = ['pending'] * len(progress_df.index)
                    progress_df.at[tile_id, col_name] = status_value
        else:
            # if the status_csv does not exist, something must have gone wrong.
            # do not update the progress for this tile, re-process tile.
            pass
    # Status update
    print(' done.')
    # Return progress_df
    return(progress_df)


## Define function to gather logs
def gather_logs(script_name, step_name, tile_id):
    """
    Gather logs from temporary work dir. 
    This wee function is to be run out of a temporary working directory by a pool process from a multiprocessing
    workflow. It then copies all log files in the temporary working directory to the main log folder for the processing script, 
    where it stores them in a sub-subfolder according to the step_name and tile_id parameters.
    :param script_name: name of the script that is calling the function
    :param step_name: name of the step that should be logged for
    :param tile_id: tile id in the usual format (rrrr_ccc)
    :return: nothing
    """
    # Generate string for log folder for the tile and create the directory if it does not exist
    log_folder_tile = settings.log_folder + '/' + script_name + '/' + tile_id
    if not os.path.exists(log_folder_tile):
        os.mkdir(log_folder_tile)

    # Generate string for log folder and create the directory if it does not exist
    log_folder_step = log_folder_tile + '/' + step_name
    if not os.path.exists(log_folder_step):
        os.mkdir(log_folder_step)

    # Confirm function is executed from temporary work dir using regex
    wd = os.getcwd()
    temp_re = re.compile('.*temp_.*')
    if not temp_re.match(wd):
        print(datetime.datetime.now().strftime('%X') + ' Error: gather_logs function called from outside temporary work dir.')
        print(wd)
        return('Error: gather_logs.')

    # Check whether dklidar logfile exists if yes copy:
    if os.path.exists(wd + '/log.txt'):
        # copy file to tile log directory
        shutil.copy(wd + '/log.txt', log_folder_step)
        # remove log file from temp directory
        os.remove(wd + '/log.txt')

    # Check whether opalslog logfile exists if yes copy:
    if os.path.exists(wd + '/opalsLog.xml'):
        # copy file to tile log directory
        shutil.copy(wd + '/opalsLog.xml', log_folder_step)
        # remove log file from temp directory
        os.remove(wd + '/opalsLog.xml')

    # Check whether opalsError logfile exists if yes copy:
    if os.path.exists(wd + '/opalsErrors.txt'):
        # copy file to tile log directory
        shutil.copy(wd + '/opalsErrors.txt', log_folder_step)
        # remove log file from temp directory
        os.remove(wd + '/opalsErrors.txt')


## Function to generate sea and inland water masks for a tile
def generate_water_masks(tile_id):
    """
    Generates both sea and inland water mask rasters with 10 m grain size, based on the dtm as a template and the
    the nationwide sea and inland water masks vector files specified in the settings file.
    :param tile_id: id of the tile
    :return: execution status
    """

    # Initiate return valule and log output
    return_value = ''
    log_file = open('log.txt', 'a+')

    # get temporary work directory
    wd = os.getcwd()

    # Prepare output folder
    sea_out_folder = settings.output_folder + '/masks/sea_mask'
    inland_water_out_folder = settings.output_folder + '/masks/inland_water_mask'
    if not os.path.exists(settings.output_folder + '/masks'): os.mkdir(settings.output_folder + '/masks')
    if not os.path.exists(sea_out_folder): os.mkdir(sea_out_folder)
    if not os.path.exists(inland_water_out_folder): os.mkdir(inland_water_out_folder)

    sea_mask_file = sea_out_folder + '/sea_mask_' + tile_id + '.tif '
    inland_mask_file = inland_water_out_folder + '/inland_water_mask_' + tile_id + '.tif '
    temp_file = os.getcwd() + '/temp.tif'



    try:
        ## Aggregate dtm
        cmd = settings.gdalwarp_bin + \
              '-tr 10 10 -r min -ot Int16 -dstnodata -9999 -overwrite ' + \
              settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif ' + \
              temp_file

        # Execute gdal command
        log_file.write(subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' aggregating dtm to 10 m for mask successful.\n\n')

        # Set all cells with data in raster to 0 and set it as no data value
        cmd = settings.gdal_calc_bin + \
              '--calc=1 --NoDataValue=-9999 --overwrite --type Int16 ' + \
              '-A ' + temp_file + ' ' + \
              '--outfile=' + sea_mask_file

        # Execute gdal command
        log_file.write(subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' set all cells with data to 1.\n\n')

        # Dublicate file
        shutil.copyfile(sea_mask_file, inland_mask_file)

        # Make a local copies of the nationwide masks to speed up simulatneaous access
        dk_sea_mask_path = re.sub('(.*/)(.*)\.shp$', '\g<1>', settings.dk_coastline_poly)
        dk_inland_mask_path = re.sub('(.*/)(.*)\.shp$', '\g<1>', settings.dk_lakes_poly)
        dk_sea_mask_file_base = re.sub('(.*/)(.*)\.shp$', '\g<2>', settings.dk_coastline_poly)
        dk_inland_mask_file_base = re.sub('(.*/)(.*)\.shp$', '\g<2>', settings.dk_lakes_poly)

        for file in glob.glob(dk_sea_mask_path + dk_sea_mask_file_base + '.*'):
            temp_file = os.getcwd() + '/temp_' + re.sub('(.*\\\)(.*)\.*$', '\g<2>', file)
            shutil.copy(file, temp_file)
        for file in glob.glob(dk_inland_mask_path + dk_inland_mask_file_base + '.*'):
            temp_file = os.getcwd() + '/temp_' + re.sub('(.*\\\)(.*)\.*$', '\g<2>', file)
            shutil.copy(file, temp_file)

        dk_sea_mask_temp_file = os.getcwd() + '/temp_' + dk_sea_mask_file_base + '.shp'
        dk_inland_mask_temp_file = os.getcwd() + '/temp_' + dk_inland_mask_file_base + '.shp'

        # Generate sea mask
        cmd = settings.gdal_rasterize_bin + \
              '-b 1 ' + '-burn -9999 ' + '-i ' + '-at ' + \
              dk_sea_mask_temp_file + ' ' + \
              sea_mask_file
        log_file.write('\n' + \
                     subprocess.check_output(
                         cmd,
                         shell=False,
                         stderr=subprocess.STDOUT) + \
                     '\n' + sea_mask_file + ' sea mask created. \n\n ')

        # Generate inland water mask
        cmd = settings.gdal_rasterize_bin + \
              '-b 1 ' + '-burn -9999 ' + '-at ' + \
              dk_inland_mask_temp_file + ' ' + \
              inland_mask_file
        
        log_file.write('\n' + \
                     subprocess.check_output(
                         cmd,
                         shell=False,
                         stderr=subprocess.STDOUT) + \
                     '\n' + inland_mask_file + ' inland water mask created. \n\n ')

        # Remove temporary files
        temp_file_list = glob.glob(os.getcwd() + '/temp*.*')
        for file in temp_file_list: os.remove(file)

        return_value = 'success'
    except:
        log_file.write('\n' + tile_id + ' creating mask rasters failed.\n\n')
        return_value = 'gdalError'

    # Close log file
    log_file.close()

    return return_value

## Function to apply water masks, sea or inland water.
def apply_mask(target_raster = '', sea_mask = False, inland_water_mask = False):
    """
    For a given target raster, this function masks all sea off the coastline of Denmark (sea_mask = True),
    or all inland water bodies such as lakes or ponds (inland_water_mask = True) or both. 
    Requires raster masks to be generated using generate_water_masks().
    :param sea_mask: boolean switch for applying sea mask
    :param inland_water_mask: boolean switch for applying the inland water mask
    :param target_raster: target raster file path
    :return: execution status
    """
    # initiate return value and log ouptut
    return_value = ''
    log_file = open('log.txt', 'a+')

    # Check whether input raster was provided
    if (target_raster == ''): raise Exception('No input raster provided.')

    # Get current wd
    temp_wd = os.getcwd()

    # Get tile_id from path
    tile_id = re.sub('.*?_(\d*_)(\d*)(_\d*)?\.tif *', '\g<1>\g<2>', target_raster)

    # set mask paths
    sea_out_folder = settings.output_folder + '/masks/sea_mask'
    inland_water_out_folder = settings.output_folder + '/masks/inland_water_mask'
    sea_mask_file = sea_out_folder + '/sea_mask_' + tile_id + '.tif'
    inland_mask_file = inland_water_out_folder + '/inland_water_mask_' + tile_id + '.tif'

    temp_file = temp_wd + '/temp_raster.tif'
    # Apply sea mask
    if (sea_mask == True):
        try:
            # Construct gdal command
            cmd = settings.gdal_calc_bin + \
              '-A ' + sea_mask_file + ' ' + \
              '-B ' + target_raster + ' ' + \
              '--outfile=' + temp_file + ' ' + \
              '--calc=B --NoDataValue=-9999 --overwrite --type Int16 '
            
            log_file.write('\n' + \
                 subprocess.check_output(
                     cmd,
                     shell=False,
                     stderr=subprocess.STDOUT) + \
                 '\n' + target_raster + ' sea mask applied. \n\n ')

            shutil.copyfile(temp_file, target_raster)
            os.remove(temp_file)

            return_value = 'success'
        except:
            log_file.write('\n' + target_raster + ' applying sea mask failed. \n\n ')
            return_value = 'gdalError'

    # Apply lake mask
    if (inland_water_mask == True):
        try:
            # Construct gdal command
            cmd = settings.gdal_calc_bin + \
              '-A ' + inland_mask_file + ' ' + \
              '-B ' + target_raster + ' ' + \
              '--outfile=' + temp_file + ' ' + \
              '--calc=B --NoDataValue=-9999 --overwrite --type Int16 '
            
            log_file.write('\n' + \
                 subprocess.check_output(
                     cmd,
                     shell=False,
                     stderr=subprocess.STDOUT) + \
                 '\n' + target_raster + ' inland water mask applied. \n\n ')

            shutil.copyfile(temp_file, target_raster)
            os.remove(temp_file)

        except:
            log_file.write('\n' + target_raster + ' applying inland water mask failed. \n\n ')
            return_value = 'gdalError'

    if (sea_mask == False & inland_water_mask == False):
        log_file.write('\n' + target_raster + ' no masks to be applied. \n\n ')
        return_value = 'success'

    # Close log file
    log_file.close()

    return return_value
