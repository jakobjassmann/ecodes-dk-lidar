# Short script to confirm transferred file integrity using md5 checksums.
# Prerequisite is that files were transferred using the create_envir.bat
# Jakob Assmann j.assmann@bios.au.dk 16 January 2020

# Imports
import os
import glob
import numpy as np
import pandas

# Read in filenames using unix filename extensions from glob
# 1) Pointcloud files (laz)
orig_md5_files = glob.glob("data/laz/*.md5")
local_md5_files = glob.glob("data/laz/*.local_md5")
# 2) DTM files (tif)
orig_md5_files.extend(glob.glob("data/dtm/*.md5"))
local_md5_files.extend(glob.glob("data/dtm/*.local_md5"))

# Initiate empty lists
md5_orig = list()
md5_local = list()

# Fill lists with md5 sums from files
for file_name in orig_md5_files:
    file = open(file_name)
    md5_orig.append(file.read(32))
for file_name in local_md5_files:
    file = open(file_name)
    md5_local.append(file.read(32))

# Zip all lists into one data frame
df = pandas.DataFrame(zip(orig_md5_files, md5_orig, local_md5_files, md5_local),
                      columns=['orig_file', 'orig_md5', 'local_file', 'local_md5'])

# Add md5_vheck comparison column to df
md5_check = df['orig_md5'] == df['local_md5']
df['md5_check'] = md5_check

# Print dataframe overiview to console
print()
print('df overview:')
print(df.head())
print()

# Filter rows where the check returned false
print('Non matching md5 checksums:' + str(np.sum([not i for i in df['md5_check']])))
damaged_files = df[df['md5_check'] == False]
print(damaged_files)

# Export csv
damaged_files.to_csv('data/damaged_files.csv', index=False)