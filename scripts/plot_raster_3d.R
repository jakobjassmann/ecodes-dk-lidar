# Handy wrapper functions to quickly generate oublishable 3D rasterplots 
# using the rayshader package
# Jakob Assmann j.assmann@bio.au.dk 9 March 2021

# Dependencies
library(raster)
library(rayshader)
library(cowplot)
library(tidyverse)
library(colorspace)
library(magick)

#' Publication ready 3D plots for single-layer raster objects
#'
#' Visualises a single raster layer as a 3D tile with heights being  single layer
#' rasters, mapping the raster values using a colour scale.
#' 
#' Default parameters work best for square rasters. 
#' 
#' @param raster_object A single layer raster object
#' @param dtm_raster A digital terrain model raster, defaults to a zero height raster generated from the raster_object. 
#' @param output_file A PNG output file to write the plot to.
#' @param 	 A colour ramp vector or a single string specifing a sequential colour ramp name of the colorspace apackage. 
#' @param invert_ramp Logical. Invert colour ramp. 
#' @param min_value Minimum value for the colour ramp.  
#' @param max_value Maximum vale for the colour ramp. 
#' @param n_steps Number of steps in the colour ramp. 
#' @param z_scale Scale factor for the height, defaults to the x resolution of the dtm raster. 
#' @param plot_width Plot width in pixels. 
#' @param plot_height Plot height in pixels.
#' @param plot_phi View azimuth. 
#' @param plot_theta View rotation.
#' @param plot_zoom View zoom.
#'
#' @return A ggpot grob of the rendered snapshot image. 
#' @export
#'
#' @examples
#' 
#' # Suare crop of volcano dtm 
#' volcano_raster <- raster(nrow = 60, ncol = 60, extent(0, 600, 0, 600), crs = NA, vals = volcano[1:60,1:60])
#' 
#' # Plot with correct x, y and z proportions. 
#' plot_raster_3d(volcano_raster, volcano_raster)
#' 
#' # Amplify elevation by a factor of 2
#' plot_raster_3d(volcano_raster, volcano_raster, z_scale = res(volcano_raster)[1] / 2)
#' 
#' # Change colour ramp
#' plot_raster_3d(volcano_raster, volcano_raster, colour_ramp = "Blues3")
#' 
#' # Invert colour ramp
#' plot_raster_3d(volcano_raster, volcano_raster, invert_ramp = T)
#' 

plot_raster_3d <- function(raster_object, 
                           dtm_raster = NULL,
                           output_file = NULL, 
                           colour_ramp = "Plasma", 
                           invert_ramp = F, 
                           min_value = NULL, 
                           max_value = NULL, 
                           n_steps = NULL,
                           z_scale = NULL,
                           plot_width = 1000,
                           plot_height = 800,
                           plot_phi = 45,
                           plot_theta = 45,
                           plot_zoom = 0.75){
  
  # Check whether raster object was supplied
  if(class(raster_object) != "RasterLayer") stop("Please supply a single layer raster object!")
  
  # Check whether dtm was supplied if not generate a 0 height raster
  if(is.null(dtm_raster)) {
    warning("No dtm_raster supplied, using null raster!")
    dtm_raster <- setValues(raster_object, 0)
  } 
  
  ## Prepare graphical parameters
  
  # Set min and max values if needed
  if(is.null(min_value)) min_value <- cellStats(raster_object, min)
  if(is.null(max_value)) max_value <- cellStats(raster_object, max)
  
  # Create / check colour ramp if needed
  # If single string, assume it's the name of a sequential "colorspace" ramp
  if(length(colour_ramp) == 1) {
    # Assign 100 breaks if not specified
    if(is.null(n_steps)) n_steps <- 100
    # Set colour ramp
    colour_ramp <- sequential_hcl(n_steps, palette = colour_ramp, rev = invert_ramp)
  } else if (length(colour_ramp) >= 1){
    if(is.null(n_steps)) n_steps <- length(colour_ramp)
    if(n_steps != (length(colour_ramp))){
      warning("Length of colour_ramp and n_steps do not match!\nUsing length of colour_ramp as n_steps.")
      n_steps <- length(colour_ramp)
    }
  }
  
  # Set z_scale parameter if needed
  if(is.null(z_scale)) {
    warning("No z_scale parameter specified!\nUsing x resolution of the dtm_raster.")
    z_scale <- res(dtm_raster)[1]
  }
  
  ## Raster preparations
  
  # Cut raster into breaks for colour asignment
  raster_object_cut <- cut(raster_object, seq(min_value, max_value, length.out = n_steps + 1), include.lowest = T)
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
  
  # Prepare DTM baselayer
  dtm_raster_mat <- raster_to_matrix(dtm_raster)
  
  # Set temp file if needed
  if(is.null(output_file)){
    temp <- T
    output_file <- tempfile(fileext = ".png")
  } else {
    temp <- F
  }
  
  # Write out plot
  rgl::rgl.clear()
  raster_object_rgb_array %>%
    plot_3d(dtm_raster_mat,
            windowsize = c(plot_width, plot_height),
            zscale = z_scale,
            theta = plot_theta,
            phi = plot_phi,
            zoom = plot_zoom)
  render_snapshot(output_file)
  rgl::rgl.close()
  
  # Load plot as ggplot grob
  raster_rgb_plot <- ggdraw() + draw_image(image_read(output_file))
  
  # Remove temp file if needed
  if(temp) file.remove(output_file)
  
  # Return plot grob
  return(raster_rgb_plot)
}

