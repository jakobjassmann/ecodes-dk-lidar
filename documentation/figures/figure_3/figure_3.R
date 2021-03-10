# Visualisation of DTM derived variables for manuscript
# Jakob J. Assmann j.assmann@bio.au.dk Feb 2021

## 1) Housekeeping ----

# Set wd
setwd("D:/Jakob/dk_nationwide_lidar/documentation/figures/figure_3")

# Dependencies
library(cowplot)
library(tidyverse)
library(rnaturalearth)
library(rnaturalearthdata)

# Source 3D plotting funcitions for rasters
# Contains special characters and stored in UTF-8 does not work with "source"
# Use eval and parse instead.
eval(parse("../plot_raster_3d/plot_raster_3d.R", encoding = "UTF-8"))

# Set target tile id (Mol's Bjerge)
tile_id <- "6210_570"

# Set folder paths
dtm_10m <- "D:/Jakob/dk_nationwide_lidar/data/outputs/dtm_10m"
amplitude_mean <- "D:/Jakob/dk_nationwide_lidar/data/outputs/amplitude/amplitude_mean"
amplitude_sd <- "D:/Jakob/dk_nationwide_lidar/data/outputs/amplitude/amplitude_sd"
canopy_height <- "D:/Jakob/dk_nationwide_lidar/data/outputs/canopy_height"
normalized_z_mean <- "D:/Jakob/dk_nationwide_lidar/data/outputs/normalized_z/normalized_z_mean"
normalized_z_sd <- "D:/Jakob/dk_nationwide_lidar/data/outputs/normalized_z/normalized_z_sd"
ground_point_count <- "D:/Jakob/dk_nationwide_lidar/data/outputs/point_count/ground_point_count_-01m-01m"
water_point_count <- "D:/Jakob/dk_nationwide_lidar/data/outputs/point_count/water_point_count_-01m-01m"
vegetation_point_count <- "D:/Jakob/dk_nationwide_lidar/data/outputs/point_count/vegetation_point_count_00m-50m"
building_point_count <- "D:/Jakob/dk_nationwide_lidar/data/outputs/point_count/building_point_count_-01m-50m"
total_point_count <- "D:/Jakob/dk_nationwide_lidar/data/outputs/point_count/total_point_count_-01m-50m"
point_source_nids <- "D:/Jakob/dk_nationwide_lidar/data/outputs/point_source_info/point_source_nids"
canopy_openness <- "D:/Jakob/dk_nationwide_lidar/data/outputs/proportions/canopy_openness"
vegetation_density <- "D:/Jakob/dk_nationwide_lidar/data/outputs/proportions/vegetation_density"
building_proportion <- "D:/Jakob/dk_nationwide_lidar/data/outputs/proportions/building_proportion"

# Load rasters for the tile
dtm_10m_raster <- raster(paste0(dtm_10m, "/dtm_10m_", tile_id, ".tif"))/ 100
amplitude_mean_raster <- raster(paste0(amplitude_mean, "/amplitude_mean_", tile_id, ".tif"))
amplitude_sd_raster <- raster(paste0(amplitude_sd, "/amplitude_sd_", tile_id, ".tif"))
canopy_height_raster <- raster(paste0(canopy_height, "/canopy_height_", tile_id, ".tif")) / 100
normalized_z_mean_raster <- raster(paste0(normalized_z_mean, "/normalized_z_mean_", tile_id, ".tif")) / 100
normalized_z_sd_raster <- raster(paste0(normalized_z_sd, "/normalized_z_sd_", tile_id, ".tif")) / 100
ground_point_count_raster <- raster(paste0(ground_point_count, "/ground_point_count_-01m-01m_", tile_id, ".tif")) 
water_point_count_raster <- raster(paste0(water_point_count, "/water_point_count_-01m-01m_", tile_id, ".tif"))
vegetation_point_count_raster <- raster(paste0(vegetation_point_count, "/vegetation_point_count_00m-50m_", tile_id, ".tif"))
building_point_count_raster <- raster(paste0(building_point_count, "/building_point_count_-01m-50m_", tile_id, ".tif"))
total_point_count_raster <- raster(paste0(total_point_count, "/total_point_count_-01m-50m_", tile_id, ".tif"))
point_source_nids_raster <- raster(paste0(point_source_nids, "/point_source_nids_", tile_id, ".tif"))
canopy_openness_raster <- raster(paste0(canopy_openness, "/canopy_openness_", tile_id, ".tif")) / 10000
vegetation_density_raster <- raster(paste0(vegetation_density, "/vegetation_density_", tile_id, ".tif")) / 10000
building_proportion_raster <- raster(paste0(building_proportion, "/building_proportion_", tile_id, ".tif")) / 10000

