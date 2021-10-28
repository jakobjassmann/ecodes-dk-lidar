# Short script to confirm transferred file integrity using md5 checksums.
# Prerequisite is that checsum were generated using create_checksums.bat
# A comparsions of the sets of laz tiles and dtm tiles is also carried out.
# Jakob Assmann j.assmann@bios.au.dk 16 January 2020

# Imports
import os
import glob
import numpy as np
import pandas
import re
from dklidar import settings

### Read in filenames using unix filename extensions from glob
### 1) Pointcloud files (laz)
##orig_md5_files = glob.glob(settings.laz_folder + '*.md5')
##local_md5_files = glob.glob(settings.laz_folder + '*.local_md5')
### 2) DTM files (tif)
##orig_md5_files.extend(glob.glob(settings.dtm_folder + "*.md5"))
##local_md5_files.extend(glob.glob(settings.dtm_folder + "*.local_md5"))
##
### Initiate empty lists
##md5_orig = list()
##md5_local = list()
##
### Fill lists with md5 sums from files
##for file_name in orig_md5_files:
##    file = open(file_name)
##    md5_orig.append(file.read(32))
##for file_name in local_md5_files:
##    file = open(file_name)
##    md5_local.append(file.read(32))
##
### Zip all lists into one data frame
##df = pandas.DataFrame(zip(orig_md5_files, md5_orig, local_md5_files, md5_local),
##                      columns=['orig_file', 'orig_md5', 'local_file', 'local_md5'])
##
### Add md5_vheck comparison column to df
##md5_check = df['orig_md5'] == df['local_md5']
##df['md5_check'] = md5_check
##
### Print dataframe overiview to console
##print()
##print('df overview:')
##print(df.head())
##print()
##
### Filter rows where the check returned false
##print('Non matching md5 checksums:' + str(np.sum([not i for i in df['md5_check']])))
##damaged_files = df[df['md5_check'] == False]
##print(damaged_files)
##
### Export csv
##damaged_files.to_csv(settings.laz_folder + '../damaged_files.csv', index=False)
##
# ---------------------------------------------------
# Check for completeness of datasets

# Load file names
dtm_files = glob.glob(settings.dtm_folder + '/*.tif')
laz_files = glob.glob(settings.laz_folder + '/*.laz')

# initiate empty lists for tile_ids
dtm_tile_ids = []
laz_tile_ids = []

# fill dictionaries with tile_id, as well as row number and column number for each file name:
for file_name in dtm_files:
    tile_id = re.sub('.*DTM_1km_(\d*_\d*).tif', '\g<1>', file_name)
    dtm_tile_ids.append(tile_id)

for file_name in laz_files:
    tile_id = re.sub('.*PUNKTSKY_1km_(\d*_\d*).laz', '\g<1>', file_name)
    laz_tile_ids.append(tile_id)

# Determine differences between sets of tiles
missing_laz_tiles = set(dtm_tile_ids) - set(laz_tile_ids)
missing_dtm_tiles = set(laz_tile_ids) - set(dtm_tile_ids)

df_missing_dtm = pandas.DataFrame(zip(missing_dtm_tiles), columns=['tile_id'])
df_missing_dtm.to_csv(settings.dtm_folder + '../missing_dtm_tile_ids.csv', index=False)

# Print out a quick overview of data frame for control
print(df_missing_dtm.head())

df_missing_laz = pandas.DataFrame(zip(missing_laz_tiles), columns=['tile_id'])
df_missing_laz.to_csv(settings.laz_folder + '../missing_laz_tile_ids.csv', index=False)

# Print out a quick overview of data frame for control
print(df_missing_laz.head())

# Export lists to files
# DTMs with missing LAZs
out_file = open(settings.dtm_folder + '../dtm_files_with_missing_laz.txt', 'a+')
for tile_id in missing_laz_tiles:
    out_file.write(settings.dtm_folder + 'DTM_1km_' + tile_id + '.tif\n')
out_file.close()

# LAZs with missing DTMs
out_file = open(settings.laz_folder + '../laz_files_with_missing_dtm.txt', 'a+')
for tile_id in missing_dtm_tiles:
    out_file.write(settings.laz_folder  +'PUNKTSKY_1km_' + tile_id + '.laz\n')
out_file.close()