#' Coloured histograms and colourscale bars for 3D raster plots
#'
#' Convenience function to generate a histogram / colour scale bar to accompany plot_raster_3d() outputs.
#'
#' @param raster_object Single-layer raster object to generate histogram / colour scale bar for.
#' @param variable_name Title for the x-axis.
#' @param colour_ramp A colour ramp vector or a single string specifing a sequential colour ramp name of the colorspace apackage. 
#' @param min_value Minimum value for the colour ramp.  
#' @param max_value Maximum vale for the colour ramp. 
#' @param n_steps Number of steps in the colour ramp. 
#' @param y_max Upper limit for the y-axix, defaults to the maximum pxiel count.
#' @param colour_bar_only Logical, plot histogram or colour scale bar only. 
#'
#' @return Ggplot object
#' @export
#'
#' @examples
#' 
#' # Square crop of volcano dtm
#' volcano_raster <- raster(nrow = 60, ncol = 60, extent(0, 600, 0, 600), crs = NA, vals = volcano[1:60,1:60])
#' 
#' # Generate histogram and colour bar
#' plot_raster_hist_bar(volcano_raster, "Height asl (m)")
#' 
#' # Set min and max value
#' plot_raster_hist_bar(volcano_raster,  "Height asl (m)", min_value = 100, max_value = 200)
#' 
#' # Colour bar only
#' plot_raster_hist_bar(volcano_raster, "Height asl (m)", min_value = 100, max_value = 200, colour_bar_only = T)
#' 
#' # Change colour ramp
#' plot_raster_hist_bar(volcano_raster, "Height asl (m)", colour_ramp = "Blues3", min_value = 100, max_value = 200, colour_bar_only = T)
#' 

