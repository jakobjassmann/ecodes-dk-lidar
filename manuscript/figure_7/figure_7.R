# Figure 6 for DK Nationwide LiDAR paper
# Visualisation of terrain and vegetation porportion based classification at 
# the Husby Klit Plantage
# Jakob Assmann 15 April 2021

# Dependencies
library(raster)
library(sf)
library(dplyr)
library(cowplot)
library(colorspace)
library(tidyverse)
library(ggspatial)
library(rasterVis)
library(rnaturalearth)
library(rnaturalearthdata)

# Set working directory (if needed)
#setwd("D:/Jakob/dk_nationwide_lidar/")

# Also source playground script for data visualisation
source("scripts/plot_raster_3d.R")

# Set area of interest
aoi <- extent(445792.4, 6238762.3, 447477.4, 6240058.2) 

## 1) Terrain stratification based on TPI ----

# Load terrain model and crop to aoi
dtm_10m <- raster("manuscript/figure_7/data/lidar_vars/dtm_10m/dtm_10m.vrt") / 100
dtm_10m <- crop(dtm_10m, aoi)

# plot dtm in 3d
dtm_10m_viz <- plot_raster_3d(dtm_10m, dtm_10m,
                                   z_scale = 10/5,
                                   colour_ramp = sequential_hcl(100, palette = "Light Grays"))
save_plot("manuscript/figure_7/dtm_10m.png",
          dtm_10m_viz)

# Calculate tpi
tpi <- terrain(dtm_10m, opt = "TPI")

# Standardise the tpi
tpi_standard <- (tpi - cellStats(tpi, mean)) / cellStats(tpi, sd)

# Visualize tpi in 3d
tpi_standard_viz <- plot_raster_3d(tpi_standard, dtm_10m,
                                    min_value = -8,
                                    max_value = 8,
                                    z_scale = 10/5, 
                                    colour_ramp = diverging_hcl(100, palette = "Purple-Brown"))
save_plot("manuscript/figure_7/tpi_standard.png",
          tpi_standard_viz)

# Divide into classes 
tpi_classes <- reclassify(tpi_standard,
                          c(-Inf, -0.5, 1, # slope bottoms and troughs 
                            -0.5, 0.5, 4, # flats and mid-slopes
                            0.5, +Inf,7)) # tops
tpi_classes <- ratify(tpi_classes)

# Convert class raster to factorial raster
tpi_classes_levels <- levels(tpi_classes)[[1]]
tpi_classes_levels$legend <- c("Troughs & Lower-slopes",
                               "Flats & Mid-slopes",
                               "Ridges & Tops")
levels(tpi_classes) <- list(tpi_classes_levels)
names(tpi_classes) <- "TPI class"

# Crop a chunck of the raster and plot with amplified elevation as an example
bounds <- extent(446345, 446685, 6238875, 6239275)
tpi_classes_cropped <- crop(tpi_classes, bounds)
tpi_classes_example_plot <- plot_raster_3d(tpi_classes_cropped, 
                                           crop(dtm_10m, tpi_classes_cropped), 
                                           z_scale = 10/5,
                                           colour_ramp = sequential_hcl(4, palette = "YlOrBr")[-4])

# Plot histogram of standardised TPI
tpi_standard_hist <- as.data.frame(tpi_standard) %>% 
  setNames("tpi_standard") %>% 
  mutate(class = case_when(tpi_standard < -0.5 ~ "Troughs & Lower-slopes",
                           tpi_standard >= -0.5 & tpi_standard <= 0.5 ~ "Flats & Mid-slopes",
                           tpi_standard > -0.5 ~ "Ridges & Tops")) %>%
  mutate(class = factor(class, levels = c("Troughs & Lower-slopes",
                                          "Flats & Mid-slopes",
                                          "Ridges & Tops"))) %>% 
  ggplot() +
  geom_histogram(aes(x = tpi_standard, fill = class),
                 breaks = seq(-6.25,8.25, 0.25)) +
  labs(x = "Top. Position Index (scaled)",
       y = "n Pixels",
       fill = "Topographic Class") +
  geom_vline(xintercept = -0.5, colour = "grey", linetype = "dashed") +
  geom_vline(xintercept = 0.5, colour = "grey", linetype = "dashed") +
  scale_fill_manual(values = sequential_hcl(4, palette = "YlOrBr")[-4]) +
  theme_cowplot() +
  theme(legend.justification = c(0, 0))
tpi_standard_hist <- ggdraw(tpi_standard_hist) +
  draw_plot(tpi_classes_example_plot, .5, .45, .5 ,.5)
save_plot("manuscript/figure_7/tpi_hist.png",
          tpi_standard_hist)
## 2) Vegetation stratification based on proportions in height bins ----

