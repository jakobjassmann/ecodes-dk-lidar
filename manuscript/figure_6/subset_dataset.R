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
# (change according to EcoDes-DK15 directory, using the teaser directory here)
ecodes_dir <- "manuscript/figure_6/teaser_data" 
variable_dirs <- list.dirs(ecodes_dir, 
                           recursive = T, 
                           full.names = F)

# Filter out folders containing subfolders
variable_dirs <- variable_dirs[-1]
variable_dirs <- grepl("(.*)/.*",variable_dirs) %>%
  variable_dirs[.] %>%
  gsub("(.*)/.*", "\\1", .) %>%
  unique() %>%
  match(., variable_dirs) %>%
  sapply(function(x)(x*-1)) %>%
  variable_dirs[.]
variable_dirs <- variable_dirs[!grepl("tile_footprints", variable_dirs)]

# Set list of variables to subset (if applicable)
# Matching will be done via regex later, so partial names / groupings are okay
# i.e. "vegetation_point_count" will match all variables including this string
# their name.
variables_to_subset <- c("vegetation_point_count", "dtm_10m")
# Subsets dirs suing regex matching
sub_dirs_to_export <- variables_to_subset %>%
  map(function(dir_name) variable_dirs[grepl(dir_name, variable_dirs)]) %>%
  unlist()
# (Alternatively use this line for all variables):
# sub_dirs_to_export <- variable_dirs

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
  # Copy tiles with special procedures for point_source counts and proportions
  if(!grepl("point_source_counts", var_name) & !grepl("point_source_proportion", var_name)) {
  tiles %>% map(function(tile_id){
    file_name <- paste0(var_name, "_", tile_id, ".tif")
    in_path <- paste0(in_dir, "/", file_name)
    out_path <- paste0(out_dir, "/", file_name)
    file.copy(in_path, out_path)
    cat(".")
  })
  } else {
    cat("Scanning files ...\n")
    var_files <- shell(paste0("dir /b ", gsub("/", "\\\\", in_dir)), intern = T)
    cat("Copying files ...\n")
    tile_files <- unlist(sapply(tiles, function(x) var_files[grepl(x, var_files)]))
    tile_files %>% map(function(file_name){
      in_path <- paste0(in_dir, "/", file_name)
      out_path <- paste0(out_dir, "/", file_name)
      file.copy(in_path, out_path)
      cat(".")})
  } 
  cat("\nDone.\n")
  return(NULL)
}

# Copy / extract subset of dataset by applying helper function
map2(in_dirs,
     out_dirs,
     function(in_dir, out_dir) copy_subset(aoi_tiles$tile_id, in_dir, out_dir))

# Generate vrt files for subset variables using sf's inbuild gdalutils 
# Skipping point source id's for which vrt generation is not possible!
map(out_dirs,
    function(dir_name) {
      oldwd <- getwd()
      setwd(dir_name)
      var_name <- gsub(".*/(.*)$", "\\1", dir_name)
      cat("Generating vrt for:", var_name, "\n")
      try(gdal_utils("buildvrt",
                 source = list.files(getwd(),".tif", full.names = T),
                 destination = paste0(var_name, ".vrt")))
      setwd(oldwd)
      return(NULL)
    })

# ! End of subsetting script!

# # This script can also be used to generate the teaser / sample dataset, 
# # the following lines complete the sample dataset.
# 
# # Generate tile footprints
# dir.create(paste0(target_dir, "/tile_footprints"))
# system2("C:/OSGeo4W64/OSGeo4W.bat",
#         args = c("gdaltindex",
#                  paste0(getwd(), "/", target_dir,
#                         "/tile_footprints/tile_footprints.shp"),
#                  paste0(getwd(), "/", target_dir,
#                         "/dtm_10m/*.tif")))
# # Load file as sf object
# tile_footprints <- read_sf(paste0(target_dir,
#                                   "/tile_footprints/tile_footprints.shp"))
# # Extract tile ids from file paths
# tile_footprints$tile_id <- gsub(".*([0-9]{4}_[0-9]{3}).*",
#                                 "\\1",
#                                 tile_footprints$location)
# # Remove location column
# tile_footprints <- dplyr::select(tile_footprints, -location)
# # Save changes
# write_sf(tile_footprints,
#          paste0(target_dir,
#                 "/tile_footprints/tile_footprints.shp"),
#          delete_layer = T)
# 
# # Generate list of vrts
# list_of_vrts <- list.files(target_dir, "\\.vrt", recursive = T)
# write.table(list_of_vrts, 
#             file = paste0(target_dir, "/list_of_vrts.txt"),
#             row.names = F,
#             col.names = F,
#             quote = F)
# 
# # Pack it into zip (requires 7z to be installed)
# current_wd <- getwd()
# setwd("D:/Jakob/dk_nationwide_lidar/manuscript/figure_6/teaser_data")
# shell(paste0('"C:\\Program Files\\7-Zip\\7z.exe"', " a ", "../EcoDes-DK15_teaser.zip ",
#              "."))
# setwd(current_wd)

# End of file