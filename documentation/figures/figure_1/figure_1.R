# Visualisation of pointclouds for publication

# Dependencies
library(lidR)
library(cowplot)
library(sf)
library(tidyverse)
library(raster)
library(rgl)
library(magick)

# Set wd
setwd("D:/Jakob/dk_nationwide_lidar/documentation/figures/figure_1")

# File paths
laz_files <- "D:/Jakob/dk_nationwide_lidar/data/laz"
canopy_height <- "D:/Jakob/dk_nationwide_lidar/data/outputs/canopy_height"
dtm_10m <- "D:/Jakob/dk_nationwide_lidar/data/outputs/dtm_10m"
point_counts <- list.dirs("D:/Jakob/dk_nationwide_lidar/data/outputs/point_count", recursive = F, full.names = T)
point_proportions <- list.dirs("D:/Jakob/dk_nationwide_lidar/data/outputs/proportions/", recursive = F, full.names = T)
normalized_z_sd <- "D:/Jakob/dk_nationwide_lidar/data/outputs/normalized_z/normalized_z_sd"
amplitude_mean <- "D:/Jakob/dk_nationwide_lidar/data/outputs/amplitude/amplitude_mean"

# Set tile id of interest
# Here we select a tile from the Husby Klit plantage
tile_id <- "6210_570"

# Load point cloud 
tile_laz <- readLAS(paste0(laz_files, "/PUNKTSKY_1km_", tile_id, ".laz"))
# Normalize heights
dtm_10m_raster <- raster(paste0(dtm_10m, "/dtm_10m_", tile_id, ".tif"))/ 100
tile_laz <- tile_laz - dtm_10m_raster

# Get variables by pixels using a helper function
get_variable <- function(folder_name){
  variable_name <- gsub(".*/(.*)$", "\\1", folder_name)
  cat("Loading", variable_name, "...\n")
  raster_pixels <- raster(paste0(folder_name, "/", variable_name, "_", tile_id, ".tif")) %>%
    as.data.frame() %>% 
    mutate(x = rep(1:100, 100), 
           y = sort(rep(1:100,100)),
           pixel_id = paste0("x", x, "y", y)) %>%
    select(-x, -y)
  return(raster_pixels)
}
raster_pixels <- lapply(c(canopy_height,
                          unlist(point_counts),
                          unlist(point_proportions),
                          normalized_z_sd,
                          amplitude_mean),
                        get_variable) 
raster_pixels <- raster_pixels %>% 
  reduce(full_join, by = "pixel_id")
# Add footprint geometries
raster_pixels <- raster(paste0(dtm_10m, "/", "dtm_10m_", tile_id, ".tif")) %>%
  as("SpatialPolygonsDataFrame") %>% 
  st_as_sf() %>%
  mutate(x = rep(1:100, 100), 
         y = sort(rep(1:100,100)),
         pixel_id = paste0("x", x, "y", y)) %>%
  select(-x, -y) %>%
  full_join(., raster_pixels)
# Remove tile ids from names
names(raster_pixels) <- gsub("_([0-9]{4}_[0-9]{3})", "", names(raster_pixels))

# Export for browsing in a GIS 
write_sf(raster_pixels, paste0(tile_id, "_pixelids.shp"))

# Set palette
palette <- c(empty1 = NA,
             ground2 = "#A68B03",
             vegetation3 = "#4F7302", #"#2B8C83" or this green here "#83A603" 
             vegetation4 = "#4F7302", #"#2B8C83",
             vegetation5 = "#4F7302", #"#2B8C83",
             buildings6 = "#4F7302",
             empty7 = NA,
             empty8 = NA,
             water9 = "#5C73F2") # or "#5752D9")

# Function to extract pixel based on footpring
crop_laz_to_pixel <- function(pixel){
  pixel_bounds <- raster_pixels %>%
    filter(pixel_id == pixel) %>%
    st_bbox()
  clip_rectangle(tile_laz,
                 pixel_bounds['xmin'], pixel_bounds['ymin'],
                 pixel_bounds['xmax'], pixel_bounds['ymax'])
}