plot_raster_hist_bar <- function(raster_object,
                                 variable_name = "Raster Value",
                                 colour_ramp = "Plasma", 
                                 min_value = NULL, 
                                 max_value = NULL, 
                                 n_steps = NULL,
                                 y_max = NULL,
                                 colour_bar_only = F,
                                 font_size = 18) {
  
  # Convert raster object to data frame
  raster_df <- as.data.frame(raster_object)
  
  # Overwrite column names for ease of data handling
  names(raster_df) <- "x"
  
  # Set min, max and n_steps
  if(is.null(min_value)) min_value <- min(raster_df$x, na.rm = T)
  if(is.null(max_value)) max_value <- max(raster_df$x, na.rm = T)
  
  # Create / check colour ramp if needed
  # If a single string, assume it's the name of a sequential "colorspace" ramp
  if(length(colour_ramp) == 1) {
    # Assign 100 breaks if not specified
    if(is.null(n_steps)) n_steps <- 100
    # Set colour ramp
    colour_ramp <- sequential_hcl(n_steps, palette = colour_ramp)
  } else if (length(colour_ramp) >= 1){
    if(is.null(n_steps)) n_steps <- length(colour_ramp)
    if(n_steps != (length(colour_ramp))){
      warning("Length of colour_ramp and n_steps do not match!\nUsing length of colour_ramp as n_steps.")
      n_steps <- length(colour_ramp)
    }
  }
  
  # Set breaks and calculate centres
  breaks <- seq(min_value, max_value, length.out = n_steps + 1)
  breaks_centre <- NA
  breaks_centre[1:(length(breaks)-1)] <- NA
  for(i in 1:length(breaks_centre)) breaks_centre[i] <- (breaks[i + 1] + breaks[i])/2 
  
  # Cur raster values by breaks 
  raster_df$col <- as.data.frame(cut(raster_object, breaks, include.lowest = T))[,1]
  if( sum(is.na(raster_df$col)) > 0) warning("There were ", sum(is.na(raster_df$col)), " NA values in the colour assignment for ", variable_name, "!\nThese may need to be adressed!\n")
  
  # Calculate counts per break / bin
  raster_df<- raster_df %>% group_by(col) %>%
    summarise(n_x = n()) %>% na.omit()
  
  # Set "empty" breaks to zero
  if(sum(!(1:length(breaks_centre) %in% raster_df$col)) > 0){
    raster_df <- data.frame(n_x = 0,
                            col = (1:length(breaks_centre))[!(1:length(breaks_centre) %in% raster_df$col)]) %>%
      bind_rows(raster_df)  }
  
  # Set maximum count unless specified (10% above max value)
  if(is.null(y_max)) y_max <- max(raster_df$n_x, na.rm = T) * 1.1
  
  # Add extra colum with negative values to simulate a colour ramp (20% of max value below zero)
  raster_df <- raster_df%>% arrange(col) %>%
    mutate(x_centre = breaks_centre) %>%
    mutate(col = as.factor(col)) %>%
    mutate(bar_lower = y_max * -0.2) 
  
  # set x reolution
  x_res <- (raster_df$x_centre[2] - raster_df$x_centre[1])
  
  # Set xmin and xmax for plotting rectangles
  raster_df <- mutate(raster_df,
                      x_min = x_centre - (x_res / 2),
                      x_max = x_centre + (x_res / 2))

  ## Assemble plot
  # Histogram and colour scale bar
  if(!colour_bar_only){
    hist_plot <- ggplot(raster_df, aes(fill = col, colour = col)) +
      geom_rect(aes(xmin = x_min, xmax = x_max,
                    ymin = 0, ymax = n_x),
               colour = "#505050", size = 0.005) +
      geom_rect(aes(xmin = x_min, xmax = x_max,
                    ymin = bar_lower, ymax = 0),
               size = 0.005) +
      scale_fill_manual(values = colour_ramp) +
      scale_colour_manual(values = colour_ramp) +
      annotate("rect", 
               xmin = min_value,
               xmax = max_value,
               ymin = raster_df$bar_lower[1],
               ymax = 0,
               fill = NA, 
               colour = "black",
               size = 0.75) +
      labs(x = variable_name, 
           y = "n pixels") +
      coord_cartesian(xlim = c(min_value, max_value), 
                      ylim = c(raster_df$bar_lower[1],
                               y_max),
                      expand = F) +
      theme_cowplot(font_size) +
      theme(legend.position = "none",
            plot.margin = margin(1, 1, 1, 0.25, "inch"),
            axis.title.y = element_text(hjust = 0.7))
  } else{
    hist_plot <- ggplot(raster_df, aes(x = x_centre, y = n_x, fill = col, colour = col)) +
      geom_rect(aes(xmin = x_min, xmax = x_max,
                   ymin = bar_lower, ymax = 0),
               size = 1) +
      scale_fill_manual(values = colour_ramp) +
      scale_colour_manual(values = colour_ramp) +
      scale_x_continuous(limits = c(min_value, max_value),
                         # c(raster_df$x_centre[1] - resolution(raster_df$x_centre),
                         #          raster_df$x_centre[100] + resolution(raster_df$x_centre)),
                         expand = expansion(add = x_res*2)) +
      scale_y_continuous(limits = c(raster_df$bar_lower[1],
                                    0),
                         expand = c(0,0)) +
      annotate("rect", 
               xmin = min_value,
               xmax = max_value,
               ymin = raster_df$bar_lower[1],
               ymax = 0,
               fill = NA, 
               colour = "black",
               size = 0.75) +
      labs(x = variable_name, 
           y = "") +     
      coord_cartesian(xlim = c(min_value, max_value), 
                      ylim = c(raster_df$bar_lower[1],
                               0),
                      expand = F) +
      theme_cowplot(font_size) +
      theme(legend.position = "none",
            plot.margin = margin(1, 1, 1, 0.25, "inch"),
            axis.title.y = element_blank(),
            axis.ticks.y = element_blank(),
            axis.text.y = element_blank())
  }
  
  # Return plot
  return(hist_plot)
}

