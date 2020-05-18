# Scripts for processing and setting up the environment
The scripts in this folder are used to set up the environment and process the dataset, using the functions defined in the *dklidar* pacakage. 

## Getting started
Carry out the following steps to prepare the processing:

1. Make a local clone of the repository.
2. Set the absolute paths to your local folders in `dklidar/settings.py`.
3. Check out all [pointcloud](https://download.kortforsyningen.dk/content/dhmpunktsky) and [DTM](https://download.kortforsyningen.dk/content/dhmterr%C3%A6n-04-m-grid) tile bundles on the Kortforsyningen website, but don't download via your browser\*.
4. Follow instructions in the comments of the `download_files.py` script to retrieve a cookie for the Kortforsyningen website using *Google Chrome*. Adjust the number of parallel downloads in the script to fit your needs. Note: Tile bundle file names are specified in the `.txt` files in the `data/kortforsyningen_file_lists/` folder.
5. Open an OPALS shell.
5. Modify the `set_environment.bat` script with your local paths and run the script to add the *dklidar package* to the OPALS python environment.
5. Run `donwload_files.py`. 
6. Run `create_checksums.bat` to create the checksums for the downloaded files.
7. Verify checksums and establish any missing tiles using `checksum_qa.py`. Follow up by running `remove_missing_tiles.py` if you want to. 

Once all those steps are completed...

8. Run `process_tiles.py` to start the processing.
9. Open a second OPALS shell and start `progress_monitor.py` to keep taps on the progress.

\* *Alternatively, Kortforsyningen could be contacted to request access to the  dataset via a different route.* 

----

## Scripts
Script | Description 
--- | ---
checksum_qa.py | Validates checksums for downloads, and checks dtm and pointcloud datasets for completnness.
create_checksums.bat | Generates checksums for downloaded files. 
download_files.py | Downloads laz pointclouds and dtm rasters.
generate_dems.py | Helper script to generate low-quality DEMs from the pointclouds for tiles missing a DTM file (*currently not needed*).
local_qa.R | Quality control script for quick post-processing QA (written in shorthand).
make_vrt.bat | Creates a vrt from all .tif files in the current folder, requires one argument to name the output vrt file.
make_vrt_subfolders.bat | Recursively creates vrt files for all subfolders naming the file with the subfolder name.
**process_tiles.py** | Main script for processing, controls process managment and steps carried out for the processing of each tile. 
**progress_monitor.py** | Progress monitor to be launched after starting process_tiles. Running in a separate shell this helper script provides key stats for the process of the processing.
remove_missing_tiles.py | Helper script that removes incomplete tiles from the DTM and laz folders (can be run after checksum_qa.py has been executed).
**set_environment.bat** | Launched from the OPALS shell, adds the dklidar python package folder to OPALS python path.
**stop.bat** | Stops processing chain by providing a shortcut to killing all pyhton.exe processes currently run by the user. Can be used to interrupt the processing using the process_tiles.py script.
test.py | Playground script to test processing steps etc. 

*Note: Other scripts may appear here that are version controlled for temporary purposes.*
