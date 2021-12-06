# Scripts for processing and setting up the environment
The scripts in this folder are used to prepare the processing environment, process the dataset, and carry out any post-processing steps neccessary. 

## Content

1. [Setting up the environment and downloading the data](#setting-up-the-environment-and-downloading-the-data)
2. [Test run for a single tile](#test-run-for-a-single-tile)
3. [Execute the processing for all tiles](#execute-the-processing-for-all-tiles)
4. [Post-processing steps](#post-processing-steps)
5. [Quality control and log file processing](#quality-control-and-log-file-processing)
6. [Overview of scripts in this folder](#scripts-overview)

[\[to top\]](#content)

## Setting up the environment and downloading the data
Carry out the following steps to prepare the processing. **Unless explicitly stated, all scripts need to be executed from within an OPALS shell.** 

1. Make a local clone of the repository.
2. Update the relevant paths and parameters in `dklidar/settings.py` according to your local system.
3. Modify the `set_environment.bat` script to set the absolute paths to your OPALS Python executable and the *dklidar* modules. **Note: You will have to run this batch script every time you open a new OPALS shell for processing using this workflow.**
4. If you have not already installed `pandas` in your OPALS Python environment do this now, for example by running: `python -m pip install pandas --user`. It is also worth checking whether `numpy`, `osgeo` (`gdal`) and `ogr` are provided by your OPALS install (they should be), but if not install those also. Furthermore, some of the suppport scripts require addtional modules which might need to be installed if you would like to use those scripts later (see [list](#python-modules-required-by-support-scripts) at end of document).
5. Download the source dtm and point clouds:
   1. Order / check out all [pointcloud](https://download.kortforsyningen.dk/content/dhmpunktsky) and [DTM](https://download.kortforsyningen.dk/content/dhmterr%C3%A6n-04-m-grid) tile bundles on the Kortforsyningen website, but don't download these files via your browser yet. We will download them in step 3 using the `download_files.py` script\*.
   2. Follow instructions in the comments of the `download_files.py` script to retrieve a cookie for the Kortforsyningen website using *Google Chrome* (you could also do that in a different browser, but we only provide instructions for *Chrome* here). 
   3. Adjust the number of parallel downloads in the `download_files.py` script to fit your needs and bandwidth. Note: Tile bundle file names are specified in the `.txt` files in the `data/kortforsyningen_file_lists/` folder.
   4. Open an OPALS shell.
   5. Navigate to the `scripts` folder in your local clone of this repository. 
   6. Run `set_environment.bat` to set up the environment .
   7. Run `python donwload_files.py`. 
6. Verify the integrity of the downloads and check for completness of the datasets:
   1. Run `create_checksums.bat` to create the checksums for the downloaded files.
   2. Verify checksums and establish any missing tiles by running `python checksum_qa.py`. 
      - The script will flag up any corrputed files based on the checksums and export a list of those to a csv stored in the parent folder that contain the data (the file will be named damaged_files.csv).
      - The script will cross-compare the completness of the dtm and point cloud files. Tiles present in one set, but not present in the other, are reported. The outcomes are exported both as a csv of tile ids and as alist of file names. Again these are saved in the parent folder containing each dataset. 
7. Optional: fill in any gaps in the dtm dataset by generating missing dtms using `python generate_dems.py` . If you do so, don't forget to update the outputs for the completness check by re-running `python checksum_qa.py` afterwards.
8. Finally, remove any remaining incomplete tiles in the datasets (e.g. dtm tiles without a corresponding point cloud) by running `python remove_missing_tiles.py` . 
9. Consider confirming that the dataset is complete by re-running `python checksum_qa.py`.

\* *Alternatively, Kortforsyningen could be contacted to request access to the dataset via a different route, e.g. their ftp file server access.* 

[\[to top\]](#content)

## Test run for a single tile

1. Open `debug.py` and adjust the file paths in line 22 and 25 to match your local file paths.

2. Specify the tile_id (line 36) for which you would like to carry out the test run. (This can also be done by providing the tile_id as a command line argument when executing the script.)

3. Run the debug script in an OPALS shell using `python debug.py`.
4. If needed, quality control debug run outputs using `debug.Rmd`.

[\[to top\]](#content)

## Execute the processing for all tiles

Once the above steps are completed and the single tile test run was successful, we can then:

1. Adjust the number of parallel processes to be run in `process_tiles.py`

2. Run `python process_tiles.py` to start the processing.

3. Open a second OPALS shell, set the environment using `set_environment.bat` and start `python progress_monitor.py` to keep track of the progress.

Note: 

- If for some reason the processing needs to be interrupted, use `stop.bat` to kill all Python processs and sub-processes on the machine. **NB: This will also kill any Python processes not related to the processing of the LiDAR data.**
- `process_tiles.py` uses a CSV-based database created in the `log/process_tiles`  to keep track of which tiles have been processed. The progress database allows the script to resume without data loss, should the processing be interrupted. Once the processing is resumed, all already processed tiles will be skipped and any partially processed tiles will be re-processed. If, for some reason, you would like to start a fresh processing attempt that overwrites any existing progress, then you will have to delete the script's log folder and its contents (`log/process_tiles`).  
- To process only a subset of the variables, comment out any unwanted processing steps in `process_tiles.py`.
- If you change the number of parallel processing threads in the `process_tiles.py` script, you will also have to update the same variable in the `progress_monitor.py` script. 
- `progress_monitor.py` uses a linear estimate for the ETA, this should give a general idea for when the processing might finish, but becomes inaccurate once the first parallel processes are starting to be completed.
- `progress_monitor.py` might fail to keep track of the progress once less tiles than the number of parallel processes are remaining. In that case, check the output from `process_tiles.py` to confirm the final completion. 

[\[to top\]](#content)

## Post processing steps

Once the processing has finished, a few post-processing steps need to be carried out:

1. Generate a tile_footprints shapefile by running `generate_tile_footprints.py`. 
2. Fill in processing gaps using `fill_processing_gaps.py`.
   - A small number of tiles (< 100), e.g. on the fringes of the dataset (including sand banks, spits etc.), may fail processing for some of the variables - especially the point cloud derived variables. This script fills these "processing gaps", by creating empty rasters containing only NA for the missing tiles and variables. The script also outputs a csv file summarising the number of tiles missing for each variable [/documentation/empty_tiles_summary.csv](/documentation/empty_tiles_summary.csv). The specific tile ids of the missing variable / tile combinations can be retrieved from the log files and/or [/documentation/empty_tile_ids.csv](/documentation/empty_tile_ids.csv). 
   - `fill_processing_gaps.py` will automatically generate Int16 NA tiles, this is not suitable for the Int32 and Float32 variables (amplitude* and date_stamp_*). Run `fix_na_tile_data_type.py`  after the `fill_processing_gaps.py` run is complete. 
3. Generate VRT files for each variable using the `make_vrt_subfolders.bat` batch script. Execute this script in the parent folder containing all your output rasters (the one specified in the settings.output_folder variable of the settings.py module). **NB: Unlike the other scripts this batch script will have to be run in an ordinary (non-OPALS) Windows command prompt. You will also need to update the file path to the OSgeo4W binaries (line 18) in the make_vrt.bat script and the file path to the make_vrt.bat script in the make_vrt_subfolders.bat (line 11).** 
   - The script will recursively loop through the folder tree and generate a vrt file in any folder that contains tif files. 
   - The script will name the VRT file based on the folder that contains it and all file paths used will be relative.
   - The VRT file will be generated for the  extent of the nationwide datset, consider adjusting the extent parameter in `make_vrs.bat` in case only a subset has been processed. 
   - Note that the script will try (and fail) to generate VRTs for the *tile_footprints* and the *point_source_counts*, *point_source_ids* and *point_source_proportion* variables. The shapefiles and multilayer rasters cannot be inccorporated into VRT files. I suggest removing the relevant dummy *.vrt files created by this script after completion.  
4. Optional: Bundle and compress outputs as tar.bz2 archives by running `archive_outputs.py`. Note: Adjust the destination folder for archives (line 14) prior execution. You can also generate md5 checksums for those archives using `create_checksums_archives.bat`, again update the folder path(s) in the script.
5. Optional: Generate a list of all the VRT files with in the settings.output_folder folder structre using `generate_list_of_vrts.py`. This file can be handy for fast access to the data, especially in R as listing files in a folder tree with a large amount of files can be very slow (albeit something you can work around by calling `dir` or `ls` using `shell()`).
6. Optional: Check output file integrity using `check_putputs_integrity.py`. 
   - If you run the full EcoDes-DK processing you will have likely created something along the lines of 4-5 million tif files. Some errors might have occured when generating those files. We only had one of these errors for all of the different processing batches that we did, but it is worth checking! The `check_outputs_integrity.py` script checks the integrity of the output tif files by loading each of them into a python environment using gdal. Should the file be corrupt, the script will catch the error and report the tile_id and error in the output csv log file. You can then repocress the tiles (e.g using the `debug.py` script or if many a new `process_tiles.py` batch - see commented out section in main script on how to process only a small batch). 
   - Runs in parallel so that you won't have to wait too long. 

[\[to top\]](#content)

## Quality control and log file processing

We have provided a couple of scripts that allow for quality control and log file processing: 

- `quality_assurance.R` - A simple quality assurance script that checks summary statistics, generates histograms and correlation plots for a set of random sample points from across Denmark. **(To be updated!)**
- `processing_report.Rmd` - R Markdown file that gathers key processing information from the log files, such as error rates, messages and tile id, as well as variable - tile id combination for which the processing was not succesffull. 

Note: The logging database used for processe management in also contains information on the exit status of each processing step for each tile. In addition, the OPALs and GDAL logs are kept for all processed tiles in the subfolders of this folder named with the tile id.

[\[to top\]](#content)

## Scripts overview
Script | Description 
--- | ---
archive_outputs.py | Simple scripts to bundle and compress the output files by variable / group, based on the subfolders of the output folder defined in `settings.py`. 
check_outputs_integrity.py | Checks integrity of raster outputs by scannning the output folder and tries to load every individual tif file with gdal. Opperates in parallel for speed. Documents any errors that occur. 
check_vrt_completeness.py | Scans output dir for vrts and then checks whether any tif files have been missed in these vrts. 
checksum_qa.py | Validates checksums for downloads, and cross-compares dtm and pointcloud datasets for completnness. Requires `checksum_qa.py` to be run previously. 
create_checksums.bat | Generates checksums for downloaded files. 
create_checksums_archives.bat | Generates checksums for outputs packed into archives using `archive_outputs.py`. 
debug.py | Script for testing / debugging the processing workflow based on a single tile. Processing is done sequentially, one variable after the other. Timings are provided. 
debug.Rmd | R Markdown document for visual quality assurance of the debug.py outputs. 
download_files.py | Helper script to download DHM\Punktsky pointclouds and DHM dtm rasters from the Kortforsyningen website. 
fill_processing_gaps.py | Fills incomplete variables with empty rasters (all NA) for the missing tiles. To be executed after processing. 
fix_na_tile_data_type.py | Helper script to assist with post-processing after running fill_processing_gaps.py. Fixes the data type for any non Int16 descriptors, translating outputs to the relevant data types (e.g. Int32 or Float32). 
generate_dems.py | Generates DTMs from the pointclouds that are missing a corresponding DTM file. 
generate_list_of_vrts.py | Generates a text file containing a list of all vrt files in each subfolder of a given directory. 
generate_tile_footprints.py | Generates tile_footprint variable (based on dtm_10m by default).
make_vrt.bat | Creates a vrt from all .tif files in the folder from which it is executed, 1st argument specifies the name of the output vrt file. 
make_vrt_subfolders.bat | Recursively creates vrt files within all subfolders of the current directory that contain tif images. Each VRT file is named with the subfolder name. (Scripts works, but is a bit buggy, should be replaced by a Python version in the long run). 
plot_raster_3d.R | Set of helper functions to generate publication ready 3D plots of rasters in R using the *rayshader* package. (Used to generate the figures for the manuscript). 
**process_tiles.py** | **Main script for processing**. Controls process managment and defines which processing steps are carried out. Uses the functions defined in the *dklidar* modules. 
**progress_monitor.py** | **Progress monitor**. Run this script in a separate OPALS shell to keep track of the processing. Launch after initating processing using `process_tiles.py`. 
processing_report.Rmd | R Markdown document to generate an overview report based on the log outputs from `process_tiles.py`. 
quality_assurance.R | Simple quality assurance script that checks summary statistics, generates histograms and correlation plots for a set of random sample points from across Denmark. 
remove_missing_tiles.py | Removes incomplete sets of tiles from the DTM and laz folders. Run after `checksum_qa.py` has been executed. 
**set_environment.bat** | Adds the *dklidar package* to the OPALS shell python path. **Execute each time after launching an new OPALS shell.** 
**stop.bat** | **Stops process_tiles.py** by killing all pyhton.exe processes currently running. Can be used to interrupt `process_tiles.py`. **NB: Kills ALL Python processes!** 

*Note: Other scripts may appear here that are version controlled for temporary purposes.*

[\[to top\]](#content)

## Python modules required by support scripts

In addtion to the modules provided by the OPALS install, the support scripts require the following Python 2.7 modules also (version used): `pandas`(0.24.2), `numpy`(1.16.6), `scandir`(1.10.0) and `tqdm`(4.62.3).

[\[to top\]](#content)
