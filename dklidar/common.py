### Common module for the dklidar reporcessing - general functions likely used by all scripts
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

# Imports
import settings
import os
import glob
import pandas
import re

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
        print('No progress file found, generating log folder and progress file...'),
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
        print('Progress file found, loading previous processing status...'),
        ## Load progress status_file
        try:
            progress_df = pandas.read_csv(progress_file, index_col='tile_id')
            print(' done.')
            # update progress dataframe
            progress_df = update_progress_df(script_name, progress_df)
        except:
            print('\nCan\'t load progress file. Exiting script!')
            quit()
        # Compare tile_id column with tile_ids list
        if not progress_df.index.values.tolist() == tile_ids:
            print('\nWarning: lists of tile_ids in laz folder( ' + settings.laz_folder +
                  ') and progress file (' + progress_file + 'do not match.' +
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
    print('Updating progress management...'),

    # Check log root folder for script if not existing... quit!
    log_folder = settings.log_folder + '/' + script_name
    if not os.path.exists(log_folder):
        print('\nWarning: script log folder does not exist. Exiting script')
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
def update_logs(step_name, tile_id):
    # Generate string for log folder

    print('test')



## Define function to gather logs... (DEPRICATED)
def gather_logs_old(n_processes, global_log_file, global_opalsLog = None, global_opalsErrors = None):
    """
    WARNING: Depricated!
    Small helper to gather all logs from the parallel processes and append them to the global log file.
    :param n_processes: number of processes to search for in scratch folder
    :param global_log_file: file connection to global log_file
    :param global_opalsLog: file connection to global opalsLog file (default = None)
    :param global_opalsErrors: file connection to global opalsErrors file (default = None)
    :return: Nothing.
    """
    for pid in range(1, n_processes):
        # Check whether log file exists
        # Generate string to temp folder of process
        temp_folder = settings.scratch_folder + '/temp_' + str(pid)
        if os.path.exists(temp_folder + '/log.txt'):
            # Open connection to process log file and read
            log_file = open(temp_folder + '/log.txt', 'r')
            log_text = log_file.read()
            # Write log text to global log file
            global_log_file.write('\n\n!!! SOF Log for pid ' + str(pid) + ':\n' +
                              log_text +
                              '\n\n!!! EOF Log for pid ' + str(pid) + '.\n')
            # Close process log file
            log_file.close()
            # Remove temporary log file for process
            os.remove(temp_folder + '/log.txt')
        else:
            # Write log text to global log file
            global_log_file.write('\n\n!!! SOF Log for pid ' + str(pid) + ':\n' +
                              'File does not exists.' +
                              '\n\n!!! EOF Log for pid ' + str(pid) + '.\n')

        # Check whether opalsLog file connection was supplied
        if not global_opalsLog is None:
            if os.path.exists(temp_folder + '/opalsLog.xml'):
                # Open connection to process Log file and read
                opalsLog_file = open(temp_folder + '/opalsLog.xml', 'r')
                opalsLog_text = opalsLog_file.read()
                # Write log text to global log file
                global_opalsLog.write('\n\n!!! SOF opalsLog.xml for pid ' + str(pid) + ':\n' +
                                  opalsLog_text +
                                  '\n\n!!! EOF opalsLog.xmlo for pid ' + str(pid) + '.\n')
                # Close process opalsLog file
                opalsLog_file.close()

                # Remove temporary log file for process
                os.remove(temp_folder + '/opalsLog.xml')
            else:
                # Write log text to global log file
                global_log_file.write('\n\n!!! SOF opalsLog.xml for pid ' + str(pid) + ':\n' +
                                'File does not exists.' +
                                '\n\n!!! EOF opalsLog.xml for pid ' + str(pid) + '.\n')

        # Check whether opalsError file connection was supplied

        if not global_opalsLog is None:
            if os.path.exists(temp_folder + '/opalsLog.xml'):
                # Open connection to process Log file and read
                opalsErrors_file = open(temp_folder + '/opalsErrors.txt', 'r')
                opalsErrors_text = opalsErrors_file.read()
                # Write log text to global log file
                global_opalsErrors.write('\n\n!!! SOF opalsErrors for pid ' + str(pid) + ':\n' +
                                     opalsErrors_text +
                                     '\n\n!!! EOF opalsErros for pid ' + str(pid) + '.\n')
                # Close process opalsLog file
                opalsErrors_file.close()

                # Remove temporary log file for process
                os.remove(temp_folder + '/opalsErrors.txt')
            else:
                # Write log text to global log file
                global_log_file.write('\n\n!!! SOF opalsErrors.txt for pid ' + str(pid) + ':\n' +
                                      'File does not exists.' +
                                      '\n\n!!! EOF opalsErrors.txt for pid ' + str(pid) + '.\n')