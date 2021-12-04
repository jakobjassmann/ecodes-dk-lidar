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

# Status
print('#' * 80)
print('Merging EcoDes-DK outputs from the different reprocessing batches.')
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
##folders = [folders[0]]
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
          
def copy_tiles(tiles_to_copy, files_df, source_folder, out_folder):
    # Subset files to copy
    files_to_copy = files_df[files_df['tile_id'].
                             isin(tiles_to_copy['tile_id'].tolist())]['file_name'].tolist() 
    # Set counter to 0:
    progress = 0 
    # Copy files
    for i in range(0, len(files_to_copy)):
          # Check whether file exists, if not copy
          if not os.path.isfile(out_folder + '/' + files_to_copy[i]):
                # Copy file
                shutil.copy(source_folder + '/' + files_to_copy[i],
                            out_folder + '/' + files_to_copy[i])
          # Update progress
          progress = float(i + 1) / float(len(files_to_copy))
          # Update progress bar
          print('\r\t|' +
                '-' * int(round(progress * 54)) +
                ' ' * int(round((1 - progress) * 54)) +
                '| ' +
                str(int(round(progress * 100))) + '%'),

def check_dir(folder_path):
    # Check if dir exists
    if os.path.exists(folder_path): return(0)
    # Determine file path components and check filpath from root to end
    subfolders = [folder_path]
    current_dir = folder_path
    while not current_dir  == (os.path.splitdrive(folder_path)[0] + '/'):
        parent_dir = os.path.dirname(current_dir)
        subfolders.append(parent_dir)
        current_dir = parent_dir
    subfolders = subfolders[::-1][1:len(subfolders)]
    for folder in subfolders:
        if not os.path.exists(folder): os.mkdir(folder)
    return(0)

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

def get_var_from_source(var_folder, tiles_df, source_folder):
    # Get all files for one variable from one source
    # Set dest directory based on global variable
    global dest_folder
    out_folder = dest_folder + var_folder
    #  and create if needed
    check_dir(out_folder)
    # Set source folder
    source_folder = source_folder + var_folder
    # Generate df of tile_ids and file names
    files_to_copy = get_tile_ids(list_files(source_folder))
    # Copy files
    copy_tiles(tiles_df, files_to_copy, source_folder, out_folder)
    return(0)

def get_var(var_folder):
    # Get global variables
    global tiles_to_source_original_processing, tiles_to_source_reprocessing_1, tiles_to_source_reprocessing_2, folder_original_processing, folder_reprocessing_1, folder_reprocessing_2
        
    # Get all files for one variable from the three data sources
    print('Sourcing: ' + var_folder)
    print('\tOriginal processing')
    get_var_from_source(var_folder,
                        tiles_to_source_original_processing,
                        folder_original_processing)
    print('\n\tReprocessing #1')
    get_var_from_source(var_folder,
                        tiles_to_source_reprocessing_1,
                        folder_reprocessing_1)
    print('\n\tReprocessing #2')
    get_var_from_source(var_folder,
                        tiles_to_source_reprocessing_2,
                        folder_reprocessing_2)
    # Return df of copied tiles and 
    files_copied = get_tile_ids(list_files(dest_folder + var_folder))
    files_copied['var_folder'] = var_folder
    print('\tDone.\n')
    return(files_copied)

# Status
print(' done.\n')

## 3) Main body of script

## Check completeness of tile lists
# Status
print('Checking completness of tile list to copy...'),

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
  
## Copy tiles for all variables

# Status
print('Starting merger:\n\n')

files_copied_dfs = []
for var_folder in folders:
    files_copied_df = get_var(var_folder)
    files_copied_dfs.append(files_copied_df)

# Stauts
print('Merger complete!\n')
print('#' * 80 + '\n')

## Quality control

# Status
print('Quality control:\n')

# Quality control:
files_missing_dfs = []
for files_copied_df in files_copied_dfs:
    # Get tiles missed in copying (e.g. due to absence in source)
    files_missing_df = compare_tile_dfs(dhm_merged_tiles,
                                        files_copied_df)
    if len(files_missing_df) > 0:
        # Status
        print('\t' +
              files_copied_df['var_folder'][1] +
              ' is missing: ' +
              str(len(files_missing_df)) +
              ' tiles.\n')
        # Add missing tiles to list
        files_missing_df['var_folder'] = files_copied_df['var_folder'][1]
        files_missing_dfs.append(files_missing_df)
    else:
        # Status
        print('\t' + files_copied_df['var_folder'][1] + ' complete.\n')

files_missing_dfs = pandas.concat(files_missing_dfs)
files_missing_dfs.to_csv('final_merger_missing_files.csv', index = False)

# Status
print('A total of ' + str(len(files_missing_dfs)) + ' files are missing.\n')
print('Quality control complete.\n')
print('Merger complete.\n')
print('#' * 80 + '\n')
 
# EOF



    
