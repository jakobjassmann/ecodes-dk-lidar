# DK Nationwide LiDAR - A short R script to generate the tile footprints file. 
# Jakob Assmann j.assmann@bios.au.dk 11 August 2020

# Dependencies
library(sf)
library(dplyr)

# Set global parameters
osgeos_path <- "C:/OSGeo4W64/OSGeo4W.bat"
data_outputs_path <- "D:/Jakob/dk_nationwide_lidar/data/outputs/" 

# Create dir (if needed)
dir.create(paste0(data_outputs_path, "tile_footprints"))

# Make footprint shape file with GDAL from OSGEOS
system2(osgeos_path, 
        args = c("gdaltindex",
                 paste0(data_outputs_path, 
                        "tile_footprints/tile_footprints.shp"),
                 paste0(data_outputs_path, 
                        "aspect/*.tif")))

# Load file as sf object
tile_footprints <- read_sf(paste0(data_outputs_path, 
               "tile_footprints/tile_footprints.shp"))

# Extract tile ids from file paths
tile_footprints$tile_id <- gsub(".*([0-9]{4}_[0-9]{3}).*",
                                "\\1",
                                tile_footprints$location)

# Remove location column
tile_footprints <- select(tile_footprints, -location)

# Save changes
write_sf(tile_footprints,
         paste0(data_outputs_path, 
                "tile_footprints/tile_footprints.shp"),
         delete_layer = T)

