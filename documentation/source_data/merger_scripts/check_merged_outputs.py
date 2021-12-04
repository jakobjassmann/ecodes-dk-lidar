## EcoDes-DK output merger
## This script is used to merge the outputs of the various EcoDes processing
## runs to create the merged dataset based on the DHM_201415 merger.
## Jakob J. Assmann jakobjassmann@gmail.com

# Dependencies
import os
import shutil
import pandas
import glob
import re
import scandir
import hashlib

# Status
print('#' * 80)
print('Check MD5 sums of merged EcoDes-DK outputs from the different reprocessing batches.')
print('\nPreparing environment...'),

## 1) Set global variables

# tile_ids to source
tiles_to_source_original_processing = pandas.read_csv('D:/Jakob/dhm201415_merger/tiles_from_DHM2018.csv')
tiles_to_source_reprocessing_1 = pandas.read_csv('D:/Jakob/dhm201415_merger/tiles_from_DHM2015.csv')
tiles_to_source_reprocessing_2 = pandas.read_csv('D:/Jakob/dhm201415_merger/tiles_to_process_dhm201415_merger.csv')
tiles_incomplete = pandas.read_csv('D:/Jakob/dhm201415_merger/incomplete_tile_pairs.csv')

# Remove incomplete tiles from tile_ids
tiles_to_source_original_processing = pandas.DataFrame(
    set(tiles_to_source_original_processing['tile_id'].tolist()) -
    set(tiles_incomplete['tile_id'].tolist()),
    columns = ['tile_id'])
tiles_to_source_reprocessing_1 = pandas.DataFrame(
    set(tiles_to_source_reprocessing_1['tile_id'].tolist()) -
    set(tiles_incomplete['tile_id'].tolist()),
    columns = ['tile_id'])
tiles_to_source_reprocessing_2 = pandas.DataFrame(
    set(tiles_to_source_reprocessing_2['tile_id'].tolist()) -
    set(tiles_incomplete['tile_id'].tolist()),
    columns = ['tile_id'])

# Remove redundancies
tiles_to_source_original_processing = pandas.DataFrame(
    set(tiles_to_source_original_processing['tile_id'].tolist()) -
    set(tiles_to_source_reprocessing_2['tile_id'].tolist()),
    columns = ['tile_id'])
tiles_to_source_reprocessing_1 = pandas.DataFrame(
    set(tiles_to_source_reprocessing_1['tile_id'].tolist()) -
    set(tiles_to_source_reprocessing_2['tile_id'].tolist()),
    columns = ['tile_id'])

# source folders
folder_original_processing = 'D:/Jakob/dk_nationwide_lidar/data/outputs'
folder_reprocessing_1 = 'D:/Jakob/ecodes-dk-lidar/data/outputs'
folder_reprocessing_2 = 'D:/Jakob/ecodes-dk-lidar-reprocessing/data/outputs'

# destination folder
dest_folder = 'D:/Jakob/ecodes-dk-lidar-rev1/data/outputs'

# base folders
dtm_files = 'D:/Jakob/ecodes-dk-lidar-reprocessing/data/dtm'
laz_files = 'D:/Jakob/ecodes-dk-lidar-reprocessing/data/laz'

# determine output folder structure based on original processing
folders = [] 
for folder in scandir.scandir(folder_original_processing):
    if folder.is_dir():
        sub_folders = [sub_folder.path for sub_folder in scandir.scandir(folder.path) if sub_folder.is_dir()]
        if len(sub_folders) > 0:
            for sub_folder in sub_folders:
                folders.append(sub_folder)
        else:
            folders.append(folder.path)

# remove variables that were / will be separately reprocessed (if present)
folders = [folder for folder in folders if not bool(re.match('.*tile_footprints.*', folder))]
folders = [folder for folder in folders if not bool(re.match('.*solar_radiation.*', folder))]
folders = [folder for folder in folders if not bool(re.match('.*date_stamp.*', folder))]

# Clean up file paths
folders = map(lambda folder: re.sub('\\\\', '/', folder), folders)

# Keep only relative paths
folders = map(lambda folder: '/' + os.path.relpath(folder,
                                             folder_original_processing),
              folders)

###!!! Break(s) for debugging !!!
##folders = [folders[1]]
##folders = ['/point_source_info/point_source_counts']

## 2) Function definitons
def list_files(folder_path):
    files = []
    # Scan directory
    for file_name in scandir.scandir(folder_path):
        files.append(file_name.name)
    return(files)

def get_tile_ids(file_names):
    # initiate empty list for tile_ids
    tile_ids = []
    # clean up files names
    for i in range(0, len(file_names)):
        file_names[i] = re.sub('\\\\', '/', file_names[i])
    # fill list with tile_id
    for file_name in file_names:
        tile_id = re.sub('.*(\d{4}_\d{3}).*', '\g<1>', file_name)
        tile_ids.append(tile_id)
    # combine to data frame
    files_df = pandas.DataFrame(zip(*[tile_ids, file_names]),
                                columns = ['tile_id', 'file_name'])
    # return files_df
    return(files_df)

