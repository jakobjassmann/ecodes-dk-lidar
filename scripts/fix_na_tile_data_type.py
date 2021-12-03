# EcoDes-DK - Fix files missing from VRTs
# Jakob J. Assmann j.assmann@bio.au.dk 2 December 2021

# Most files missing from the VRTs are missing because they are the wrong raster
# file type (e.g. Int16 instead of float32) - the only tiles affected seem to
# be NA tiles.
# These originate  from the processing workflow and OPALS output, but
# also from the fill_processing_gaps.py script that does not accoutn for
# differences in the file paths. This script is here to correct the raster
# type of those files.

# !!! This scripts requires check_vrt_completeness.py to be run beforehand !!!

# Prep environment:

# Dependencies
import pandas
import os
import re
import scandir
import shutil
import itertools
import subprocess
from osgeo import gdal
from dklidar import settings

# Function definitions

def get_data_type(file_name):
    raster = gdal.Open(file_name)
    dataType = gdal.GetDataTypeName(raster.GetRasterBand(1).DataType)
    raster = None
    return(dataType)

def translate_file(file_name, data_type):
    # Copy file to temp folder:
    temp_file = settings.scratch_folder + '/temp_raster.tif'
    shutil.copy(file_name, temp_file)
    # remove old file
    os.remove(file_name)
    # translate file
    os.system(settings.gdal_translate_bin +
              '-ot ' + data_type + ' ' +
              temp_file + ' ' +
              file_name)

# Load missing tiles
missing_files = pandas.read_csv(settings.log_folder +
                                '/missing_files_in_vrts.csv')

# Set DataTypes for non-int16 variables
data_types_df = pandas.DataFrame(
    zip(*[
    ['solar_radiation',
     'amplitude_mean',
     'amplitude_sd',
     'date_stamp_min',
     'date_stamp_max',
     'date_stamp_mode'],
    ['Int32',
     'Float32',
     'Float32',
     'Int32',
     'Int32',
     'Int32']]),
    columns = ['variable','data_type'])

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

# Set up progres bar
progress = 0
for i in range(0,len(missing_files.index)):
    # Grab folder name
    folder = list(
        itertools.compress(
            folders,
            [bool(re.search(missing_files.variable[i], folder)) for folder in folders]))
    folder = folder[0]
    # Grab data_type
    data_type = list(
        itertools.compress(
            data_types_df.data_type,
            [bool(re.search(missing_files.variable[i], variable)) for variable in data_types_df.variable]))
    data_type = data_type[0]
    # Set file path
    file_name = folder + '/' +  missing_files.file_name[i]
    # Check wehether data types match
    if data_type == get_data_type(file_name):
        break
    # Copy to temp file
    temp_file = settings.scratch_folder + '/' + missing_files.file_name[i]
    shutil.copy(file_name, temp_file)
    # Break for debugging
    # file_name = settings.scratch_folder + '/test_out/' + missing_files.file_name[i]
    # Remove file from original folder
    os.remove(file_name)
    # Construct gdal command
    cmd = settings.gdal_translate_bin + '-ot ' + data_type + ' ' + temp_file + ' ' + file_name
    print(cmd)
    # Execute gdal commannd and swallow output
    os.system(cmd)
    # Remove temp_file
    os.remove(temp_file)
    # Update progress
    progress = float(i + 1) / float(len(missing_files.index))
    # Update progress bar
    print('\n\r|' +
          '#' * int(round(progress * 54)) +
          '-' * int(round((1 - progress) * 54)) +
          '| ' +
          str(int(round(progress * 100))) + '%\n'),



