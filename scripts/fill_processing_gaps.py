# fix_processing_gaps.py
# short script to fix missing tiles for each variable
# to be run post completion of processing with process_tiles.py
# Jakob Assmann j.assmann@bios.au.dk 11 May 2021

# NB: uses scandir for speed, on OPALS Shell an install might be required with
# python -m pip install scandir --user

# Dependencies
import os
import glob
import pandas
import re
import scandir
import copy
import sys
import subprocess
import shutil
from dklidar import settings

## 1) Determine output folder structure

# Status
print('#' * 80 + 'Check EcoDes-DK processing outputs for completness' + '\n\n')
print('Preparing environment...'),

# Initiate list
folders = []

# Check for subfolders present (max depth = 1)
for folder in scandir.scandir(settings.output_folder):
    if folder.is_dir():
        sub_folders = [sub_folder.path for sub_folder in scandir.scandir(folder.path) if sub_folder.is_dir()]
        if len(sub_folders) > 0:
            for sub_folder in sub_folders:
                folders.append(sub_folder)
        else:
            folders.append(folder.path)
            
# Remove tile_footprints folder if present
folders = [folder for folder in folders if not bool(re.match('.*tile_footprints.*', folder))]
folders = [folder for folder in folders if not bool(re.match('.*point_source_proportion.*', folder))]
folders = [folder for folder in folders if not bool(re.match('.*point_source_counts.*', folder))]

## Get reference set of tiles based on dtm_10m
dtm_10m = [folder for folder in folders if bool(re.match('.*dtm_10m.*', folder))][0]
dtm_10m_tiles = [re.sub('.*_(\d*_\d*).tif', '\g<1>', file_name) for file_name in glob.glob(dtm_10m + '/*.tif')]
dtm_10m_tiles = set(dtm_10m_tiles)

print(' done.')

## 2) Check completeness of tiles for all variables
# Status
print('Scanning tiles for...')

# Initiate empty dictionary
missing_tiles = {}

# Scan folders for missing tiles
for folder in folders:
    variable_name = re.sub('.*[\\\\\/]', '', folder)
    print('\t' + variable_name)
    tiles = [re.sub('.*_(\d*_\d*).tif', '\g<1>', file_name) for file_name in glob.glob(folder + '/*.tif')]
    tiles = set(tiles)
    tiles_missing = dtm_10m_tiles - tiles
    missing_tiles.update({variable_name: tiles_missing})

# Status
print('Scan complete.\n')
print('Exporting missing tile_ids to csv...'),

# Save missing tiles for each variable to csv
missing_tiles_df_list = []
for variable in missing_tiles.keys():
    missing_diles_df_local = pandas.DataFrame(missing_tiles[variable], columns = ['tile_id'])
    missing_diles_df_local['variable'] = variable
    missing_tiles_df_list.append(missing_diles_df_local)

# Concatenate list of dfs into one df and export to csv
missing_tiles_df = pandas.concat(missing_tiles_df_list)
missing_tiles_df.to_csv(settings.wd + '/documentation/empty_tile_ids.csv', index = False)

# Status
print(' done.')

## 3) Generate empty tiles for all missing tile ids

# Plenty of overlap means this is faster to do once then just copy

# Make temp dir
os.mkdir(settings.scratch_folder + '/fill_temp')
# Get unique tile ids
unique_missing_tiles = [tile_id for tile_list in missing_tiles.values() for tile_id in tile_list]
unique_missing_tiles = set(unique_missing_tiles)

# Status
print('Generating ' + str(len(unique_missing_tiles)) + ' empty tiles in temp folder...')

# Generate empty tiles using gdal
for tile_id in unique_missing_tiles:
    in_file = dtm_10m + '/dtm_10m_' + tile_id + '.tif'
    out_file = settings.scratch_folder + '/fill_temp/' + "empty_" + tile_id + '.tif'
    cmd = settings.gdal_calc_bin + ' -A ' + in_file + ' --outfile ' + out_file + ' --calc=(-9999*greater(A,-9999)) --type=Int16 --NoDataValue=-9999'
    call_return = subprocess.check_output(cmd, shell=False)
    sys.stdout.write('.')
    sys.stdout.flush()

# Status
print(' done.')

## 4) Perpare summary oputput and fill missing rasters

# Status
print('Generating stummary stats...'),

# Duplicate missing_tiles dict for summary stats
summary_stats = copy.copy(missing_tiles)

# Loop through key value pairs, get stats and write missing NA rasters
for variable, tiles_missing in missing_tiles.items():
    # Status
    print(variable + ' with ' + str(len(tiles_missing)) + ' tiles.')
    # Determine output folder
    output_folder = [folder for folder in folders if bool(re.match('.*[^_]' + variable + '.*', folder))][0]
    # Set summary stats
    summary_stats[variable] = len(tiles_missing)
    # Fill missing NA rasters if needed
    if len(tiles_missing)>0:
        for tile_id in tiles_missing:
            source = settings.scratch_folder + '/fill_temp/' + "empty_" + tile_id + '.tif'
            destination = output_folder + '/' + variable + "_" + tile_id + '.tif'
            if not os.path.exists(destination):
                shutil.copy(source, destination)
            else:
                print('Warning: file already exists')
    # Write summary stats to text file
    stats_file = open(output_folder + '/empty_tiles_' + variable + '.txt', 'w')
    stats_file.write(variable + '\n' + '' + str(len(tiles_missing)) + ' tiles did not complete processing and were replaced with empty tiles (all values = NA).\nThe affected tile_ids are:\n' + '\n'.join(list(tiles_missing)) + '\n')
    stats_file.close()

# Status
print(' done.')
print('Exporting summary stats to csv...'),

# Export stats as csv
summary_stats_df = pandas.DataFrame()
summary_stats_df['variable'] = summary_stats.keys()
summary_stats_df['n_missing_tiles'] = summary_stats.values()
summary_stats_df = summary_stats_df.sort_values('variable')
summary_stats_df.to_csv(settings.wd + '/documentation/empty_tiles_summary.csv', index=False)

# Status
print(' done.')
print('Cleaning up temp files...'),

# Remove temp files
for tile_id in unique_missing_tiles:
    temp_file = settings.scratch_folder + '/fill_temp/' + "empty_" + tile_id + '.tif'
    os.remove(temp_file)
os.rmdir(settings.scratch_folder + '/fill_temp/')

# Status
print(' done.')
print('Script complete.' + '\n' + 80 * '#')

## End of File


   

