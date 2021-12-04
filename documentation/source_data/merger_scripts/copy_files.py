## DHM2018+ and DHM2015 merger
## Script to copy the files and create a physical version of the merger
## using the outputs from dhm201415_merger.R
## Jakob J. Assmann j.assmann@bio.au.dk

## Dependencies
import os
import shutil
import pandas
import glob
import re

## Status
print('\n' + '#' * 80)
print('Merging DHM2018+, DHM2015 and GST2014\n')
print('Setting up work environment...')

## Prepare environment
# Set wd
os.chdir('D:/Jakob/dhm201415_merger/')

# Set file paths
gst2014_laz = 'O:/Nat_Ecoinformatics/B_Read/LegacyData/Denmark/Elevation/GST_2014/Punktsky/laz/'
dhm2015_laz = 'D:/Jakob/datafordeler_downloads/DHM2015_punktsky'
dhm2018_laz = 'D:/Jakob/dk_nationwide_lidar/data/laz'
gst2014_dtm = 'O:/Nat_Ecoinformatics/B_Read/LegacyData/Denmark/Elevation/GST_2014/DTM_tif'
dhm2015_dtm = 'D:/Jakob/datafordeler_downloads/DHM2015_terraen'
dhm2018_dtm = 'D:/Jakob/dk_nationwide_lidar/data/dtm'
laz_out = 'laz/'
dtm_out = 'dtm/'
os.mkdir(laz_out)
os.mkdir(dtm_out)

# Load tile_ids to source from DHM2015
gst2014_tile_ids = pandas.read_csv('tiles_from_GST2014.csv')

# Load tile_ids to source from DHM2015
dhm2015_tile_ids = pandas.read_csv('tiles_from_DHM2015.csv')

# Load tile_ids to source from DHM2018+
dhm2018_tile_ids = pandas.read_csv('tiles_from_DHM2018.csv')

# Load file names
gst2014_laz_files = glob.glob(gst2014_laz + '/*.laz')
dhm2015_laz_files = glob.glob(dhm2015_laz + '/*.laz')
dhm2018_laz_files = glob.glob(dhm2018_laz + '/*.laz')
gst2014_dtm_files = glob.glob(gst2014_dtm + '/*.tif')
dhm2015_dtm_files = glob.glob(dhm2015_dtm + '/*.tif')
dhm2018_dtm_files = glob.glob(dhm2018_dtm + '/*.tif')

# Helper function to retrieve tile_ids from file names
def get_tile_ids(file_names):
      # initiate empty list for tile_ids
      tile_ids = []

      # clean up files names
      for i in range(0, len(file_names)):
          file_names[i] = re.sub('\\\\', '/', file_names[i])
      
      # fill dictionaries with tile_id, as well as row number and column number for each file name:
      for file_name in file_names:
          tile_id = re.sub('.*(\d{4}_\d{3}).*', '\g<1>', file_name)
          tile_ids.append(tile_id)

      # combine to data frame
      files_df = pandas.DataFrame(zip(*[tile_ids, file_names]),
                                   columns = ['tile_id', 'file_name'])

      # return files_df
      return(files_df)

# Appy helper function to all file names
gst2014_laz_files_df = get_tile_ids(gst2014_laz_files)
dhm2015_laz_files_df = get_tile_ids(dhm2015_laz_files)
dhm2018_laz_files_df = get_tile_ids(dhm2018_laz_files)
gst2014_dtm_files_df = get_tile_ids(gst2014_dtm_files)
dhm2015_dtm_files_df = get_tile_ids(dhm2015_dtm_files)
dhm2018_dtm_files_df = get_tile_ids(dhm2018_dtm_files)

## Copy files      

