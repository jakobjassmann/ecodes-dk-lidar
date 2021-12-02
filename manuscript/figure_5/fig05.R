# EcoDes-DK15 - GPS date stamp mode figure (figure 5)
# Jakob J. Assmann j.assmann@bio.au.dk 26 September 2021

# Dependencies
library(raster)
library(ggplot2)
library(cowplot)
library(sf)
library(tidyverse)
library(parallel)
library(pbapply)

# Set wd (if needed)
setwd("D:/Jakob/ecodes-dk-lidar-rev1/")

# Get list of date_stamp files
file_list <- shell(paste0("dir /b /l ", 
                          normalizePath(
                            file.path("D:", 
                                      "Jakob", 
                                      "ecodes-dk-lidar-rev1", 
                                      "data",
                                      "outputs", 
                                      "date_stamp",
                                      "date_stamp_mode"
                                    ))), 
                   intern = TRUE) 
file_list <- file_list[grep(".tif", file_list)]

# Modified function from Ken Wiliams on stack exchange
Mode <- function(x, na.rm = T) {
  if(na.rm == T) x <- na.omit(x)
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

# write function to extract mode of date stamp
mode_date_stamp <- function(file_name){
  date_raster <- raster(
    file.path(
      "D:/Jakob/ecodes-dk-lidar-rev1/data/outputs/date_stamp/date_stamp_mode/", 
      file_name))
  mode_date <- cellStats(date_raster, Mode, na.rm = T)
  data.frame(tile_id = gsub("date_stamp_mode_(.*)\\.tif", "\\1", file_name),
             date_mode = mode_date)
}


# Prep cluster
cl <- makeCluster(62)
clusterEvalQ(cl, library(raster))
clusterExport(cl, c("Mode", "mode_date_stamp"))

# Extract mode of date stamp for each tile (takes around 5 mins on VRS01)
date_stamps <- pblapply(file_list, mode_date_stamp, cl = cl) %>%
  bind_rows()

# Stop cluster
stopCluster(cl)

# Read in tile footprints shape file
tile_footprints <- read_sf(
  paste0("D:/Jakob/ecodes-dk-lidar-rev1/data/",
  "outputs/tile_footprints/tile_footprints.shp"))

# Merge with date_stamps
prints_with_stamps <- full_join(tile_footprints, date_stamps,
                                by = c("tile_id" = "tile_id"))

# Change date from date precision to month precision
prints_with_stamps$date_mode_month <- gsub("([0-9]{4})([0-9]{2}).*", "\\1, \\2", prints_with_stamps$date_mode)

# Set NA to "no date"
prints_with_stamps[is.na(prints_with_stamps$date_mode_month),]$date_mode_month <- "No date"

# convert to factor
prints_with_stamps$date_mode_month <- as.factor(prints_with_stamps$date_mode_month)

# Save as shp and csv (if needed)
prints_with_stamps %>%
  mutate(year = substr(date_mode, 1,4)) %>%
  write_sf("D:/Jakob/ecodes-dk-lidar-rev1/manuscript/figure_5/date_mode_tiles.shp")
prints_with_stamps %>%
  mutate(year = substr(date_mode, 1,4)) %>%
  st_drop_geometry() %>%
  write_csv("D:/Jakob/ecodes-dk-lidar-rev1/manuscript/figure_5/date_mode_tiles.csv")

# Plot map
month_plot <- ggplot() +
  geom_sf(data = prints_with_stamps,
          aes(fill = date_mode_month),
          colour = NA) +
  labs(fill = "Year, Month", title = "EcoDes-DK15 Vegetation Point Collection Dates", 
       subtitle = "Aggregate of date_stamp_mode for each tile") +
  scale_fill_manual(values = c('#F2620F',
                               rep('#F2C53D', 3),
                               rep('#5259D9', 3),
                               rep('#A63348', 3),
                               '#0F0F0F')) +
  theme_cowplot() +
  theme(axis.line = element_blank(),
        axis.text = element_blank(),
        axis.ticks = element_blank())
save_plot("manuscript/figure_5/fig05.png", month_plot,
          base_height = 6)

# End of File
