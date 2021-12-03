# EcoDes-DK15 check validity of outputs based on whether gdal can open the file.
# Jakob J. Assmann j.assmann@bio.au.dk 2 December 2021

# Dependencies
import scandir
import pandas
import re
import tqdm
from osgeo import gdal
import multiprocessing
from dklidar import settings

# Switch on gdal Python exceptions
gdal.UseExceptions()

## 1) Function definitions
# Check file function
def check_file(file_name):
    file_path = []
    error = []
    try:
        gtif = gdal.Open(file_name)
        gtif = None
    except RuntimeError, e:
        file_path.append(file_name)
        error.append(e)
    return(pandas.DataFrame(zip(*[file_path, error]),
                            columns = ['file_name','error']))

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
    print('Validating EcoDes-DK15 outputs through a gdal load\n\n')
    print('Preparing environment...'),

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

    # Scan files
    file_lists = [list_files(folder) for folder in folders]
    file_list = [file_name for file_list in file_lists for file_name in file_list]
    # break for debug:
    file_list = file_list
    # Status print check - if needed
    print(' done.\n')
    #print('\n')
    #print(''.join(map(lambda folder: folder + '\n', folders)))
    print('Checking ' + str(len(folders)) + ' output folders.')
    print('Containing: ' + str(len(file_list)) + ' files.\n')

    # Run file checks in parallel
    multiprocessing.set_executable(settings.python_exec_path)
    pool = multiprocessing.Pool(processes=62)
    file_checks = list(tqdm.tqdm(pool.imap_unordered(check_file, file_list),
                                 total = len(file_list)))
    # Concatenate into one dataframe
    errors_df = pandas.concat(file_checks)

    # Write to file
    errors_df.to_csv(settings.log_folder + '/output_file_erros.csv', index = False)

    # Status
    print('\nFound ' + str(len(errors_df.index)) + ' errors.')
    print('Check log file for errors:\n\t' +
          settings.log_folder + '/output_file_erros.csv')

# End of File
