# EcoDes-DK15 - Collection date figure
# Jakob J. Assmann j.assmann@bio.au.dk 26 Septemger 2021

# Dependencies
library(raster)
library(ggplot2)
library(cowplot)
library(sf)
library(tidyverse)
library(parallel)
library(pbapply)

# Set wd (if needed)
setwd("D:/Jakob/ecodes-dk-lidar/")

# Get list of date_stamp files
file_list <- shell(paste0("dir /b /l ", 
                          normalizePath(file.path("D:", "Jakob", "datafordeler_downloads", "outputs", "date_stamp"
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
  date_raster <- raster(file.path("D:/Jakob/datafordeler_downloads/outputs/date_stamp/", file_name))
  mode_date <- cellStats(date_raster, Mode, na.rm = T)
  data.frame(tile_id = gsub("date_stamp_(.*)\\.tif", "\\1", file_name),
             date_mode = mode_date)
}


# Prep cluster
cl <- makeCluster(14)
clusterEvalQ(cl, library(raster))
clusterExport(cl, c("Mode", "mode_date_stamp"))

# Extract mode of date stamp for each tile (takes around 5 mins on VRS01)
date_stamps <- pblapply(file_list, mode_date_stamp, cl = cl) %>%
  bind_rows()

# Stop cluster
stopCluster(cl)

# Read in tile footprints shape file
tile_footprints <- read_sf("D:/Jakob/datafordeler_downloads/outputs/tile_footprints/tile_footprints.shp")
tile_footprints <- filter(tile_footprints, tile_id != "6144_577")

# Merge with date_stamps
prints_with_stamps <- full_join(tile_footprints, date_stamps,
                                by = c("tile_id" = "tile_id"))

# Change date from date precision to month precision
prints_with_stamps$date_mode_month <- gsub("([0-9]{4})([0-9]{2}).*", "\\1 \\2", prints_with_stamps$date_mode)

# set september 2011 to NA (the offset)
prints_with_stamps$date_mode_month[prints_with_stamps$date_mode_month == "2011 09"] <- "No date"

# convert to factor
prints_with_stamps$date_mode_month <- as.factor(prints_with_stamps$date_mode_month)

# Save as csv (if needed)
prints_with_stamps %>%
  mutate(year = substr(date_mode, 1,4)) %>%
  st_drop_geometry() %>%
  write_csv("D:/Jakob/ecodes-dk-lidar/auxillary_files/date_DHM2015_tiles.csv")

# Plot map
month_plot <- ggplot() +
  geom_sf(data = na.omit(prints_with_stamps),
          aes(fill = date_mode_month),
          colour = NA) +
  labs(fill = "Year, Month", title = "DHM2015_punktsky tile acquisition dates", 
       subtitle = "Most common GPS timestamp per tile, given as year and month") +
  scale_fill_manual(values = c('#CAA0F2',
                               '#A656F0',
                               rep('#BD9C3A', 3),
                               rep('#F0C64A', 3),
                               rep('#4A5BF0', 3),
                               '#287029',
                               rep('#F03C3D', 2),
                               rep('#BD2F2F', 2),
                               rep('#F28585', 2),
                               '#808080')) +
  theme_cowplot()
save_plot("documentation/figures/DHM2015_collection_month.png", month_plot,
          base_height = 6)
qualitative_hcl(9)

prints_with_stamps %>%
  group_by(date_mode_month) %>% summarise(n = n())   %>% 
  mutate(year_mode = gsub("([0-9]{4})(.*)", "\\1", as.character(date_mode_month))) %>%
  mutate(year_mode = factor(year_mode, levels = c("2013", "2014", "2015", "2016", " ", "2018", "No date"))) %>%
  {ggplot(.,
          aes(x = year_mode, y = n, fill = date_mode_month)) +
      geom_col() +
      geom_col(data = data.frame(year_mode = "2017" , n = 0, date_mode_month = "No date")) +
      geom_text(aes(x = year_mode, y = n + 1000, label = n), 
                data = group_by(., year_mode) %>% summarize(n = sum(n)), 
                inherit.aes = F) +
      scale_y_continuous(limits = c(0,30000)) + 
      labs(fill = "Year, Month", title = "DHM2015_punktsky tile acquisition dates", 
           subtitle = "Most common GPS timestamp per tile, given as year and month",
           y = "Number of Tiles", x = "Year") +
      scale_fill_manual(values = c('#CAA0F2',
                                   '#A656F0',
                                   rep('#BD9C3A', 3),
                                   rep('#F0C64A', 3),
                                   rep('#4A5BF0', 3),
                                   rep('#287029', 1),
                                   rep('#F03C3D', 2),
                                   rep('#BD2F2F', 2),
                                   rep('#F28585', 2),
                                   '#808080')) +
      scale_x_discrete(labels =  c("2013", "2014", "2015", "2016", "2017", "2018", "No date")) +
      theme_cowplot()} %>%
  save_plot("documentation/figures/DHM2015_collection_month_hist.png", .,
            base_height = 6)
