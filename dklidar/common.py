### Common module for the dklidar reporcessing - general functions likely used by all scripts
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

# Imports
import settings
import os
import glob
import pandas
import re
import shutil
import datetime

## Function definitons

def init_log_folder(script_name, tile_ids):
    """
    Initiates a log folder for storing the processing output and progress management
    :param tile_ids: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: pandas DataFrame with progress data.
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

def update_progress_df(script_name, progress_df):
    """
    Searches a script's log folder for subfolders matching the tile_id_pattern(rrrr_ccc), then crawls these folders for
    status.csv files, compiling them into one pandas datafram and retutning it.
    :param script_name: name of the script (for folder matching), progress_df: progress dataframe to be updated
    :return: returns updated progress_df
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
    This wee function needs to be run out of a temporary working directory by a pool process from the multiprocessing
    module. It then copies all log files in the temporary working directory to the log folder, where it stores them
    in a sub-subfolder according to the step_name and tile_id parameters
    :param script_name: name of the script that is calling the function.
    :param step_name: name of the step that should be logged for
    :param tile_id: tile id in the usual format (rrrr_ccc).
    :return: nothing.
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


