# Transferring the EcoDes workflow to a new data set

We developed the EcoDes workflow with flexibility in mind and hopefully it should be relatively straight forward to adapt the workflow for other point cloud data sets (i.e. not the Danish DHM). In most cases this will involve updating multiple sections of the code to accommodate for the differences within the data sets, including tile naming conventions, grain sizes etc. This document outlines some of the key considerations for the adaptations steps required. 

## Tiling and file naming conventions

The tiling/file naming conventions of a point cloud data set will probably have the biggest impact on the usability of the code for the data set in question. The code was optimized for handling the tiling convention of the Danish national grid and tiles of 1 km x 1 km in size. 

To adapt the file-handling procedures please follow the code and intext comments in `scripts/process_tiles.py`, as well as all function definitions in the `dklidar` modules that create tile neighbourhood mosaics. 

OPALS is able to import point cloud data from various formats (see [OPALS documentation](https://opals.geo.tuwien.ac.at/html/stable/usr_supported_fmt.html)). Please note that file endings will have to be changed in the script to allow for other formats than the LAZ format used for the DHM/Pointcloud.

## Grain size / resolution

The DHM/Terrain rasters come with a nominal grain size of 0.4 m, reflecting the average point density of the DHM/Pointcloud. The code has been tailored for this input grain size of the DTM and a target output grain size of 10 m. 

To adapt the code for input DTM rasters with a different grain size, please follow the code and intext comments in the `dtm_aggregate_tile()` function description of the `dklidar/dtm.py` module. 

The target output grain size for all OPALS operations is defined in the `dklidar/settings.py` module, for any other operations that carry out raster handling (mainly in the `dklidar/dtm.py` module) please see and update the individual processing functions as required. 

## Classification of point cloud

The workflow was developed to handle point clouds that are already classified following the ASPRS LAS 1.1-1.4 standard (see citation in manuscript or [here](https://desktop.arcgis.com/en/arcmap/latest/manage-data/las-dataset/lidar-point-classification.htm) for a easily interpretable documentation). 

Should the point cloud to be processed not be classified, then a prior classification step is necessary. Unfortunately, guidance on this subject is beyond the scope of this documentation. 

Adapting the workflow to other standards of classification should be possible, but might involve a bit of effort. All point filters are specified in the `dklidar/settings.py` module and called upon from the `dklidar/points.py` module where needed. 

## No accompanying digital terrain model (DTM)

Should the point cloud come without a paired digital terrain model (like the DHM/Terrain and DHM/Pointcloud), then the generation of a DTM is required prior the processing (with a grain size of 0.4 m unless the code has been adapted as discussed above). 

It is possible to generate any missing DTM tiles with corresponding point cloud tiles using OPALS and the `scripts/generate_dems.py` script. Please follow the code and intext comments to adapt it according to your needs. 

---

[24 August 2021]

