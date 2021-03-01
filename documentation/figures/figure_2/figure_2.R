# Visualisation of DTM derived variables for manuscript
# Jakob J. Assmann j.assmann@bio.au.dk Feb 2021

# Dependencies
library(raster)
library(rasterVis)
library(rayshader)
library(cowplot)
library(tidyverse)
library(colorspace)
library(magick)

# Set wd
setwd("D:/Jakob/dk_nationwide_lidar/documentation/figures/figure_2")

# Set target tile id (Mol's Bjerge)
tile_id <- "6230_595"

# Set folder paths
dtm_10m <- "D:/Jakob/dk_nationwide_lidar/data/outputs/dtm_10m"
aspect <- "D:/Jakob/dk_nationwide_lidar/data/outputs/aspect"
slope <- "D:/Jakob/dk_nationwide_lidar/data/outputs/slope"
heat_load_index <- "D:/Jakob/dk_nationwide_lidar/data/outputs/heat_load_index/"
solar_radiation <- "D:/Jakob/dk_nationwide_lidar/data/outputs/solar_radiation/"
openness_mean <- "D:/Jakob/dk_nationwide_lidar/data/outputs/openness_mean"
openness_difference <- "D:/Jakob/dk_nationwide_lidar/data/outputs/openness_difference"
twi <- "D:/Jakob/dk_nationwide_lidar/data/outputs/twi"

# Load rasters
dtm_10m_raster <- raster(paste0(dtm_10m, "/dtm_10m_", tile_id, ".tif"))/ 100
aspect_raster <- raster(paste0(aspect, "/aspect_", tile_id, ".tif"))/ 10
slope_raster <- raster(paste0(slope, "/slope_", tile_id, ".tif"))/ 10
heat_load_index_raster <- raster(paste0(heat_load_index, "/heat_load_index_", tile_id, ".tif"))/ 10000
solar_radiation_raster <- raster(paste0(solar_radiation, "/solar_rad_", tile_id, ".tif"))/ 1000
openness_mean_raster <- raster(paste0(openness_mean, "/openness_mean_", tile_id, ".tif"))
openness_difference_raster <- raster(paste0(openness_difference, "/openness_difference_", tile_id, ".tif"))
twi <- raster(paste0(twi, "/twi_", tile_id, ".tif"))/ 1000

# Load orthomosaic and reduce size for easier handling
# ortho <- stack("6230_594_ortho_2014.tif")
# ortho <- crop(ortho, dtm_10m_raster)
# ortho <- aggregate(ortho, 12)
# writeRaster(ortho, paste0("ortho_", tile_id, "_aggregated.tif"), overwrite = T)
ortho <- stack(paste0("ortho_", tile_id, "_aggregated.tif"))
# plotRGB(ortho)

# List rasters for convenience
raster_list <- list(dtm_10m_raster,
     aspect_raster,
     slope_raster,
     heat_load_index_raster,
     solar_radiation_raster,
     openness_mean_raster,
     openness_difference_raster,
     twi)

# Write quick function to plot overview of rasters
plot_dtm_variable <- function(raster_name){
  variable <- gsub("_[0-9]{4}_[0-9]{3}", "", names(raster_name))
  as_grob(levelplot(raster_name,
                    main = variable,
                    margin = F,
                    scales = list(draw=F)))
}
raster_plot_list <- lapply(raster_list, plot_dtm_variable)
plot_grid(plotlist = raster_plot_list)

# solar radiation has skweed normal distribution let's adjust
hist(solar_radiation_raster)
solar_radiation_raster_adjusted <- solar_radiation_raster
solar_radiation_raster_adjusted[solar_radiation_raster_adjusted[] <= quantile(solar_radiation_raster_adjusted, 0.05)] <- quantile(solar_radiation_raster_adjusted, 0.05)

## Rayshader
# Prepare DTM baselayer
dtm_10m_mat <- raster_to_matrix(dtm_10m_raster)