## Load and prepare LiDAR point counts
# Get list of lidar variables
lidar_vars <- list.files("manuscript/figure_7/data/lidar_vars/", pattern = ".vrt", 
                         recursive = T,
                         full.names = T)

# Load point counts for each cell
total_points <- raster(lidar_vars[grep("total_point_count", lidar_vars)])
ground_points <- raster(lidar_vars[grep("ground_point_count", lidar_vars)])
water_points <- raster(lidar_vars[grep("water_point_count", lidar_vars)][2])

veg_points_below1.5 <- lidar_vars[grep("vegetation_point_count", lidar_vars)][c(1,2,4)]
veg_points_1.5_3 <- lidar_vars[grep("vegetation_point_count", lidar_vars)][5:6]
veg_points_above3 <- lidar_vars[grep("vegetation_point_count", lidar_vars)][7:25]

veg_points_below1.5_stack <- stack(veg_points_below1.5)
veg_points_1.5_3_stack <- stack(veg_points_1.5_3)
veg_points_above3_stack <- stack(veg_points_above3)

# Turn stacks into single layer rasters with the total sum of the points
veg_points_below1.5 <- sum(veg_points_below1.5_stack)
veg_points_1.5_3 <- sum(veg_points_1.5_3_stack)
veg_points_above3 <- sum(veg_points_above3_stack)

# Add ground points to veg_points_below1.5
veg_points_below1.5 <- veg_points_below1.5 + ground_points
temp_names <- names(veg_points_below1.5_stack)
veg_points_below1.5_stack[[1]] <- veg_points_below1.5_stack[[1]]  + ground_points
names(veg_points_below1.5_stack) <- temp_names
rm(temp_names)

# Calculate proportion of points per bin in relation to total points per cell
veg_proportion_below1.5 <- veg_points_below1.5 / total_points
veg_proportion_1.5_3 <- veg_points_1.5_3 / total_points
veg_proportion_above3 <- veg_points_above3 / total_points

veg_proportion_below1.5_stack <- veg_points_below1.5_stack / total_points
veg_proportion_1.5_3_stack <- veg_points_1.5_3_stack / total_points
veg_proportion_above3_stack <- veg_points_above3_stack / total_points

names(veg_proportion_below1.5_stack) <- names(veg_points_below1.5_stack)
names(veg_proportion_1.5_3_stack) <- names(veg_points_1.5_3_stack)
names(veg_proportion_above3_stack) <- names(veg_points_above3_stack)

# Combine proporiton bins into a multilayer stack
veg_proportion <- stack(veg_proportion_below1.5, veg_proportion_1.5_3,
                        veg_proportion_above3)
names(veg_proportion) <- c("a_below_1.5", "b_above_1.5_below_3", "c_above_3")

# Crop to area of interest
veg_proportion <- crop(veg_proportion, aoi)

# Plot vegetation proportions
veg_proportion_below1.5_viz <- plot_raster_3d(veg_proportion[[1]], dtm_10m, z_scale = 10/5, 
                                              min_value = 0,
                                              max_value = 1,
                                              colour_ramp = sequential_hcl(100, palette = "Greens 3", rev = T))
veg_proportion_1.5_3_viz <- plot_raster_3d(veg_proportion[[2]], dtm_10m, z_scale = 10/5, 
                                           min_value = 0,
                                           max_value = 1,
                                           colour_ramp = sequential_hcl(100, palette = "Greens 3", rev = T))
veg_proportion_above3_viz <- plot_raster_3d(veg_proportion[[3]], dtm_10m, z_scale = 10/5, 
                                            min_value = 0,
                                            max_value = 1,
                                            colour_ramp = sequential_hcl(100, palette = "Greens 3", rev = T))
veg_proportion_scale_bar <- plot_raster_hist_bar(veg_proportion[[1]] * 100,
                                                 variable_name = "Vegetation Proportion (%)",
                                                 min_value = 0,
                                                 max_value = 100,
                                                 colour_ramp = sequential_hcl(100, palette = "Greens 3", rev = T),
                                                 colour_bar_only = T)
save_plot("manuscript/figure_7/veg_prop_lt1-5.png",
          veg_proportion_below1.5_viz)
save_plot("manuscript/figure_7/veg_prop_1-5_to_3-0.png",
          veg_proportion_1.5_3_viz)
save_plot("manuscript/figure_7/veg_prop_gt3-0.png",
          veg_proportion_above3_viz)
# Classify vegetation
veg_classes <- veg_proportion[[1]]

veg_classes <- reclassify(veg_classes, 
                          c(-Inf, +Inf,2)) # Set all cells to class 2
veg_classes[veg_proportion$b_above_1.5_below_3 == 0 &
              veg_proportion$c_above_3 == 0] <- 1 # Set all cells to class 1 where there is no vegetation in layers b and c
