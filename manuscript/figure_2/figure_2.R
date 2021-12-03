# Visualisation of DTM derived variables for manuscript
# Jakob J. Assmann j.assmann@bio.au.dk Feb 2021

## 1) Housekeeping ----

# Set wd
setwd("D:/Jakob/ecodes-dk-lidar-rev1/manuscript/figure_2/")

# Dependencies
library(sf)
library(raster)
library(cowplot)
library(tidyverse)
library(rnaturalearth)
library(rnaturalearthdata)

# Source 3D plotting funcitions for rasters
# Contains special characters and stored in UTF-8 does not work with "source"
# Use eval and parse instead.
eval(parse("../../scripts/plot_raster_3d.R", encoding = "UTF-8"))

# Set target tile id (Mol's Bjerge)
tile_id <- "6230_595"

# Set folder paths
ecodes_path <- "D:/Jakob/ecodes-dk-lidar-rev1/data/outputs/"
dtm_10m <- paste0(ecodes_path, "dtm_10m")
aspect <- paste0(ecodes_path, "aspect")
slope <- paste0(ecodes_path, "slope")
heat_load_index <- paste0(ecodes_path, "heat_load_index")
solar_radiation <- paste0(ecodes_path, "solar_radiation")
openness_mean <- paste0(ecodes_path, "openness_mean")
openness_difference <- paste0(ecodes_path, "openness_difference")
twi <- paste0(ecodes_path, "twi")

# Load rasters for tile
dtm_10m_raster <- raster(paste0(dtm_10m, "/dtm_10m_", tile_id, ".tif"))/ 100
aspect_raster <- raster(paste0(aspect, "/aspect_", tile_id, ".tif"))/ 10
slope_raster <- raster(paste0(slope, "/slope_", tile_id, ".tif"))/ 10
heat_load_index_raster <- raster(paste0(heat_load_index, "/heat_load_index_", tile_id, ".tif"))/ 10000
solar_radiation_raster <- raster(paste0(solar_radiation, "/solar_radiation_", tile_id, ".tif"))/ 100000
openness_mean_raster <- raster(paste0(openness_mean, "/openness_mean_", tile_id, ".tif"))
openness_difference_raster <- raster(paste0(openness_difference, "/openness_difference_", tile_id, ".tif"))
twi_raster <- raster(paste0(twi, "/twi_", tile_id, ".tif"))/ 1000

# Load orthomosaic 
# Reduce size for easier handling (commmented out as this takes time)
# ortho <- stack("6230_594_ortho_2014.tif")
# ortho <- crop(ortho, dtm_10m_raster)
# ortho <- aggregate(ortho, 12)
# writeRaster(ortho, paste0("ortho_", tile_id, "_aggregated.tif"), overwrite = T)
# Shortcut to cropped and aggregated ortho raster
ortho <- stack(paste0("ortho_", tile_id, "_aggregated.tif"))


# Define data frame with plotting parameters
parameters <- tibble(
  variable_code = c("dtm_10m",
                    "aspect",
                    "slope",
                    "heat_load_index",
                    "solar_radiation",
                    "openness_mean",
                    "openness_difference",
                    "twi"),
  variable_name = c("Height asl (m)",
                    "Aspect (°)",
                    "Slope (°)",
                    "Heat Load Index (unitless)",
                    "Energy (10^5 MJ / 100 m2 / yr)",
                    "Openness Mean (°)",
                    "Openness Difference (°)",
                    "TWI (unitless)"),
  raster_object = list(dtm_10m_raster,
                         aspect_raster,
                         slope_raster,
                         heat_load_index_raster,
                         solar_radiation_raster,
                         openness_mean_raster,
                         openness_difference_raster,
                         twi_raster),
  dtm_raster = list(dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster,
                    dtm_10m_raster),
  colour_ramp = list(sequential_hcl(99, palette = "DarkMint"),
                     diverging_hcl(n = 40, h = c(12, 12), c = c(22, 153), l = c(0, 79), power = c(0.5, 1.45)),
                     sequential_hcl(99, palette = "Plasma"),
                     sequential_hcl(99, palette = "Blues3", rev = T),
                     c(rep(sequential_hcl(70, palette = "Inferno")[1], 29),sequential_hcl(70, palette = "Inferno")),
                     sequential_hcl(99, palette = "Viridis"),
                     sequential_hcl(99, palette = "Viridis"),
                     sequential_hcl(99, palette = "Blues3", rev = T)),
  min_value = c(25,0,0,0,1600000/100000,75,0, 0),
  max_value = c(125,360,30,1,2400000/100000, 95, 40, 20),
  y_max = c(700, 600, 400, 500, 750, 3000, 700, 1000),
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
                    "dtm_10m",
                    "aspect",
                    "slope",
                    "heat_load_index",
                    "solar_radiation",
                    "openness_mean",
                    "openness_difference",
                    "twi")),
  label_size = 24,
  label_x = 0.025,
  label_y = 0.96,
  hjust = 0,
  vjust = 1
  )

# Save plot
save_plot("fig02.png", combined_plot,
          base_height = 4,
          base_aspect_ratio = 2,
          ncol = 3,
          nrow = 3,
          bg = "white")
 