# Definte funciton to generate 3D RGB from a single band raster using a palette
# Test objets
 # raster_object <- openness_difference_raster
# colour_ramp <- colorRampPalette(c("#000000", "#FFFFFF"))(100)
# colour_ramp <- viridisLite::viridis(100)
# n_breaks <- 100
# min_value <- 0
# max_value <- 40
# file_name <- "test.png"
# cut raster into 99 intervals

plot_variable_in_3d <- function(raster_object, file_name, colour_ramp, min_value, max_value, n_breaks){
  # Cut raster into breaks for colour asignment
  raster_object_cut <- cut(raster_object, seq(min_value, max_value, length.out = n_breaks), include.lowest = T)
  # Convert to matrix for rayshader
  raster_object_matrix <- raster_to_matrix(raster_object_cut)
  
  # Create empty RGB array
  raster_object_rgb_array <- array(0,dim=c(nrow(raster_object_matrix),ncol(raster_object_matrix),3))
  
  # Fill array with RGB values based on ramp
  for(i in 1:nrow(raster_object_matrix)){
    for(j in 1:ncol(raster_object_matrix)) {
      pixel_value <- raster_object_matrix[i,j]
      pixel_rgb <- col2rgb(colour_ramp[pixel_value])
      raster_object_rgb_array[i,j,1] <- pixel_rgb[1] / 255
      raster_object_rgb_array[i,j,2] <- pixel_rgb[2] / 255
      raster_object_rgb_array[i,j,3] <- pixel_rgb[3] / 255
    }
  }
  # Rotate array for rayshader
  raster_object_rgb_array <- aperm(raster_object_rgb_array, c(2,1,3))
  
  # Plot output for QC
  #plot_map(raster_object_rgb_array)
  
  # Add shadow and plot
  rgl::rgl.clear()
  raster_object_rgb_array %>%
    plot_3d(dtm_10m_mat,
            windowsize = c(1000, 800),
            zscale = 5,
            zoom = 0.75)
  render_snapshot(file_name)
  rgl::rgl.close()
  
  # Return raser RGB array
  return(raster_object_rgb_array)
}
mapply(plot_variable_in_3d,
       list(dtm_10m_raster,
            aspect_raster,
            slope_raster,
            heat_load_index_raster,
            solar_radiation_raster_adjusted,
            openness_mean_raster,
            openness_difference_raster,
            twi),
       paste0("sub_plots/", c("dtm_10m.png",
                             "aspect.png",
                             "slope.png",
                             "heat_load_index.png",
                             "solar_radiation.png",
                             "openness_mean.png",
                             "openness_difference.png",
                             "twi.png")),
       list(sequential_hcl(99, palette = "DarkMint"),
            diverging_hcl(99, palette = "Berlin"),
            sequential_hcl(99, palette = "Plasma"),
            sequential_hcl(99, palette = "Blues3", rev = T),
            sequential_hcl(99, palette = "Inferno"),
            sequential_hcl(99, palette = "Viridis"),
            sequential_hcl(99, palette = "Viridis"),
            sequential_hcl(99, palette = "Blues3", rev = T)),
       min_value = c(25,0,0,0,0.65, 75,0, 0),
       max_value = c(125,360,30,1,0.85, 95, 40, 20),
       n_breaks = 100,
       SIMPLIFY = F)

# Add ortho plot
ortho_r <- rayshader::raster_to_matrix(ortho[[1]])
ortho_g <- rayshader::raster_to_matrix(ortho[[2]])
ortho_b <- rayshader::raster_to_matrix(ortho[[3]])

ortho_rgb_array <- array(0,dim=c(nrow(ortho_r),ncol(ortho_r),3))

ortho_rgb_array[,,1] <- ortho_r/255 #Red layer
ortho_rgb_array[,,2] <- ortho_g/255 #Blue layer
ortho_rgb_array[,,3] <- ortho_b/255 #Green layer

