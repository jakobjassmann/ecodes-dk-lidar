# DK-LiDAR Example script - dataset subsetting
# Jakob J. Assmann j.assmann@bio.au.dk June 2021

# Dependencies
library(sf)
library(tidyverse)
library(raster)

# Set area of interest (here Husby Klit Dune reserve)
aoi <- st_polygon(list(matrix(c(8.12534,56.30670,
                                8.12700,56.28855,
                                8.14738,56.30377,
                                8.14606,56.28725,
                                8.12534,56.30670), 
                              ncol = 2,
                              byrow = T))) %>%
  st_sfc(crs = 4326)

# Read in tile footprints
tile_footprints <- read_sf("manuscript/figure_6/data/lidar_vars/tile_footprints/tile_footprints.shp")

# Determine intersecting tiles
aoi_tiles <- aoi %>%
  st_transform(., st_crs(tile_footprints)) %>%
  st_intersects(tile_footprints, ., sparse = F) %>%
  filter(tile_footprints, .)

# Get dirs for the available variables 
# (change according to EcoDes-DK15 directory, using a toy directory here)
ecodes_dir <- "manuscript/figure_6/data/lidar_vars/" 
variable_dirs <- list.dirs(ecodes_dir, 
                           recursive = T, 
                           full.names = F)

# Set list of variables to subset 
# Matching will be done via regex later, so partial names / groupings are okay
# i.e. "vegetation_point_count" will match all variables including this string 
# their name.
variables_to_subset <- c("vegetation_point_count", "dtm_10m")

# Subsets dirs suing regex matching
sub_dirs_to_export <- variables_to_subset %>%
  map(function(dir_name) variable_dirs[grepl(dir_name, variable_dirs)]) %>% 
  unlist()

# Set target dir to place output:
target_dir <- "~/Desktop"

# Create absolute folder paths
in_dirs <- paste0(ecodes_dir, "/", sub_dirs_to_export)
out_dirs <- paste0(target_dir, "/", sub_dirs_to_export)

# Define helper function to copy tiles 
copy_subset <- function(tiles, in_dir, out_dir){
  # Get variable name
  var_name <- gsub(".*/(.*)$", "\\1", in_dir)
  # Status
  cat(rep("#", 80), "\n", sep = "")
  cat("Copying", length(tiles), "tiles for varialbe:", var_name, "\n")
  cat("from:\t", in_dir, "\n")
  cat("to:\t", in_dir, "\n")
  # Check whether out dir exists
  if(!dir.exists(out_dir)) dir.create(out_dir, recursive = T)
  # Copy tiles
  tiles %>% map(function(tile_id){
    file_name <- paste0(var_name, "_", tile_id, ".tif")
    in_path <- paste0(in_dir, "/", file_name)
    out_path <- paste0(out_dir, "/", file_name)
    file.copy(in_path, out_path)
    cat(".")
  })
  cat("\nDone.\n")
  return(NULL)
}

# Copy / extract subset of dataset by applying helper function
map2(in_dirs,
     out_dirs,
     function(in_dir, out_dir) copy_subset(aoi_tiles$tile_id, in_dir, out_dir))

# Generate vrt files for subset variables using sf's inbuild gdalutils 
map(out_dirs,
    function(dir_name) {
      oldwd <- getwd()
      setwd(dir_name)
      var_name <- gsub(".*/(.*)$", "\\1", dir_name)
      gdal_utils("buildvrt",
                 source = list.files(getwd(),".tif", full.names = T),
                 destination = paste0(var_name, ".vrt"))
      setwd(oldwd)
    })

# End of file