# Function to plot pixel
plot_10m_pixel <- function(pixel, out_file = "test.png"){

  # Generate pixel pointcloud
  pixel_laz <- crop_laz_to_pixel(pixel)
  
  # Filter point cloud for only classified pixels
  pixel_laz <- filter_poi(pixel_laz, Classification %in% c(2,3,4,5,6,9))
  
  # Subset palette
  unique_classes <- unique(pixel_laz@data$Classification)
  palette <- palette[sort(unique_classes)]
  
  # Set viewpoint parameters
  # use the following line to save "good looking" parameters from a plot window
  # um <- par3d()$userMatrix
  # Pre-defined paramters:
  um <- rbind(c(0.67814875,  0.734917164, 0.003316864,    0),
              c(-0.01463961,  0.008996292, 0.999852240,    0),
              c(0.73477894, -0.678097069, 0.016859649,    0),
              c(0.00000000,  0.000000000, 0.000000000,    1))
  
  # Base plot
  offsets <- plot(pixel_laz, color = "Classification",
                bg = "white", #"#232223", 
                size = 2, colorPalette = palette)
  
  # Set viewpoing
  rgl.viewpoint(userMatrix = um)
  
  # Add pixel footprint
  pixel_bounds <- raster_pixels %>%
    filter(pixel_id == pixel) %>%
    st_bbox()
  rgl.quads(x = c(pixel_bounds['xmin'], pixel_bounds['xmax'], 
                pixel_bounds['xmax'], pixel_bounds['xmin']) - offsets[1],
          y = c(pixel_bounds['ymin'], pixel_bounds['ymin'], 
                pixel_bounds['ymax'], pixel_bounds['ymax']) - offsets[2],
          z = c(0,0,0,0), 
          col = "#505050", #grey",
          lit = F, front = "lines",
          line_antialias = T)

  # Add z axis (line, ticks, lables)
  rgl.lines(x = c(0,0), y = c(0,0), z = c(0,30), 
            col = "#505050", #"grey", or "#808080"
            line_antialias =T)
  rgl.points(x = rep(0,7), y = rep(0,7), z = seq(0,30,5), pch = "-",
             col = "#505050")
  rgl.texts(x = rep(0,7), y = rep(0,7), z = seq(0,30,5), text = paste0(seq(0,30,5), " m"), 
            col = "#505050", #"white", or "#808080"
            adj = c(1.25, 0.25), cex = 1.5, alpha = 1)
  
  # Annotate pixel footprint dimensions
  rgl.texts(x = c(6.05,12), y = c(-4.55, 2), z = c(0,0), text = c("10 m", "10 m"), 
            col = "#505050", #white", or "#808080"
            adj = c(0,0), cex = 1.5)
  
  # Export to file
  snapshot3d(out_file, height = 650, width = 550)
}

# Set pixels
pixel_ids <- sort(c("x29y59",
                    "x56y51",
                    "x63y40",
                    "x67y44"))
# Set order of plotting
pixel_order <- c(2,3,1,4)

# Generate pixel plots 
mapply(plot_10m_pixel, pixel_ids, paste0(pixel_ids, ".png"))

# Combine into one matrix
pngs <- list.files(".", "*.png") 
pngs <- pngs[grep("x[0-9]{2}y[0-9]{2}.*", pngs)]

pixel_plots <- lapply(pngs, function(x){
  img <- image_read(x) %>% image_crop("300x520+110+70")
  ggdraw() +
    draw_image(img)
})
pixel_plots <- plot_grid(plotlist = pixel_plots[pixel_order], ncol = 4,
                         labels = "auto",
                         label_colour = "black" #"white"
)
save_plot("figure_1_top_panel.png", 
          pixel_plots,
          base_aspect_ratio = (4*300)/520)

pallete_variables <- data.frame(
  variable_name = c("ground_point_count_.01m.01m",
                    "water_point_count_.01m.01m",
                    "vegetation_point_count_00m.50m",
                    "point_density",
                    "canopy_height",
                    "normalized_z_sd",
                    "amplitude_mean"),
  variable_name_pretty = c("Ground Pts.",
                           "Water Pts.",
                           "Veg. Pts.",
                           "",
                           "Canopy H.",
                           "Norm. z sd",
                           "Ampl. Mean"),
  scale_factor = c(1,1,1,1,0.01,0.01,1),
  decimals = c(0,0,0,0,1,1,1),
  unit = c("","","",""," m", " m", ""),
  colours = c(
    palette["ground2"],
    palette["water9"],
    palette["vegetation3"],
    palette["vegetation3"],
    "#8D00BF",
    "#505050",
    "#505050"),
  range_min = c(0, 0, 0, 0, 0, NA, NA),
  range_max = NA,
  stringsAsFactors = F)