ortho_rgb_array <- aperm(ortho_rgb_array, c(2,1,3))
ortho_rgb_array %>%
  #add_shadow(ray_shade(dtm_10m_mat, zscale = 5), 0.8) %>%
  plot_3d(dtm_10m_mat,
          windowsize = c(1000, 800),
          zscale = 5,
          zoom = 0.75)
render_snapshot("sub_plots/ortho.png")
rgl::rgl.close()

# Assemble plot grid
variable_plots <- lapply(list.files("sub_plots/", full.names = T), function(x){
  if(grepl("ortho", x)){
    ggdraw() + draw_image(image_read(x)) +
      draw_label("1 km", x= 0.225, y = 0.25, size = 20, angle = -38, fontface = "bold") +
      draw_label("→", x= 1-0.245, y = 0.27, size = 40, angle = +41, fontface = "bold") +
      draw_label("N", x= 1-0.2, y = 0.2, size = 20, angle = -46, fontface = "bold")
  } else {
    ggdraw() + draw_image(image_read(x))
  }
} )
names(variable_plots) <- gsub(".png", "", list.files("sub_plots/", full.names = F))
save_plot("figure_2_raw.png", plot_grid(plotlist = variable_plots,
          ncol = 3),
          base_asp = 1,
          base_height = 8)

# Set parameters for histogram plots
hist_parameters <- data.frame(
  variable_name = c("dtm_10m",
                    "aspect",
                    "slope",
                    "heat_load_index",
                    "solar_rad",
                    "openness_mean",
                    "openness_difference",
                    "twi"),
  x_min = c(25,0,0,0,0.65, 75,0, 5),
  x_max = c(125,360,30,1,0.85, 95, 40, 20),
  n_breaks = 100,
  y_max = c(700, 300, 400, 500, 700, 3000, 700, 1000),
  x_title = c("Height asl (m)",
              "Aspect (°)",
              "Slope (°)",
              "Heat Load Index (unitless)",
           "Solar Radiation (ln(MJ/cm2/yr))",
           "Openness Mean (°)",
           "Openness Difference (°)",
           "TWI (unitless)")
)
# Write function to generate histograms
plot_histogram <- function(raster_object, colour_ramp) {
  raster_df <- as.data.frame(raster_object)
  variable_name <- gsub("_[0-9]{4}_[0-9]{3}", "", names(raster_df))
  cat(variable_name, "\n")
  names(raster_df) <- "x"
  breaks <- seq(hist_parameters$x_min[hist_parameters$variable_name == variable_name], 
                hist_parameters$x_max[hist_parameters$variable_name == variable_name], 
                length.out = hist_parameters$n_breaks[hist_parameters$variable_name == variable_name])
  breaks_centre <- NA
  breaks_centre[1:(length(breaks)-1)] <- NA
  for(i in 1:length(breaks_centre)) breaks_centre[i] <- (breaks[i + 1] + breaks[i])/2 
  raster_df$col <- as.data.frame(cut(raster_object, breaks, include.lowest = T))[,1]
  cat("Warning: ", sum(is.na(raster_df$col)), "NA values. These need to be adressed!\n")
  raster_df<- raster_df %>% group_by(col) %>%
    summarise(n_x = n()) %>% na.omit()
  if(sum(!(1:length(breaks_centre) %in% raster_df$col)) > 0){
  raster_df <- data.frame(n_x = 0,
                          col = (1:length(breaks_centre))[!(1:length(breaks_centre) %in% raster_df$col)]) %>%
     bind_rows(raster_df)  }
  raster_df <- raster_df%>% arrange(col) %>%
    mutate(x_centre = breaks_centre) %>%
    mutate(col = as.factor(col)) %>%
    mutate(bar_lower = hist_parameters$y_max[hist_parameters$variable_name == variable_name] * -0.2) 

  
  hist_plot <- ggplot(raster_df, aes(x = x_centre, y = n_x, fill = col, colour = col)) +
    geom_col(width =  resolution(raster_df$x_centre), colour = "#505050", size = 0.005) +
    geom_col(aes(x = x_centre, y = bar_lower),
             width = resolution(raster_df$x_centre), size = 1) +
    scale_fill_manual(values = colour_ramp) +
    scale_colour_manual(values = colour_ramp) +
    scale_x_continuous(limits = c(raster_df$x_centre[1] - resolution(raster_df$x_centre),
                                  raster_df$x_centre[99] + resolution(raster_df$x_centre)),
                       expand = c(0,0)) +
    scale_y_continuous(limits = c(raster_df$bar_lower[1],
                                  hist_parameters$y_max[hist_parameters$variable_name == variable_name]),
                       expand = c(0,0)) +
    annotate("rect", 
             xmin = raster_df$x_centre[1] - resolution(raster_df$x_centre),
             xmax = raster_df$x_centre[99] + resolution(raster_df$x_centre),
             ymin = raster_df$bar_lower[1],
             ymax = 0,
             fill = NA, 
             colour = "black",
             size = 0.75) +
    labs(x = hist_parameters$x_title[hist_parameters$variable_name == variable_name], 
         y = "n pixels") +
    coord_cartesian(clip = "off") +
    theme_cowplot(18) +
    theme(legend.position = "none",
          plot.margin = margin(1, 1, 1, 0.25, "inch"),
          axis.title.y = element_text(hjust = 0.7))
  
  hist_plot
  return(hist_plot)
}
hist_plots <- mapply(plot_histogram,
       list("dtm_10m" = dtm_10m_raster,
            "aspect" = aspect_raster,
            "slope" = slope_raster,
            "heat_load_index" = heat_load_index_raster,
            "solar_radiation" = solar_radiation_raster,
            "openness_mean" = openness_mean_raster,
            "openness_difference" = openness_difference_raster,
            "twi" = twi),
       list(sequential_hcl(99, palette = "DarkMint"),
            diverging_hcl(99, palette = "Berlin"),
            sequential_hcl(99, palette = "Plasma"),
            sequential_hcl(99, palette = "Blues3", rev = T),
            sequential_hcl(99, palette = "Inferno"),
            sequential_hcl(99, palette = "Viridis"),
            sequential_hcl(99, palette = "Viridis"),
            sequential_hcl(99, palette = "Blues3", rev = T)),
       SIMPLIFY = F)
