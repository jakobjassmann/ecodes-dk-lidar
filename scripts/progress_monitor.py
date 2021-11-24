### Script to mointor progress of the process_tiles.py script
### Execute in separate terminal in when running process_tile.py
### Jakob Assmann j.assann@bios.au.dk 20 April 2020

## Imports
import glob
import os
import datetime
import time

from dklidar import settings

# Set working directory
os.chdir(settings.wd)

# Set number of parallel processes:
n_processes = 62 # 54

# set update interval
update_interval = 60 # 60 s

# Load tile file names and derive total number of files to process
laz_files = glob.glob(settings.laz_folder + '/*.laz')
n_total = len(laz_files)

# Check nubmer of files already processed
n_processed_at_start = len(glob.glob(settings.log_folder + '/process_tiles/*_*'))

# set start date and time:
start_time = datetime.datetime.fromtimestamp(os.path.getmtime(settings.log_folder + '/process_tiles/overall_progress.csv'))
# Initate progress variables
progress = 0

# Update progress till complete
while progress < 1:
    # Obtain n sum of n tiles in process and completed
    n_sum = len(glob.glob(settings.log_folder + '/process_tiles/*_*'))
    # Calculate n of fully processed tiles
    n_processed = n_sum - n_processes
    progress = float(n_processed) / float(n_total)

    # Calculate time differences
    time_passed = datetime.datetime.now() - start_time
    if (n_processed - n_processed_at_start) <= 54:
        time_estimated = 'estimating'
    else:
        time_estimated = (time_passed / (n_processed - n_processed_at_start)) * (n_total - n_processed)


    # Check whether the overall_progress.csv has been updated, if so
    # assume the processing of the last 54 files is done
    overal_progress_timestamp = datetime.datetime.fromtimestamp(
        os.path.getmtime(settings.log_folder + '/process_tiles/overall_progress.csv'))
    if not overal_progress_timestamp == start_time:
        progress = 1
        n_processed = n_total

    # Print stats on screen
    os.system('cls')
    print('\n')
    print('-' * 80),
    print(' ' * (79 - len('Jakob Assmann j.assmann@bios.au.dk 2020 ')) +
          'Jakob Assmann j.assmann@bios.au.dk 2020 ')
    print(' \'process_tiles.py\' progress:')
    print('  - processing with ' + str(n_processes) + ' parallel threads')
    print('  - start time: ' + str(start_time.ctime()))
    print('  - execute \'stop.bat\' to pause \ interrupt processing')
    print('\n')
    print(' update interval: ' + str(update_interval) + ' s' +
          ' ' * (79 - len(' update interval: ' + str(update_interval) + ' s' + 'last update: ' + str(datetime.datetime.now().ctime()))) +
          'last update: ' + str(datetime.datetime.now().ctime()))
    print('-' * 80)
    print('\n' * 2)
    print(' ' + str(n_processed) + ' / ' + str(n_total) + ' tiles' +
          ' ' * (80 - len(' ' + str(n_processed) + ' / ' + str(n_total) + ' tiles' + str(int(round(progress * 100))) + '% ')) +
          str(int(round(progress * 100))) + '%'),
    print('-' * 80),
    print('#' * int(round(78*progress)))
    print('-' * 80),
    print('passed: ' + str(time_passed).split('.')[0] +
          ' ' * (79 - len('passed: ' + str(time_passed).split('.')[0] +
                          'remaining (estimate): ' + str(time_estimated).split('.')[0] + ' ')) +
          'remaining (estimate): ' + str(time_estimated).split('.')[0] + ' ')
    print(' ' * (79 - len('press CRTL+C to exit progress monitor ')) + 'press CRTL+C to exit progress monitor ')

    # Wait for next update
    time.sleep(update_interval)

    # End of while loop