veg_classes[veg_proportion$c_above_3 >= cellStats(veg_proportion$c_above_3, "max") * 0.1] <- 3 # Set all cell sto class 3 where the proportion in the layer c exceeds 10% of the maximym value in layer c. 

# Set water classe if cell is:
# a) either more than 10% water hits
# b) total_points == 0
water_points <- crop(water_points, aoi)
total_points <- crop(total_points, aoi) 
water_proportion <- water_points / total_points
veg_classes[water_proportion > 0.1 | total_points == 0] <- 0

# Crop proportion height bin stacks
veg_proportion_below1.5_stack <- crop(veg_proportion_below1.5_stack, aoi)
veg_proportion_1.5_3_stack <- crop(veg_proportion_1.5_3_stack, aoi)
veg_proportion_above3_stack <- crop(veg_proportion_above3_stack, aoi)

# Visualize classification for a sample
set.seed(53098)
veg_sample <- sampleRandom(veg_classes, ncell(veg_classes) * 0.01, cells = T)
veg_sample <- as.data.frame(veg_sample)
names(veg_sample) <- c("cell_id", "veg_class")
veg_sample <- cbind(veg_sample, veg_proportion_below1.5_stack[veg_sample$cell_id])
veg_sample <- cbind(veg_sample, veg_proportion_1.5_3_stack[veg_sample$cell_id])
veg_sample <- cbind(veg_sample, veg_proportion_above3_stack[veg_sample$cell_id])
veg_sample <- veg_sample %>% pivot_longer(cols = 3:ncol(veg_sample),
                                          names_to = "proportion")
veg_sample$proportion <- gsub("vegetation_point_count_","",veg_sample$proportion)
veg_sample$proportion <- gsub("m\\."," - ",veg_sample$proportion)
veg_sample$proportion <- gsub("m"," m",veg_sample$proportion)
veg_sample$veg_class[veg_sample$veg_class == 1] <- "Grass & Heath"
veg_sample$veg_class[veg_sample$veg_class == 2] <- "Shrubs &\nSmall Trees"
veg_sample$veg_class[veg_sample$veg_class == 3] <- "Trees"
veg_sample$veg_class <- factor(veg_sample$veg_class)
veg_sample$proportion <- factor(veg_sample$proportion, 
                                   levels = sort(unique((veg_sample$proportion))))
veg_sample <- veg_sample[veg_sample$veg_class != 0,]
veg_sample$value <- veg_sample$value * 100
veg_sample_plot <- ggplot(veg_sample, aes(x = proportion, 
                                          y = value, 
                                          group = cell_id,
                                          colour = veg_class)) +
  geom_line(alpha = 0.5) +
  geom_vline(xintercept = 3.5, colour = "grey", linetype = "dashed") +
  geom_vline(xintercept = 5.5, colour = "grey", linetype = "dashed") +
  labs(x = "Height Bin", y = "Proportion of Points (%)") +
  scale_colour_manual(values = c("#F5E52CFF",
                                 "#A89E27FF",
                                 "#1E8AA8FF")) +
  scale_x_discrete(labels = gsub("0([0-9])","\\1",veg_sample$proportion)) +
  coord_flip() +
  facet_wrap(~veg_class) +
  theme_cowplot() +
  theme(legend.position = "none",
        strip.background = element_rect(fill = "white"))
save_plot("manuscript/figure_7/point_props_bins.png",
          veg_sample_plot,
          base_height = 5,
          base_asp = 1.1)
## 3) Merge TPI and veg classes ----
tpi_veg_combined_classes <- tpi_classes + (veg_classes - 1) 
tpi_veg_combined_classes[veg_classes == 0] <- 0
tpi_veg_combined_classes <- ratify(tpi_veg_combined_classes)
classes <- levels(tpi_veg_combined_classes)[[1]]
classes$legend <- c("Water", 
                    "Troughs + Grass & Heath",
                    "Troughs + Shrubs & Small Trees",
                    "Troughs + Trees",
                    "Mid-slopes + Grass & Heath",
                    "Mid-slopes + Shrubs & Small Trees",
                    "Mid-slopes + Trees",
                    "Ridges + Grass & Heath",
                    "Ridges + Shrubs & Small Trees",
                    "Ridges + Trees")
