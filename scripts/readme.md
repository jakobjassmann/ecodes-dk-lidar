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
7. Verify checksums and establish any missing tiles using `checksum_qa.py`. Follow up by running `remove_missing_tiles.py` if you want. 

Once all those steps are completed...

8. Run `process_tiles.py` to start the processing.
9. Open a second OPALS shell and start `progress_monitor.py` to keep taps on the progress.

The `process_tiles.py` scripts uses a CSV-based database created in the `log/process_tiles` folder to keep track of which tiles have been processed. The progress database allows the script to resume without dataloss, should the processing be interrupted for some unexpected reason. In this case all partially processed tiles will be re-processed again. The database also contains information on the exit status of each processing step for each tile. Furthermore, the OPALs and GDAL logs are kept for all processed tiles in the subfolders of this folder named with the tile id. 

\* *Alternatively, Kortforsyningen could be contacted to request access to the  dataset via a different route.* 

----

## Scripts
Script | Description 
--- | ---
checksum_qa.py | Validates checksums for downloads, and checks dtm and pointcloud datasets for completnness.
create_checksums.bat | Generates checksums for downloaded files. 
download_files.py | Downloads pointclouds and dtm rasters.
generate_dems.py | Generates low-quality DTMs from the pointclouds for tiles missing a DTM file (*currently not used*).
local_qa.R | Quality control for quick post-processing QA (written in shorthand).
make_vrt.bat | Creates a vrt from all .tif files in the current folder, 1st argument names the vrt file.
make_vrt_subfolders.bat | Recursively creates vrt files for all subfolders naming the file with the subfolder name.
**process_tiles.py** | **Main script for processing**. Controls process managment and defines which steps are carried out. Uses the functions defined in the *dklidar package*.
**progress_monitor.py** | Progress monitor to be launched after starting process_tiles. Run in a separate OPALS shell to keep track of the processing. 
remove_missing_tiles.py | Removes incomplete tiles from the DTM and laz folders. Run after `checksum_qa.py` has been executed.
**set_environment.bat** | Adds the *dklidar package* to the OPALS shell python path.
**stop.bat** | Stops processing chain by killing all pyhton.exe processes currently running. Can be used to interrupt `process_tiles.py`.
test.py | Playground script to test processing steps etc. 

*Note: Other scripts may appear here that are version controlled for temporary purposes.*
