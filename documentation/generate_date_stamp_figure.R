# EcoDes-DK15 - Collection date figure
# Jakob J. Assmann j.assmann@bio.au.dk 26 Septemger 2021

# Dependencies
library(raster)
library(ggplot2)
library(cowplot)
library(sf)
library(tidyverse)
library(parallel)

# Set wd (if needed)
setwd("D:/Jakob/dk_nationwide_lidar/")

# Get list of date_stamp files
file_list <- shell(paste0("dir /b /l ", 
                          normalizePath(file.path("D:", "Jakob", "dk_nationwide_lidar", "data", "outputs", "date_stamp"
                                    ))), 
                   intern = TRUE) 

# Modified function from Ken Wiliams on stack exchange
Mode <- function(x, na.rm = T) {
  if(na.rm == T) x <- na.omit(x)
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

# write function to extract mode of date stamp
mode_date_stamp <- function(file_name){
  date_raster <- raster(file.path("data/outputs/date_stamp/", file_name))
  mode_date <- cellStats(date_raster, Mode, na.rm = T)
  data.frame(tile_id = gsub("date_stamp_(.*)\\.tif", "\\1", file_name),
             date_mode = mode_date)
}


# Prep cluster
cl <- makeCluster(72)
clusterEvalQ(cl, library(raster))
clusterExport(cl, c("Mode", "mode_date_stamp"))

# Extract mode of date stamp for each tile (takes around 5 mins on VRS01)
date_stamps <- parLapply(cl, file_list, mode_date_stamp) %>%
  bind_rows()

# Stop cluster
stopCluster(cl)

# Read in tile footprints shape file
tile_footprints <- read_sf("data/outputs/tile_footprints/tile_footprints.shp")

# Merge with date_stamps
prints_with_stamps <- full_join(tile_footprints, date_stamps,
                                by = c("tile_id" = "tile_id"))

# Change date from date precision to month precision
prints_with_stamps$date_mode_month <- gsub("([0-9]{4})([0-9]{2}).*", "\\1 \\2", prints_with_stamps$date_mode)

# set september 2011 to NA (the offset)
prints_with_stamps$date_mode_month[prints_with_stamps$date_mode_month == "2011 09"] <- "No data"

# convert to factor
prints_with_stamps$date_mode_month <- as.factor(prints_with_stamps$date_mode_month)

# Plot map
month_plot <- ggplot() +
  geom_sf(data = na.omit(prints_with_stamps),
          aes(fill = date_mode_month),
          colour = NA) +
  labs(fill = "Year, Month", title = "EcoDes-DK15 tile acquisition dates", 
       subtitle = "Most common GPS timestamp per tile, given as year and month") +
  scale_fill_manual(values = c("#C86DD7",
                               rep("#00AD9A",3),
                               rep("#50A315",3),
                               rep("#009ADE",3),
                               rep("#B88A00",3),
                               "#E16A86")) +
  theme_cowplot()
save_plot("documentation/figures/collection_month.png", month_plot,
          base_height = 6)
qualitative_hcl(6)