levels(tpi_veg_combined_classes) <- classes
names(tpi_veg_combined_classes) <- "class"
classification_plot <- as_grob(levelplot(tpi_veg_combined_classes,
                                         col.regions=c('#45D0F5FF',
                                                       "#F5E52CFF",
                                                       "#A89E27FF",
                                                       "#1E8AA8FF",
                                                       "#F5E52C77",
                                                       "#A89E2777",
                                                       "#1E8AA877",
                                                       "#F5E52C33",
                                                       "#A89E2733",
                                                       "#1E8AA833"),
                                         xlab=NULL, 
                                         ylab=NULL, 
                                         scales=list(draw=FALSE)) +
                                 latticeExtra::layer({
                                   ## Scale bar
                                   # Determine position of scale bar (bottom left corner)
                                   scale_bar_length <- 500 # Scale bar length 20 m
                                   scale_bar_height <- 50 # scale bar height 3 m
                                   scale_bar_nsegments <- 1 # 1 segment
                                   scale_bar_xpos <- 80 # x position from bottom left corner in percent
                                   scale_bar_ypos <- 92.5 # y position from bottom left corner in percent
                                   
                                   # calculate derived parameters:
                                   # (there is a bug in lattice so we need to shove it into the global enviornment)
                                   scale_bar_xmin <- extent(tpi_veg_combined_classes[[1]])@xmin + 
                                     ((extent(tpi_veg_combined_classes[[1]])@xmax -
                                         extent(tpi_veg_combined_classes[[1]])@xmin) / 100 * scale_bar_xpos)
                                   scale_bar_xmax <- scale_bar_xmin + scale_bar_length 
                                   scale_bar_ymin <- extent(tpi_veg_combined_classes[[1]])@ymin + 
                                     ((extent(tpi_veg_combined_classes[[1]])@ymax -
                                         extent(tpi_veg_combined_classes[[1]])@ymin) / 100 * scale_bar_ypos)
                                   scale_bar_step <- scale_bar_length / scale_bar_nsegments
                                   
                                   xs <- seq(scale_bar_xmin, scale_bar_xmax, scale_bar_step)
                                   grid.rect(x = xs[1:(length(xs)-1)],
                                             y = scale_bar_ymin,
                                             width = scale_bar_length, height=scale_bar_height,
                                             gp= gpar(fill = rep(c('black', "black"),
                                                                 2),
                                                      col = "black"),
                                             default.units='native')
                                   grid.text( 
                                     x = scale_bar_xmin,
                                     y = scale_bar_ymin - scale_bar_height * 2,
                                     paste(scale_bar_length, "m"),
                                     gp=gpar(cex=1.25, col = "black", font = 2),
                                     default.units='native')
                                   grid.text( 
                                     x = extent(tpi_veg_combined_classes[[1]])@xmin + 350,
                                     y = extent(tpi_veg_combined_classes[[1]])@ymax - 200, # (scale_bar_ymin - scale_bar_height * 2),
                                     paste("N"),
                                     gp=gpar(cex=1.25 * 2, col = "black", font = 2),
                                     default.units='native')
                                   grid.text( 
                                     x = extent(tpi_veg_combined_classes[[1]])@xmin + 200,
                                     y = extent(tpi_veg_combined_classes[[1]])@ymax - 150, # (scale_bar_ymin - scale_bar_height * 2),
                                     paste("↑"),
                                     gp=gpar(cex=1.25 * 2, col = "black", font = 2),
                                     default.units='native')
                                 }, data = list(tpi_veg_combined_classes = tpi_veg_combined_classes)))
save_plot("manuscript/figure_7/final_classification.png",
          classification_plot)

## 4 Location of are on map of denmark ----
# Prepare tile footprint
tile_footprint <- SpatialPolygonsDataFrame(as(extent(dtm_10m), 
                                              "SpatialPolygons"), data = data.frame(name = "Husby Klit"))
tile_footprint <- st_as_sf(tile_footprint)
st_crs(tile_footprint) <- st_crs(dtm_10m)

# Generate a map of Denmark
dk_boundary <- ne_countries(scale = "medium", returnclass = "sf") %>%
  filter(name == "Denmark") %>% st_transform(st_crs(dtm_10m))

# Set boundaries
map_bounds <- dk_boundary  %>% st_bbox()

# Plot map of tile location in Denmark
tile_location <- ggplot() + geom_sf(data = dk_boundary, fill = "white", size = 1) + 
  geom_sf(data = st_centroid(tile_footprint),
          colour = "#1E8AA8",
          size = 5, shape = 15) +  
  coord_sf(ylim = c(map_bounds["ymin"] - 50000, map_bounds["ymax"] + 50000), 
           xlim = c(map_bounds["xmin"] - 50000, map_bounds["xmax"] - 100000), expand = F) +
  annotation_scale(pad_x = unit(2.25, "in"), pad_y = unit(2.5, "in"),
                   style = "ticks",
                   width_hint = 0.15) +
  annotation_north_arrow(pad_x = unit(2.175, "in"), 
                         pad_y = unit(2.75, "in"),
                         style = north_arrow_nautical) +
  theme_nothing() +
  theme(legend.title = element_blank(),
        axis.text = element_blank(),
        axis.line = element_blank(),
        axis.ticks = element_blank(),
        panel.grid.minor = element_line(colour = "white"),
        panel.grid.major = element_line(colour = "white")) 
save_plot("manuscript/figure_7/area_location.png",
           tile_location,
           base_asp = 1)
 