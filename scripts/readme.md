# Scripts for processing and setting up the environment
The scripts in this folder are used to set up the environment and process the dataset, using the functions defined int he dklidar pacakage. 

## Getting started
*To be completed..*

## Scripts
Script | Description 
--- | ---
**set_environment.bat** | Launched from the opals shell, adds dklidar python package folder to python path.
**process_tiles.py** | Main script for processing, controls process managment and steps carried out for the processing of each tile. *(under construction)*
download_files.bat | script to retrieve laz pointclouds and dtm rasters as well as generating local checksums. *(under construction)*
checksum_qa.py | Validates checksums for laz pointcloud files and dtm rasters after download.
make_vrt.bat | Creates a vrt from all .tif files in the current folder, requires one argument to name the output vrt file.
make_vrt.bat | Recursively creates vrt files for all subfolders naming the file with the subfolder name.

*Note: Other scripts may appear here that are version controlled for temporary purposes.8
