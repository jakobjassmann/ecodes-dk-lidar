# Scripts for processing and setting up the envrionment
The scripts in this folder are used to set up the environment and process the dataset, using the functions defined int he dklidar pacakage. 

Script | Description 
--- | ---
**set_environment.bat** | Launched from the opals shell, adds dklidar python package folder to python path.
**process_tiles.py** | Main script for processing, controls process managment and steps carried out for the processing of each tile. *(under construction)*
download_files.bat | script to retrieve laz pointclouds and dtm rasters as well as generating local checksums. *(under construction)*
checksum_qa.py | Validates checksums for laz pointcloud files and dtm rasters after download.

Note: Other scripts may be version controlled here for temporary purposes.