# Helper function to select and copy files with progress bar
def copy_tiles(tiles_to_copy, files_df, out_folder):

    # Subset files to copy
    files_to_copy = files_df[files_df['tile_id'].
                             isin(tiles_to_copy)]['file_name'].tolist()
    
    # Set counter to 0:
    progress = 0 
    
    # Copy files
    for i in range(0, len(files_to_copy)):
          # Check whether file exists, if not copy
          if not os.path.isfile(os.getcwd() + '/' + out_folder +
                                re.sub('.*/(.*)', '\g<1>', files_to_copy[i])):
                # Copy file
                shutil.copy(files_to_copy[i],
                            os.getcwd() + '/' + out_folder +
                            re.sub('.*/(.*)', '\g<1>', files_to_copy[i]))
          # Update progress
          progress = float(i + 1) / float(len(files_to_copy))
          # Update progress bar
          print('\r|' +
                '#' * int(round(progress * 54)) +
                '-' * int(round((1 - progress) * 54)) +
                '| ' +
                str(int(round(progress * 100))) + '%'),

# Copy laz files
print('\nCopying GST2014 laz files...')
copy_tiles(gst2014_tile_ids['tile_id'], gst2014_laz_files_df, laz_out)
print('\n\nCopying DHM2015 laz files...')
copy_tiles(dhm2015_tile_ids['tile_id'], dhm2015_laz_files_df, laz_out)
print('\n\nCopying DHM2018 laz files...')
copy_tiles(dhm2018_tile_ids['tile_id'], dhm2018_laz_files_df, laz_out)

# Copy dtm files
print('\n\nCopying GST2014 dtm files...')
copy_tiles(gst2014_tile_ids['tile_id'], gst2014_dtm_files_df, dtm_out)
print('\n\nCopying DHM2015 dtm files...')
copy_tiles(dhm2015_tile_ids['tile_id'], dhm2015_dtm_files_df, dtm_out)
print('\n\nCopying DHM2018 dtm files...')
copy_tiles(dhm2018_tile_ids['tile_id'], dhm2018_dtm_files_df, dtm_out)

## Remove incomplete laz / dtm pairs from dataset

# Status
print('\n\nDetermining completness of laz / dtm pairs in merged data set...\n')

# Retrieve files names and tile ids in merged data set
laz_merged_files = glob.glob(laz_out + '/*.laz')
dtm_merged_files = glob.glob(dtm_out + '/*.tif')
laz_merged_files_df = get_tile_ids(laz_merged_files)
dtm_merged_files_df = get_tile_ids(dtm_merged_files)

# Work out incomplete pairs
laz_missing_dtm = list(set(laz_merged_files_df['tile_id']) -
                       set(dtm_merged_files_df['tile_id']))
dtm_missing_laz = list(set(dtm_merged_files_df['tile_id']) -
                       set(laz_merged_files_df['tile_id']))

# Save incomplte pairs to file
incomplete_pairs = pandas.concat(
    [laz_merged_files_df[laz_merged_files_df['tile_id'].isin(laz_missing_dtm)],
     dtm_merged_files_df[dtm_merged_files_df['tile_id'].isin(dtm_missing_laz)]])
incomplete_pairs.to_csv('incomplete_tile_pairs.csv', index = False)

# Status
print(str(len(laz_missing_dtm)) + ' laz files have no corresponding dtm file.' +
      '\n')
print(str(len(dtm_missing_laz)) + ' dtm files have no corresponding laz file.' +
      '\n')
print('Incomplete tile_ids and file names saved to' +
      ' "incomplete_tile_pairs.csv".\n')

# Prompt for choice to delete
del_choice = raw_input('Would you like to remove the incomplete tile pairs?' +
                       '[y/n]')

# Evaluate choice
if(del_choice == 'n'):
    print('\nNo files will be deleted.')
elif(del_choice == 'y'):
    print('\nDeleting files...')
    # Delete files
    progress = 0
    files_to_delete = incomplete_pairs['file_name'].tolist()
    for i in range(0, len(files_to_delete)):
        os.remove(files_to_delete[i])
        progress = float(i + 1) / float(len(files_to_delete))
        print('\r|' +
              '#' * int(round(progress * 54)) +
              '-' * int(round((1 - progress) * 54)) +
              '| ' +
              str(int(round(progress * 100))) + '%'),
    progress = None
    print('\n')
else:
    print('\nInvalid input.')

# Status
print('Merger complete.\n\n' + '#' * 80)

# EOF