#' Side-by-side 3D plot of single-layer raster with histogram and colour bar
#'
#' Convenience wrapper for porducing a 3D plot with histogram and colour scale bar
#' for a single-layer raster object. Uses plot_raster_3d() and plot_raster_hist_bar(), 
#' see these functions for parameter descriptions. 
#'
#' @param colour_bar_y_pos Only used when colour_bar_only = T. Vertical position of the colour bar 0 to 1. 
#' @param colour_bar_height_factor Only used when colour_bar_only = T. Adjusts the relative height of the colour bar.
#'
#' @return A ggplot grid grob. 
#' @export
#'
#' @examples
#' 
#' #' # Square crop of volcano dtm
#' volcano_raster <- raster(nrow = 60, ncol = 60, extent(0, 600, 0, 600), crs = NA, vals = volcano[1:60,1:60])
#' 
#' # Generate 3D plot, histogram and colour bar
#' plot_raster_3d_combined(volcano_raster, volcano_raster, variable_name = "Height asl (m)")
#' 
#' # Generate 3D plot and colour bar only
#' plot_raster_3d_combined(volcano_raster, volcano_raster, variable_name = "Height asl (m)", colour_bar_only = T)
#' 
#' # Generate 3D plot and colour bar only, align with raster corner
#' plot_raster_3d_combined(volcano_raster, volcano_raster, variable_name = "Height asl (m)", colour_bar_only = T, colour_bar_y_pos = 0.43)
#' 
#' # Generate 3D plot and colour bar only with large colour bar
#' plot_raster_3d_combined(volcano_raster, volcano_raster, variable_name = "Height asl (m)", colour_bar_only = T, colour_bar_height_factor = 1)

plot_raster_3d_combined <- function(raster_object, 
                                    dtm_raster = NULL,
                                    output_file = NULL, 
                                    colour_ramp = "Plasma", 
                                    min_value = NULL, 
                                    max_value = NULL, 
                                    n_steps = NULL,
                                    z_scale = NULL,
                                    plot_width = 1000,
                                    plot_height = 800,
                                    plot_phi = 45,
                                    plot_theta = 45,
                                    plot_zoom = 0.75,
                                    variable_name = "Raster Value",
                                    y_max = NULL,
                                    font_size = 18,
                                    colour_bar_only = F,
                                    colour_bar_y_pos = 0.5,
                                    colour_bar_height_factor = 0.6 # Only needed if colour_bar_only = T. This looks good if both plots are equal in width and are of sufficient height. 
                                    ){
  # Check whether dtm was supplied if not generate a 0 height raster
  if(is.null(dtm_raster)) {
    warning("No dtm_raster supplied, using null raster!")
    dtm_raster <- setValues(raster_object[[1]], 0)
  } 
  
  # Generate 3D plot of raster
  raster_plot <- plot_raster_3d(raster_object = raster_object, 
                                dtm_raster = dtm_raster,
                                output_file = output_file, 
                                colour_ramp = colour_ramp, 
                                min_value = min_value, 
                                max_value = max_value, 
                                n_steps = n_steps,
                                z_scale = z_scale,
                                plot_width = plot_width,
                                plot_height = plot_height,
                                plot_phi = plot_phi,
                                plot_theta = plot_theta,
                                plot_zoom = plot_zoom)
  
  # Generate histogram / colour bar plot
  hist_bar_plot <- plot_raster_hist_bar(raster_object = raster_object,
                                        variable_name = variable_name,
                                        colour_ramp = colour_ramp, 
                                        min_value = min_value, 
                                        max_value = max_value, 
                                        n_steps = n_steps,
                                        y_max = y_max,
                                        font_size = font_size,
                                        colour_bar_only = colour_bar_only)
  # Colur scale bar only? -> reduce height to 20% of plot size
  if(colour_bar_only) {
    hist_bar_plot <- ggdraw() +
      draw_plot(hist_bar_plot,
                x = 0.5,
                y = colour_bar_y_pos,
                hjust = 0.5,
                vjust = 0.5,
                height = colour_bar_height_factor) 
  }
  
  # Combine into grid grob:
  raster_plot_grid <- plot_grid(raster_plot,
                                hist_bar_plot)
  
  # Return grob
  return(raster_plot_grid)
}

