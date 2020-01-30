### Common module for the dklidar reporcessing - general functions likely used by all scripts
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

# Imports
import settings
import os
import pandas

## Function definitons

def init_log_folder(script_name, tile_ids, processing_steps):
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
        # Add tile_id column
        cols.append(tile_ids)
        # Add processing status column
        cols.append(['pending'] * len(tile_ids))
        # Add status colmuns for each step
        for steps in processing_steps:
            cols.append(['pending'] * len(tile_ids))
        # prepare colnames
        colnames = ['tile_id', 'processed']
        colnames.extend(processing_steps)
        # Zip into pandas data frame
        progress_df = pandas.DataFrame(zip(*cols), columns = colnames)
        # Export as CSV
        progress_df.to_csv(progress_file, index = False, header = True)
    else:
        print('Progress file found, loading previous processing status...'),
        ## Load progress status_file
        try:
            progress_df = pandas.read_csv(progress_file)
        except:
            print('\nCan\'t load progress file. Exiting script!')
            quit()
        # Compare tile_id column with tile_ids list
        if not progress_df['tile_id'].tolist() == tile_ids:
            print('\nWarning: lists of tile_ids in laz folder( ' + settings.laz_folder +
                  ') and progress file (' + progress_file + 'do not match.' +
                  '\nPlease remove manually to reset.\nExiting script!')
            quit()
    print(' done.')
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