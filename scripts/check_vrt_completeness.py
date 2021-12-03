# EcoDes-DK15 check validity of outputs based on whether gdal can open the file.
# Jakob J. Assmann j.assmann@bio.au.dk 2 December 2021

# Dependencies
import scandir
import pandas
import re
import os
import tqdm
import itertools
import multiprocessing
from osgeo import gdal
from dklidar import settings

# Switch on gdal Python exceptions
gdal.UseExceptions()

## 1) Function definitions
# Check file function
def check_vrt_completeness(folder):
    var_name = re.sub('.*/(.*)$', '\g<1>', folder)
    vrt_file_name = folder + '/' + var_name + '.vrt'
    file_names = []
    status = []
    # Check presence of vrt file
    if os.path.exists(vrt_file_name):
        # Open file
        vrt_file = open(vrt_file_name, 'r')
        # Read content
        vrt_file_contents = ''.join(vrt_file.readlines())
        # List folder content
        file_list = list_files(folder)
        # drop non tif files from list
        file_list = list(itertools.compress(
            file_list,
            [bool(re.search('tif', x)) for x in file_list]))
        # Search tif files in vrt
        #progress = 0
        for i in range(0, len(file_list)):
            if not bool(re.search(
                re.sub('.*/(.*)$', '\g<1>', file_list[i]),
                vrt_file_contents)):
                file_names.append(re.sub('.*/(.*)$', '\g<1>', file_list[i]))
                status.append('missing')
##            # Update progress
##            progress = float(i + 1) / float(len(file_list))
##            # Update progress bar
##            print('\r|' +
##                  '#' * int(round(progress * 54)) +
##                  '-' * int(round((1 - progress) * 54)) +
##                  '| ' +
##                  str(int(round(progress * 100))) + '%'),
    else:
        file_names.append('')
        status.append('vrt file missing')
    # Combined outputs to df
    status_check_df = pandas.DataFrame(zip(*[file_names, status]),
                                columns = ['file_name','error'])
    status_check_df['variable'] = var_name
    return(status_check_df)

def list_files(folder_path):
    files = []
    # Scan directory
    for file_name in scandir.scandir(folder_path):
        files.append(folder_path + '/' + file_name.name)
    return(files)

if __name__ == '__main__':
    ## 2) Prepare environment
    
    # Status
    print('#' * 80 + '\n')
    print('Checking EcoDes-DK15 vrts for completeness\n\n')
    print('Preparing environment... '),

    # determine output folder structure based on original processing
    folders = [] 
    for folder in scandir.scandir(settings.output_folder):
        if folder.is_dir():
            sub_folders = [sub_folder.path for sub_folder in scandir.scandir(folder.path) if sub_folder.is_dir()]
            if len(sub_folders) > 0:
                for sub_folder in sub_folders:
                    folders.append(sub_folder)
            else:
                folders.append(folder.path)
    # Clean up folder paths
    folders = map(lambda folder: re.sub('\\\\', '/', folder), folders)
        
    # Status
    print('done.'),
    print('Checking vrts... '),

    # Run file checks in parallel
    multiprocessing.set_executable(settings.python_exec_path)
    pool = multiprocessing.Pool(processes=62)
    file_checks = list(tqdm.tqdm(pool.imap_unordered(check_vrt_completeness, folders),
                                 total = len(folders)))
    # Concatenate into one dataframe
    status_df = pandas.concat(file_checks)

    # Write to file
    status_df.to_csv(settings.log_folder + '/missing_files_in_vrts.csv',
                     index = False)

    # Status
    print('done.'),
    print('\nFound ' + str(len(status_df.index)) + ' missing files.')
    print('Check log file for names of missing files:\n\t' +
          settings.log_folder + '/missing_files_in_vrts.csv')

# End of File