#' Convenient 3D plots for RGB raster stacks / bricks.
#'
#' Visualises RGB raster stacks / bricks in 3D, (optionally) based on a digital terrain model. Developed for orthophotos (for which no shading is required).
#' 
#' Default parameters work best for square rasters.  
#'
#' @param raster_stack RGB RasterStack or RasterBrick. First three layers must contain R, G and B bands in that order.
#' @param dtm_raster A digital elevation model. 
#' @param output_file A digital terrain model raster, defaults to a zero height raster generated from the raster_object. 
#' @param z_scale A PNG output file to write the plot to.
#' @param plot_width Plot width in pixels. 
#' @param plot_height Plot height in pixels. 
#' @param plot_phi View azimuth.
#' @param plot_theta View rotation.
#' @param plot_zoom View zoom.
#'
#' @return A ggpot grob of the rendered snapshot image. 
#' @export
#'
#' @examples
#' 
#' # Load r logo RGB raster
#' r_logo <- brick(system.file("external/rlogo.grd", package="raster"))
#' # Crop to square
#' r_logo <- crop(r_logo, extent(r_logo, 1, 77, 1, 77))
#' 
#' # Plot in 3D as flat object (ususally creates rendering artefacts)
#' plot_raster_3d_rgb(r_logo)
#' 
#' # Plot on top of volcano height model stretched by a factor of 3
#' volcano_raster <- raster(nrow = 60, ncol = 60, extent(0, 600, 0, 600), crs = NA, vals = volcano[1:60,1:60])
#' plot_raster_3d_rgb(r_logo, volcano_raster, z_scale = res(volcano_raster)[1]/3) 

plot_raster_3d_rgb <- function(raster_stack,
                               dtm_raster = NULL,
                               output_file = NULL,
                               z_scale = NULL,
                               plot_width = 1000,
                               plot_height = 800,
                               plot_phi = 45,
                               plot_theta = 45,
                               plot_zoom = 0.75) {
  
  # Check whether raster stack was supplied 
  if(class(raster_stack) != "RasterStack" & class(raster_stack) != "RasterBrick") stop("Please supply a RasterStack or RasterBrick!")
  
  # Check whether dtm was supplied if not generate a 0 height raster
  if(is.null(dtm_raster)) {
    warning("No dtm_raster supplied, using null raster!")
    dtm_raster <- setValues(raster_stack[[1]], 0)
  } 
  
  # Check number of layers
  if(nlayers(raster_stack) < 3) stop("Stack has less than 3 layers!\nPlease supply an RGB RasterStack or RasterBrick")
  if(nlayers(raster_stack) > 3) warning("Stack has more than 3 layers!\nAssuming layers 1, 2 and 3 are the R, G, and B bands respectively.")
  
  # Set z_scale parameter if needed
  if(is.null(z_scale)) {
    warning("No z_scale parameter specified!\nUsing x resolution of the dtm_raster.")
    z_scale <- res(dtm_raster)[1]
  }
  
  # Add ortho plot
  r_layer <- rayshader::raster_to_matrix(raster_stack[[1]])
  g_layer <- rayshader::raster_to_matrix(raster_stack[[2]])
  b_layer <- rayshader::raster_to_matrix(raster_stack[[3]])
  
  # Prepare three dimensional array
  rgb_array <- array(0,dim=c(nrow(r_layer),ncol(r_layer),3))
  
  # Assign layers
  rgb_array[,,1] <- r_layer/255 
  rgb_array[,,2] <- g_layer/255 
  rgb_array[,,3] <- b_layer/255 
  
  # Shuffel layer order(required for plot_3d)
  rgb_array <- aperm(rgb_array, c(2,1,3))
  
  # Prepare DTM baselayer
  dtm_raster_mat <- raster_to_matrix(dtm_raster)
  
  # Set temp file if needed
  if(is.null(output_file)){
    temp <- T
    output_file <- tempfile(fileext = ".png")
  } else {
    temp <- F
  }
  
  # Write out plot
  rgl::rgl.clear()
  rgb_array %>%
    plot_3d(dtm_raster_mat,
            windowsize = c(plot_width, plot_height),
            zscale = z_scale,
            theta = plot_theta,
            phi = plot_phi,
            zoom = plot_zoom)
  render_snapshot(output_file)
  rgl::rgl.close()
  
  # Load plot as ggplot grob
  raster_rgb_plot <- ggdraw() + draw_image(image_read(output_file))
  
  # Remove temp file if needed
  if(temp) file.remove(output_file)
  
  # Return plot grob
  return(raster_rgb_plot)
}

