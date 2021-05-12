# Quick helper script to archive all main variable folders
# Jakob Assmann j.assmann
# Zip all folders 
import shutil
import glob
import re
import multiprocessing
import os
from dklidar import settings

# Function to archive folders using shutil
def zip_folder(folder_path):
    # Set folder for zips
    zip_output = 'D:/Jakob/dk_nationwide_lidar/data/zipped_outputs'
    folder_name = zip_output + '/' + re.sub('.*\\\\(.*)\\\\', '\g<1>', folder_path)
    shutil.make_archive(folder_name, 'bztar', folder_path)
    
# Main body of script
if __name__ == '__main__':
    # Get list of folders in output directories and their names
    folders = glob.glob(settings.output_folder + '*/')

    # archive in parallel
    multiprocessing.set_executable(settings.python_exec_path)
    pool = multiprocessing.Pool(processes=len(folders))
    zipping = pool.map_async(zip_folder, folders)
    zipping.wait()
    pool.close()