# Load orthomosaic 
# Reduce size for easier handling (commmented out as this takes time)
# ortho <- stack("6210_570_ortho_2014.tif")
# ortho <- crop(ortho, dtm_10m_raster)
# ortho <- aggregate(ortho, 12)
# writeRaster(ortho, paste0("ortho_", tile_id, "_aggregated.tif"), overwrite = T)
# Shortcut to cropped and aggregated ortho raster
ortho <- stack(paste0("ortho_", tile_id, "_aggregated.tif"))


# Define data frame with plotting parameters
parameters <- tibble(
  variable_code = c("amplitude_mean",
                    "amplitude_sd",
                    "canopy_height",
                    "normalized_z_mean",
                    "normalized_z_sd",
                    "ground_point_count",
                    "water_point_count",
                    "vegetation_point_count",
                    "building_point_count",
                    "total_point_count",
                    "point_source_nids",
                    "canopy_openness",
                    "vegetation_density",
                    "building_proportion"),
  variable_name = c("Return Amplitude (undefined)",
                    "Return Amplitude σ (undefined)",
                    "Canopy Height (m)",
                    "Normalized z mean (m)",
                    "Normalized z σ (m)",
                    "Ground Point Count",
                    "Water Point Count",
                    "Vegetation Point Count",
                    "Building Point Count",
                    "Total Point Count",
                    "Point Source IDs Count",
                    "Canopy Openness",
                    "Vegetation Density",
                    "Building Proportion"
                    ),
  raster_object = list(
    amplitude_mean_raster,
    amplitude_sd_raster,
    canopy_height_raster,
    normalized_z_mean_raster,
    normalized_z_sd_raster,
    ground_point_count_raster,
    water_point_count_raster,
    vegetation_point_count_raster,
    building_point_count_raster,
    total_point_count_raster,
    point_source_nids_raster,
    canopy_openness_raster,
    vegetation_density_raster,
    building_proportion_raster),
  dtm_raster = list(dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster),
  colour_ramp = list(sequential_hcl(99, palette = "Plasma", rev = T),
                     sequential_hcl(99, palette = "Viridis", rev = T),
                     sequential_hcl(10, palette = "Greens 3", rev = T),
                     sequential_hcl(10, palette = "Heat", rev = T),
                     sequential_hcl(10, palette = "OrRd", rev = T),
                     sequential_hcl(99, palette = "BrwnYl", rev = T),
                     sequential_hcl(5, palette = "Blues 3", rev = T),
                     sequential_hcl(10, palette = "Greens 3", rev = T),
                     sequential_hcl(10, palette = "Reds 3", rev = T),
                     sequential_hcl(99, palette = "Grays", rev = T),
                     sequential_hcl(3, palette = "Inferno", rev = T),
                     sequential_hcl(10, palette = "Sunset", rev = T),
                     sequential_hcl(10, palette = "Greens 3", rev = T),
                     sequential_hcl(10, palette = "Reds 3", rev = T)),
  # min_value = c(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
  # max_value = c(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
  # y_max = c(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
  z_scale = 5
  )

# Generate combined plots
plot_list <- parameters %>% 
  dplyr::select(-variable_code) %>%
  pmap(function(...){
    plot_raster_3d_combined(...)
  })

# Generate orthophoto plot and add scale and north arrow
ortho_plot <- plot_raster_3d_rgb(ortho, dtm_10m_raster, z_scale = 5) %>%
  add_scale_north()

# Prepare tile footprint
tile_footprint <- SpatialPolygonsDataFrame(as(extent(dtm_10m_raster), 
                                              "SpatialPolygons"), data = data.frame(name = tile_id))
tile_footprint <- st_as_sf(tile_footprint)
st_crs(tile_footprint) <- st_crs(dtm_10m_raster)

# Generate a map of Denmark
dk_boundary <- ne_countries(scale = "medium", returnclass = "sf") %>%
  filter(name == "Denmark")

# Plot map of tile location in Denmark
tile_location <- ggplot() + geom_sf(data = dk_boundary, fill = "white", size = 1) + 
  geom_sf(data = st_centroid(tile_footprint),
          colour = "red",
          size = 5) +  
  coord_sf(ylim = c(54, 58.5), xlim = c(7.87307, 13.2433), expand = F) +
  theme_nothing() +
  theme(legend.title = element_blank(),
        axis.text = element_blank(),
        axis.line = element_blank(),
        axis.ticks = element_blank(),
        panel.grid.minor = element_line(colour = "white"),
        panel.grid.major = element_line(colour = "white")) 

# Add the plots to the plot list
plot_list <- append(list(plot_grid(ortho_plot, tile_location)), plot_list)

# Combine into one multipanel plot with lables
combined_plot <- plot_grid(
  plotlist = plot_list ,
  ncol = 3,
  labels = paste0(
                  letters[1:9], ") " , 
                  c("orthophoto",
                    parameters$variable_code)),
  label_size = 24,
  label_x = 0.025,
  label_y = 0.96,
  hjust = 0,
  vjust = 1
  )

# Save plot
save_plot("figure_3.png", combined_plot,
          base_height = 4,
          base_aspect_ratio = 2,
          ncol = 3,
          nrow = 5)
 