save_plot("figure_2_hists.png", plot_grid(plotlist = hist_plots),
          base_height = 8)


# Combine the 3D raster plots and historgrams into one plot.
combined_plot_list <- lapply(c("ortho",
                                      "dtm_10m",
                                      "aspect",
                                      "slope",
                                      "heat_load_index",
                                      "solar_radiation",
                                      "openness_mean",
                                      "openness_difference",
                                      "twi"), function(x) {
                                        if(x == "ortho") {
                                          plot_grid(variable_plots[[x]],
                                                    (ggplot() +geom_blank() + theme_nothing()),
                                                    rel_widths = c(1,1))
                                          # variable_plots[[x]]
                                        } else {
                                          plot_grid(variable_plots[[x]],
                                                    hist_plots[[x]],
                                                    rel_widths = c(1,1))
                                        }
                                      })

combined_plot <- plot_grid(
  plotlist =combined_plot_list ,
  ncol = 3,
  labels = paste0(
                  # letters[1:9], ") " , 
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

save_plot("figure_2.png", combined_plot,
          base_height = 4,
          base_aspect_ratio = 2,
          ncol = 3,
          nrow = 3)

# Legacy code
pixel_grid <- as(dtm_10m_raster, "SpatialPolygonsDataFrame") %>%
  st_as_sf() %>% st_cast("LINESTRING")
plot(pixel_grid)

# Legacy code
dtm_10m_with_grid <- raster_object_rgb_array %>%
  add_overlay(generate_line_overlay(pixel_grid, heightmap = dtm_10m_mat,
                                    extent = extent(dtm_10m_raster), color = "darkred",
                                    linewidth = 0.0001)) %>%
  plot_3d(dtm_10m_with_grid, dtm_10m_mat, zscale = 10)      