# Gather min and max values
pallete_variables$range_min[pallete_variables$variable_name == "normalized_z_sd"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(min = min(normalized_z_sd)) %>%
  pull(min)
pallete_variables$range_min[pallete_variables$variable_name == "amplitude_mean"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(min = min(amplitude_mean)) %>%
  pull(min)
pallete_variables$range_max[pallete_variables$variable_name == "ground_point_count_.01m.01m"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(max = max(ground_point_count_.01m.01m)) %>%
  pull(max)
pallete_variables$range_max[pallete_variables$variable_name == "water_point_count_.01m.01m"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(max = max(water_point_count_.01m.01m)) %>%
  pull(max)
pallete_variables$range_max[pallete_variables$variable_name == "vegetation_point_count_00m.50m"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(max = max(vegetation_point_count_00m.50m)) %>%
  pull(max)
pallete_variables$range_max[pallete_variables$variable_name == "canopy_height"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(max = max(canopy_height)) %>%
  pull(max)
pallete_variables$range_max[pallete_variables$variable_name == "normalized_z_sd"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(max = max(normalized_z_sd)) %>%
  pull(max)
pallete_variables$range_max[pallete_variables$variable_name == "amplitude_mean"] <-
  filter(raster_pixels, pixel_id %in% pixel_ids) %>%
  summarise(max = max(amplitude_mean)) %>%
  pull(max)

# Define function to draw a polygon with annotations
draw_poly <- function(pixel, variable){
  if(variable == "point_density"){
    
    # Extract vegetation proportion per height bin
    pixel_values <- raster_pixels %>% filter(pixel_id == pixel) %>%
      select(contains("vegetation_proportion")) %>%
      st_drop_geometry() %>%
      pivot_longer(cols = everything(), names_to = "variable", values_to = "fraction") %>%
      mutate(min_height = as.numeric(gsub(".*_([0-9]{2}\\.?[0-9]?)m\\..*", "\\1", variable)),
             max_height = as.numeric(gsub(".*\\.([0-9]{2}\\.?[0-9]?)m$", "\\1", variable)),
             range_height = max_height - min_height,
             centre_height = (max_height + min_height) / 2,
             fraction = fraction / 10000)
    
    # Adjust the last value for aesthetical pruposes
    pixel_values$max_height[pixel_values$min_height == 25] <- 30
    pixel_values$centre_height[pixel_values$min_height == 25] <- 27.5
    pixel_values$range_height[pixel_values$min_height == 25] <- 5
    
    # Set maximum proportion and round up
    max_prop <- filter(raster_pixels, pixel_id %in% pixel_ids) %>%
      select(contains("vegetation_proportion")) %>%
      st_drop_geometry() %>%
      pivot_longer(cols = everything(), names_to = "variable", values_to = "fraction") %>%
      summarise(max = max(fraction)) %>%
      pull(max) 
    max_prop <- ceiling((max_prop / 10000) * 10)/ 10
    
    # Plot RDF:
    poly_plot <- ggplot(pixel_values, 
                        aes(x = centre_height,
                            y = fraction * 100, 
                            width = range_height)) +
      geom_bar(stat = "identity",
               position = "identity", 
               colour = "#505050", 
               fill = pallete_variables$colours[pallete_variables$variable_name == variable]) +
      scale_x_continuous(limits = c(0,30), breaks = seq(0,30, 10),
                         labels = paste0(seq(0,30, 10), " m"),
                         sec.axis=sec_axis(~., breaks = NULL)) +
      scale_y_continuous(limits = c(0,max_prop) * 100, 
                         breaks = seq(0, max_prop, 0.1) * 100,
                         labels = paste0(seq(0, max_prop, 0.1) * 100, " %"),
                         sec.axis=sec_axis(~., breaks = NULL)) +
      labs(x = "", y = "") +
      theme_cowplot(14) +
      theme(panel.background = element_rect(colour = "black", size=0.25),
            axis.title = element_blank(), 
            axis.text = element_text(colour = "#505050"),
            axis.line = element_line(colour = "#505050"),
            axis.ticks = element_line(colour = "#505050"),
            plot.margin=unit(c(1.5,9,4.5,13.5), "mm"))
  
  } else {
    # get pixel value
    pixel_value <- raster_pixels %>% filter(pixel_id == pixel) %>%
      pull(get(variable))
    
    # Set scale
    colour_ramp <-  pallete_variables %>% filter(variable_name == variable) %>%
      pull(colours)
    colour_ramp <- colorRampPalette(c("white", colour_ramp))(101)
    
    # Determine colour
    range_min <- pallete_variables %>% filter(variable_name == variable) %>% 
      pull(range_min) %>% unique()
    range <- pallete_variables %>% filter(variable_name == variable) %>%
      mutate(range = range_max - range_min) %>% pull(range) %>% unique()
    ramp_position <- floor(((pixel_value - range_min) / range * 100) + 1)
    pixel_colour <- colour_ramp[ramp_position]
    
    # Set pixel text colour
    if(ramp_position <= 50) { 
      pixel_text_colour <- "#505050"
    } else pixel_text_colour <- "white"
    
    # Scale and round variable
    pixel_value <- formatC(pixel_value * unique(pallete_variables$scale_factor[pallete_variables$variable_name == variable]),
                           digits = unique(pallete_variables$decimals[pallete_variables$variable_name == variable]),
                           format = "f")
    
    # Set pixel text
    pixel_text <- paste0(pixel_value, unique(pallete_variables$unit[pallete_variables$variable_name == variable]))
    
    # Get pretty variable name
    variable_name_pretty <- pallete_variables %>% filter(variable_name == variable) %>% 
      pull(variable_name_pretty) %>% unique()
    
    # Plot "pixel" polygon
    poly_plot <- ggplot() +
      geom_polygon(aes(x = x, 
                       y = y),
                   data = data.frame(x = c(0,190,380,185),
                                     y = c(100,165,90,0)),
                   fill = pixel_colour,
                   colour = "#505050") +
      scale_x_continuous(expand = c(0,0)) +
      scale_y_continuous(expand = c(0,0)) +
      labs(x = "", y = "") +
      # annotate("text", x = 0, y = 165, hjust = 0, vjust = 1,
      #          label = variable_name_pretty, size = 2) +
      annotate("text", x = 190, y = 90, hjust = 0.5, vjust = 0.5,
               label = pixel_text, size = 6, colour = pixel_text_colour) +
      coord_cartesian() + 
      theme_nothing() +
      theme(axis.line = element_blank(),
            # panel.background = element_rect(fill = "red", colour = "black"),
            plot.title = element_text(face = "plain"),
            axis.ticks = element_blank(),
            axis.text = element_blank(),
            legend.margin=unit(0, "mm"),
            plot.margin=unit(c(1.5,9.5,1.5,24), "mm"),
            axis.ticks.length = unit(0, "mm"))
    # poly_plot <- ggplot_gtable(ggplot_build(poly_plot))
    # poly_plot$layout$clip[poly_plot$layout$name == "panel"] <- "off"
  }
  return(poly_plot)
}

poly_plot_list <- mapply(draw_poly, pixel_ids[as.vector(sapply(pixel_order, rep, length(pallete_variables$variable_name)))], 
                         rep(pallete_variables$variable_name, length(pixel_ids) ),
                         SIMPLIFY = F)
variable_plot <- plot_grid(
  plotlist = poly_plot_list, 
  ncol = length(pixel_ids),
          byrow = F, 
          rel_heights = c(1,1,1,1.5,1,1,1),
  labels = as.vector(sapply(pallete_variables$variable_name_pretty,
                    function(x) c(x, rep("", (length(pixel_ids)-1))))),
  label_fontface = "bold",
  label_size = 18,
  label_colour = "#505050",
  label_y = 1.1,
  label_x = 0.03,
  hjust = 0,
  vjust = 1)

# save_plot("figure_1_bottom_oanel.png", variable_plot,
#           ncol = length(pixel_ids),
#           nrow =  length(pallete_variables$variable_name),
#           base_asp = 2.5,
#           base_height = 1.5)
# Composite both plots

# Combine top and bottom into one panel
save_plot("figure_1.png",
          plot_grid(
            ggdraw() +
              draw_image(image_read("figure_1_top_panel.png")),  
          variable_plot,
  nrow= 2, 
  rel_heights = c(1,1.2)),
  base_asp = (4*300)/(0.95*(4*300)),
  base_height = 12)