#' Add scale and north arrow to 3D raster plots
#'
#' Covenience function to annotate a 3D raster plot with a scale descripition for 
#' one side of the raster tile and a North arrow for the other. 
#' 
#' Default values for label and North arrow positon are approximations for 
#' plots of square rasters. Fine tuning required to position the labels correctly. 
#'
#' @param plot_grob The 3D raster plot grob, e.g. generated with plot_raster_3d() or plot_raster_3d_rgb().
#' @param text_size The size of the text.
#' @param text_face The font face of the text.
#' @param text_fontfamily  The font family of the text.
#' @param scale_label_text The label for the scale of the raster edge (e.g. "1 km").
#' @param scale_label_x The x position of the scale label relative to the whole grob. 0 to 1.
#' @param scale_label_y The y position of the scale label relative to the whole grob. 0 to 1.
#' @param scale_label_angle The rotation angle of the scale label. 
#' @param arrow_position_x The x position of the North arrow relative to the whole grob. 0 to 1.
#' @param arrow_poistion_y The y position of the North arrow relative to the whole grob. 0 to 1.
#' @param arrow_angle The rotation of the arrow angle. 
#' @param arrow_size_multiplier The arrow size stretch factor.
#' @param north_postion_x The x positon of the North arrow relative to the whole grob. 0 to 1.
#' @param north_postion_y The y positon of the North arrow relative to the whole grob. 0 to 1.
#' @param north_angle The rotation angle of the North arrow relative to the whole grob. 0 to 1. 
#'
#' @return An annotated ggplot grob.
#' @export
#'
#' @examples
#' 
#' # Square crop of volcano dtm
#' volcano_raster <- raster(nrow = 60, ncol = 60, extent(0, 600, 0, 600), crs = NA, vals = volcano[1:60,1:60])
#'
#' # Generate 3D plot
#' raster_plot_3d <- plot_raster_3d(volcano_raster, volcano_raster)
#' 
#' # Calculate side length
#' side_length <- ncol(volcano_raster) * res(volcano_raster)
#' 
#' # Add scale label and North arrow to plot
#' 
#' add_scale_north(raster_plot_3d, scale_label_text = paste0(side_length, " m"))

add_scale_north <- function(plot_grob,
                            text_size = 20,
                            text_face = "bold",
                            text_fontfamily = "",
                            scale_label_text = "1 km",
                            scale_label_x = 0.225,
                            scale_label_y = 0.25,
                            scale_label_angle = -38,
                            arrow_position_x = 0.755,
                            arrow_poistion_y = 0.27,
                            arrow_angle = +41,
                            arrow_size_multiplier = 2,
                            north_postion_x = 0.8,
                            north_postion_y = 0.2,
                            north_angle = -46
){
  
  plot_grob +
    draw_label(scale_label_text, 
               x = scale_label_x,
               y = scale_label_y,
               size = text_size, 
               angle = scale_label_angle,
               fontface = text_face, 
               fontfamily = text_fontfamily) +
    draw_label("→", 
               x = arrow_position_x,
               y = arrow_poistion_y, 
               size = text_size * arrow_size_multiplier, 
               angle = arrow_angle, 
               fontface = text_face,
               fontfamily = text_fontfamily) +
    draw_label("N", 
               x = north_postion_x, 
               y = north_postion_y, 
               size = text_size,
               angle = north_angle,
               fontface = text_face,
               fontfamily = text_fontfamily)
}

# Code do render figures for documentation
# volcano_raster <- raster(nrow = 60, ncol = 60, extent(0, 600, 0, 600), crs = NA, vals = volcano[1:60,1:60])
# save_plot("images/plot_raster_3d/combined_plot.png",
#      plot_raster_3d_combined(volcano_raster, volcano_raster, variable_name = "Height asl (m)"),
#      base_height = 4,
#      base_aspect_ratio = 2)
# 
# # RGB plot
# r_logo <- brick(system.file("external/rlogo.grd", package="raster"))
# r_logo <- crop(r_logo, extent(r_logo, 1, 77, 1, 77))
# volcano_raster <- raster(nrow = 60, ncol = 60, extent(0, 600, 0, 600), crs = NA, vals = volcano[1:60,1:60])
# save_plot("images/plot_raster_3d/rgb_plot.png",
#           plot_raster_3d_rgb(r_logo, volcano_raster, z_scale = res(volcano_raster)[1]/2),
#           base_height = 4,
#           base_aspect_ratio = 1)
# 
# # Scale arrows
# raster_plot_3d <- plot_raster_3d(volcano_raster, volcano_raster)
# side_length <- ncol(volcano_raster) * res(volcano_raster)
# save_plot("images/plot_raster_3d/scale_arrow.png",
#           add_scale_north(raster_plot_3d, scale_label_text = paste0(side_length, " m")),
#           base_height = 4,
#           base_aspect_ratio = 1)