def compare_tile_dfs(df1, df2):
    if(set(df1['tile_id'].tolist()) ==
       set(df2['tile_id'].tolist())):
       return(pandas.DataFrame([], columns = ['tile_id']))
    else:
       diff = pandas.DataFrame(
           set(df1['tile_id'].tolist()) -
           set(df2['tile_id'].tolist()),
           columns = ['tile_id'])
    return(diff)

def check_var_from_source(var_folder, tiles_df, source_folder):
    # Get all files for one variable from one source
    # Set dest directory based on global variable
    global dest_folder
    out_folder = dest_folder + var_folder
    # Set source folder
    source_folder = source_folder + var_folder
    # Generate df of tile_ids and file names
    files_to_check = get_tile_ids(list_files(source_folder))
    # check files
    check_df = check_tiles(tiles_df, files_to_check, source_folder, out_folder)
    return(check_df)

def check_var(var_folder):
    # Get global variables
    global tiles_to_source_original_processing, tiles_to_source_reprocessing_1, tiles_to_source_reprocessing_2, folder_original_processing, folder_reprocessing_1, folder_reprocessing_2
        
    # Get all files for one variable from the three data sources
    print('Checking: ' + var_folder)
    print('\tOriginal processing')
    original_check = check_var_from_source(var_folder,
                        tiles_to_source_original_processing,
                        folder_original_processing)
    print('\n\tReprocessing #1')
    reprocessing_1_check = check_var_from_source(var_folder,
                        tiles_to_source_reprocessing_1,
                        folder_reprocessing_1)
    print('\n\tReprocessing #2')
    reprocessing_2_check = check_var_from_source(var_folder,
                        tiles_to_source_reprocessing_2,
                        folder_reprocessing_2)
    # Return df of copied tiles and 
    files_with_errors = pandas.concat([original_check,
                                       reprocessing_1_check,
                                       reprocessing_2_check])
    files_with_errors['variable'] = var_folder
    print('\tDone.\n')
    return(files_with_errors)

# The function below is thanks to stackoverflow usesrs quantumSoup and user2653663
# https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def check_tiles(tiles_to_check, files_df, source_folder, out_folder):
    # Subset files to check
    files_to_check = files_df[files_df['tile_id'].
                             isin(tiles_to_check['tile_id'].tolist())]['file_name'].tolist() 
    # initate output lists
    files = []
    status = []

    # Set counter to 0:
    progress = 0
    
    # Check files
    for i in range(0, len(files_to_check)):
          # Check whether files exists
          if os.path.isfile(source_folder + '/' + files_to_check[i]):
                if os.path.isfile(out_folder + '/' + files_to_check[i]): 
                    match = md5(source_folder + '/' + files_to_check[i]) == md5(out_folder + '/' + files_to_check[i])
                    if not match:
                        files.append(files_to_check[i])
                        status.append('md5_mismatch')
                else:
                    files.append(files_to_check[i])
                    status.append('out_file_missing')
          else:
              files.append(files_to_check[i])
              status.append('source_file_missing')
          # Update progress
          progress = float(i + 1) / float(len(files_to_check))
          # Update progress bar
          print('\r\t|' +
                '-' * int(round(progress * 54)) +
                ' ' * int(round((1 - progress) * 54)) +
                '| ' +
                str(int(round(progress * 100))) + '%'),
    # Compile outputs to dataframe and retun
    status_df = pandas.DataFrame(zip(*[files, status]), columns = ['file_name','status'])
    return(status_df)

# Status
print(' done.\n')

## 3) Main body of script

## Check completeness of tile lists
# Status
print('Checking completness of tile list to check...'),

# Get all tiles in data set
dhm_merged_tiles = get_tile_ids(list_files(laz_files))

# Compare with tiles to merge
missing_tiles = len(compare_tile_dfs(dhm_merged_tiles,
                 pandas.concat([tiles_to_source_original_processing,
                                tiles_to_source_reprocessing_1,
                                tiles_to_source_reprocessing_2])))
if missing_tiles > 0:
    # Prompt for choice to stop
    del_choice = raw_input('\n' + str(missing_tiles) + ' are missing! Continue anyways?' +
                       '[y/n]')
    if not del_choice == 'y':
        print('Aborting on request or invalid choice!')
        quit()
    else:
        print('Okay, continuing merger.')
else:
    print('\n=> Sets are complete, proceeding as planned.\n')
  
## Check tiles for all variables

# Status
print('Starting check:\n\n')

files_checked_dfs = []
for var_folder in folders:
    files_copied_df = check_var(var_folder)
    files_checked_dfs.append(files_copied_df)

files_checked_df = pandas.concat(files_checked_dfs)
files_checked_df.to_csv('checkusm_errors.csv', index = False)
# Stauts
print('Check complete!\n')
print('#' * 80 + '\n')
 
# EOF



    
