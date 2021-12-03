# Local quality control script for DK Nationwide LiDAR outputs
# Jakob Assmann j.assmann@bio.au.dk

# Dependencies
library(terra)
library(raster)
library(cowplot)
library(tidyverse)
library(ggcorrplot)
library(sf)
library(parallel)
library(pbapply)

# set path to repository
path_to_repo <- "D:/Jakob/ecodes-dk-lidar-rev1/"
setwd(path_to_repo)

# Load list of vrts
list_of_vrts <- read.csv("data/outputs/list_of_vrts.txt",
                         header = F,
                         stringsAsFactors = F)$V1 %>%
  paste0("data/outputs/", .)

# load fotprints shapefile
tile_footprints <- shapefile("data/outputs/tile_footprints/tile_footprints.shp")

# Obtain a selection of random coordinates within the tiles
sample_locations <- spsample(tile_footprints, 50000, type= "random")
sample_locations_vect <- vect(sample_locations)
sample_locations_vect$sample_id <- 1:nrow(sample_locations_vect)

# extract sample across all vrts in parallel (except point_source_ids)
cl <- makeCluster(62)
clusterEvalQ(cl, library(terra))
sample_list <- pblapply(cl = cl, 
                      list_of_vrts[!grepl("point_source", list_of_vrts)], 
                    function(vrt_file, sample_locations){
                      vrt_rast <- rast(vrt_file)
                      sample_vect <- vect(sample_locations, crs = crs(vrt_rast))
                      cell_values <- extract(vrt_rast, sample_locations)
                      #if(!exists("cell_values")) cell_values <- vrt_file 
                      return(cell_values)
                    },
                    geom(sample_locations_vect)[,c("x","y")])
stopCluster(cl)

# Convert to sf and save sample 
sample_sf <- bind_cols(sample_list) %>%
  setNames(., gsub(".*/(.*).vrt$", "\\1", 
                   list_of_vrts[!grepl("point_source", list_of_vrts)])) %>%
  mutate(sample_id = sample_locations_vect$sample_id) %>%
  dplyr::select(last_col(), !last_col()) 
sample_sf$x <- sample_locations$x
sample_sf$y <- sample_locations$y
sample_sf <- st_as_sf(sample_sf, coords = c("x", "y"), 
                      crs = st_crs(tile_footprints))
save(sample_sf, file = "documentation/point_sample_sf.Rda")
# load("documentation/point_sample_sf.Rda")

# dublicate sf and convert to data frame
sample_df <- st_drop_geometry(sample_sf)

# apply conversion factors
conv_factors <- read_csv("documentation/conversion_factors.csv")
for(i in 2:(ncol(sample_df))){
  sample_df[,i] <- sample_df[,i] / 
    conv_factors$conv_fac[conv_factors$var_name == colnames(sample_df)[i]]
}

# Remove masked pixels (inland water / sea)
sample_df <- sample_df %>%
  filter(sea_mask == 1) %>%
  filter(inland_water_mask == 1)

# Convert into long form and calc min, max etc. for all non height bin variables
sample_df_long <- sample_df %>% 
  dplyr::select(!contains("vegetation"), 
         `vegetation_point_count_00m-50m`,
         vegetation_density) %>%
  dplyr::select(-inland_water_mask, -sea_mask) %>%
  pivot_longer(cols = 2:ncol(.), 
               names_to = "variable", 
               values_to = "value") %>%
  mutate(variable_fac = ordered(variable, 
                                levels = unique(variable)))
sample_df_min_max_mean <- sample_df_long %>%
  group_by(variable) %>%
  summarise(min = min(value, na.rm = T),
            max = max(value, na.rm = T),
            mean = mean(value, na.rm = T),
            q2 = quantile(value, 0.02, na.rm = T),
            q98 = quantile(value, 0.98, na.rm = T))

# Histogram plot for all non height bin variables
list_hist_plots <- lapply(
  levels(sample_df_long$variable_fac), 
  function(x) {
    # Subset data
    data <- sample_df_long %>% filter(variable == x)
    # If an amplitude variable is requested remove outlier values above 1k
    if(x == "amplitude_mean" | x == "amplitude_sd") {
      n_removed <- nrow(data %>% filter(value > 1000))
      data <- data %>% filter(value <= 1000)
      removed_msg <- paste0(" outliers (>1k): ", n_removed)
    } else if(x == "canopy_height" | x == "normalized_z_mean") {
      n_removed <- nrow(data %>% filter(value > 40 | value < -1))
      data <- data %>% filter(value <= 40 & value >= -1)
      removed_msg <- paste0(" outliers (>40m|<-1m): ", n_removed)
    } else {
      removed_msg <- ""
    }
    # Plot histogram
    hist_plot <- ggplot(data, 
                        aes(x = value)) +
      labs(title = x,
           x = "value",
           y = "count",
           subtitle = paste0(
             "mean: ",
             filter(sample_df_min_max_mean, variable == x) %>%
               pull(mean) %>% pluck(1) %>% round(2),
           "   min: ",
           filter(sample_df_min_max_mean, variable == x) %>%
             pull(min) %>% pluck(1) %>% round(2),
           "   max: ",
           filter(sample_df_min_max_mean, variable == x) %>%
             pull(max) %>% pluck(1) %>% round(2),
           " ", removed_msg)
      ) +
      geom_histogram(bins = 50) +
      theme_cowplot(15) 
    return(hist_plot)
  })

# Export individual histograms
if(!dir.exists("documentation/figures/hists")) dir.create("documentation/figures/hists")
lapply(list_hist_plots, function(hist_plot){
  save_plot(paste0("documentation/figures/hists/", 
                   hist_plot$labels$title, ".png"), hist_plot)})

# Export panel figure
hist_grid <- plot_grid(plotlist = list_hist_plots, nrow = 4, ncol = 6)
save_plot("documentation/figures/hist_plot.png", 
          hist_grid,
          nrow = 5, 
          ncol = 6)

# Violin plots for Vegetation height bins 
sample_df_long <- sample_df %>% 
  dplyr::select(sample_id,
         contains("vegetation"),
         -vegetation_density,
         -`vegetation_point_count_00m-50m`) %>%
  pivot_longer(cols = 2:ncol(.), 
               names_to = "variable", 
               values_to = "value") %>%
  mutate(variable_fac = ordered(variable, 
                                levels = unique(variable)))
sample_df_min_max_mean <- sample_df_long %>%
  group_by(variable) %>%
  summarise(min = min(value, na.rm = T),
            max = max(value, na.rm = T),
            mean = mean(value, na.rm = T),
            q2 = quantile(value, 0.02, na.rm = T),
            q98 = quantile(value, 0.98, na.rm = T))

# Point counts
point_count_violin <- sample_df_long %>% 
  filter(grepl("count", variable))  %>%
  ggplot(aes(x = variable_fac, y = value)) +
  geom_violin() +
  geom_text(data =sample_df_min_max_mean %>%filter(grepl("count", variable)),
            mapping = aes(x = variable, 
                          y = max(max) + 1/3 * max(max), 
                          label = paste0(
                            "mean: ", round(mean, 2),
                            " min: ", min,
                            " max: ", max)),
            hjust = 1) +
  scale_x_discrete(labels = gsub("vegetation_point_count_", "",
                                 as.character(sample_df_long %>% 
                                                filter(grepl("count", variable)) 
                                              %>% pull(variable_fac)))) +
  labs(x = "", title = "vegetation_point_count per height bin") +
  coord_flip() + 
  theme_cowplot(15)
point_prop_violin <- sample_df_long %>% 
  filter(grepl("prop", variable))  %>%
  ggplot(aes(x = variable_fac, y = value)) +
  geom_violin() +
  geom_text(data =sample_df_min_max_mean %>%filter(grepl("prop", variable)),
            mapping = aes(x = variable, 
                          y = max(max) + 1/3 * max(max), 
                          label = paste0(
                            "mean: ", round(mean, 2),
                            " min: ", min,
                            " max: ", max)),
            hjust = 1) +
  scale_x_discrete(labels = gsub("vegetation_proportion_", "",
                                 as.character(sample_df_long %>% 
                                                filter(grepl("prop", variable)) 
                                              %>% pull(variable_fac)))) +
  labs(x = "", title = "vegetation_proportion per height bin") +
  coord_flip() + 
  theme_cowplot(15)
save_plot("documentation/figures/hists/vegetation_point_count_violin.png",
          point_count_violin, base_height = 8)
save_plot("documentation/figures/hists/vegetation_point_prop_violin.png",
          point_prop_violin, base_height = 8)
save_plot("documentation/figures/veg_height_bin_violin.png",
          plot_grid(point_count_violin, point_prop_violin, nrow = 2),
          base_height = 8,
          nrow = 2)

# Correlation plot
sample_corr <- sample_df %>%
  dplyr::select(!contains("mask"), -sample_id) %>%
  na.omit() %>%
  as.matrix() %>%
  cor() 
corr_plot <- ggcorrplot(sample_corr, ggtheme = theme_cowplot(20))
save_plot("documentation/figures/corr_plot.png", corr_plot,
          base_height = 20)


# Visualise sample 
sample_sf <- bind_cols(sample_list) %>%
  setNames(., gsub(".*/(.*).vrt$", "\\1",
                   list_of_vrts[!grepl("point_source", list_of_vrts)])) %>%
  mutate(sample_id = sample_locations_vect$sample_id) %>%
  dplyr::select(last_col(), !last_col()) %>%
  mutate(sample_type = case_when(
    !is.na(sea_mask) ~ "Sea",
    !is.na(inland_water_mask) ~ "Inland water",
    TRUE ~ "Land"
  )) %>% 
  dplyr::select(sample_id, sample_type)
sample_sf$x <- sample_locations$x
sample_sf$y <- sample_locations$y
sample_sf <- st_as_sf(sample_sf, coords = c("x", "y"),
                      crs = st_crs(tile_footprints))
sample_plot <- ggplot() +
  geom_sf(data = st_as_sf(tile_footprints), 
          colour = NA, fill = "grey") +
  geom_sf(data = sample_sf, 
          mapping = aes(colour = sample_type),
          size = 0.05) +
  labs(colour = "Sample Type") +
  guides(colour = guide_legend(override.aes = list(size=5))) +
  theme(        
    panel.grid.minor = element_line(colour = "lightgrey"), 
    panel.grid.major = element_line(colour = "lightgrey"), 
    plot.margin=grid::unit(c(0,0,0,0), "mm"),
    panel.background = element_rect(fill = "white"), 
    panel.border = element_rect(colour = "lightgrey", fill=NA, size=0.5)
    )
save_plot("documentation/figures/sample_locations.png",
          sample_plot,
          base_height = 8)

# Solar radiation vs. heat load index
solar_rad_vs_heat_load <- ggplot(
  sample_df, 
  aes(x = solar_radiation,
      y = heat_load_index)) +
  geom_point() +
  annotate("text", 
           x = 1600000, 
           y = 0.9, 
           label = paste0("r = ", round(cor(sample_df$solar_radiation,
                                      sample_df$heat_load_index, 
                                      "complete.obs"), 2)),
           size = 6) +
  theme_cowplot()
save_plot("documentation/figures/solar_rad_vs_heat_index.png",
          solar_rad_vs_heat_load,
          base_height = 6,
          base_asp = 1.1)

## End of Script

## The below code is kept for legacy reasons.
# 
# # Find maximum canopy height in sample
# row_max_height <- sample_df[which(sample_df$canopy_height == max(sample_df$canopy_height)),]
# veg_profile_count <- row_max_height %>% select(contains("vegetation") & contains("count")) %>% 
#   pivot_longer(cols = everything(), names_to = "variable", values_to = "value")
# ggplot(veg_profile_count, aes(x = variable, y = value))+ geom_col() +theme_cowplot(15) +
#   theme(axis.text.x = element_text(angle = 90))
# veg_profile_prop <- row_max_height %>% select(contains("vegetation") & contains("proportion")) %>% 
#   pivot_longer(cols = everything(), names_to = "variable", values_to = "value")
# ggplot(veg_profile_prop, aes(x = variable, y = value))+ geom_col() +theme_cowplot(15) +
#   theme(axis.text.x = element_text(angle = 90))
# veg_profile2 <- row_max_height %>% select(contains("count")) %>% 
#   pivot_longer(cols = everything(), names_to = "variable", values_to = "value")
# 
# sample_df_long <- sample_df %>% 
#          pivot_longer(cols = everything(), 
#                       names_to = "variable", 
#                       values_to = "value") %>%
#          mutate(variable_fac = ordered(variable, 
#                                        levels = unique(variable)))
#        
# list_hist_plots <- lapply(
#   levels(sample_df_long$variable_fac), 
#   function(x) {
#     data <- sample_df_long %>% filter(variable == x)
#     if(x == "amplitude_mean") data <- data %>% filter(value <= 1000)
#     if(x == "amplitude_sd") data <- data %>% filter(value <= 1000)
#     hist_plot <- ggplot(data, 
#                        aes(x = value)) +
#       ggtitle(x) +
#       geom_histogram() +
#       theme_cowplot(15) +
#       theme(plot.title= element_text(size= 10))
#     return(hist_plot)
#   })
# hist_grid <- plot_grid(plotlist = list_hist_plots, nrow = 8, ncol = 9)
# save_plot("D:/Jakob/dk_nationwide_lidar/qa_local/hist_plot.png", hist_grid,
#           base_height = 20)
# 
# # Known test points in Aarhus, Bornholm and Zealand.
# test_points_df <- data.frame(
#   region = c(rep("Aarhus", 3), rep("Zealand",3), rep("Bornholm", 3)),
#   class = rep(c("forest","city", "field"), 3),
#   x = c(576684,
#         574660,
#         567624,
#         704533,
#         704104,
#         701802,
#         878338,
#         863757,
#         866273),  
#   y = c(6218621,
#         6224141,
#         6235996,
#         6211657,
#         6203399,
#         6220799,
#         6122788,
#         6120852,
#         6129505))
# test_points_sf <- st_as_sf(
#   test_points_df,
#   coords = c("x", "y"),
#   crs = crs(dtm_stack))
# 
# st_write(test_points_sf, "D:/Jakob/dk_nationwide_lidar/qa_local/test_points.shp",
#          delete_layer = T)
# # Extract variables
# dtm_values <- raster:::extract(dtm_stack, test_points_sf, df = T)[-1]
# colnames(dtm_values) <- names(dtm_stack)
# lidar_values <- raster:::extract(lidar_stack, test_points_sf, df = T)[-1]
# colnames(lidar_values) <- gsub("_\\.", "_-", 
#                                gsub("m\\.", "m-", names(lidar_values)))
# test_points_df <- bind_cols(
#   test_points_df,
#   dtm_values,
#   lidar_values)
# 
# # Apply converison factors
# conv_fac <- read.csv("D:/Jakob/dk_nationwide_lidar/data/auxillary_files/conversion_factors.csv",
#                      stringsAsFactors = F)
# test_points_df_converted <- test_points_df %>% 
#   colnames %>%
#   map_dfc(function(col_name){
#     if(col_name %in% conv_fac$ï..var_name){
#       conv_factor <- filter(conv_fac, ï..var_name == !!col_name) %>% 
#         pull(conv_fac) %>%
#         pluck(1)
#       column_df <- test_points_df %>% 
#         select(col_name) 
#       print(paste0("Factor ", conv_factor, " applied to ", col_name))
#       return(column_df * conv_factor)
#     } else  {
#       print(paste0("No conversion applied to ", col_name))
#        return(test_points_df %>% select(!!col_name))
#       }
#     }) 
# test_points_df == test_points_df_converted
# 
# # Check whether proportions were correctly calculated
# counts <- colnames(test_points_df)[grep("vegetation_point_count", colnames(test_points_df))]
# props_df <- test_points_df[,counts]
# props_df <- props_df[,-1] / props_df[,1]
# props_df <- props_df %>% 
#   map_dfc(function(x){
#   x[is.nan(x)] <- 0
#   return(x)
#   }) %>%
#   round(4) %>% as.data.frame()
# names(props_df) <- gsub("point_count", "proportion", names(props_df))
# 
# props_orig_df <- test_points_df_converted %>% select(contains("vegetation_proportion"))
# apply(apply(apply(props_df[,-11], 2, as.character), 2, as.numeric) == 
#   apply(apply(as.data.frame(test_points_df_converted %>% select(contains("vegetation_proportion"))),
#         2, as.character), 2, as.numeric), 2, sum)
# # They were though floating point conversion is a pain as always.
# 
# # Let's graph it:
# test_points_df_converted_long <- pivot_longer(test_points_df_converted,
#                                               cols = 5:76, 
#                                               names_to = "variable",
#                                               values_to = "value")
# ggplot(test_points_df_converted_long[grep("vegetation_proportion",
#                                                   test_points_df_converted_long$variable),],
#        aes(x = variable, 
#            y = value,
#            fill = class, group = class)) + 
#   geom_col(position = "dodge") +
#   scale_fill_manual(values = c("red", "blue", "darkgreen")) +
#   theme(axis.text.x = element_text(angle = 90)) +
#   facet_wrap(~region) +
#   coord_flip() +
#   theme_cowplot(10)
# 
# test_points_df_converted_long_sub <- 
#   test_points_df_converted_long[-grep("vegetation_proportion",
#                                      test_points_df_converted_long$variable),]
# test_points_df_converted_long_sub <- 
#   test_points_df_converted_long_sub[-grep("point_count",
#                                           test_points_df_converted_long_sub$variable),]
# test_points_df_converted_long_sub <- 
#   test_points_df_converted_long_sub[-grep("point_source_counts",
#                                           test_points_df_converted_long_sub$variable),]
# test_points_df_converted_long_sub <- 
#   test_points_df_converted_long_sub[-grep("point_source_ids",
#                                           test_points_df_converted_long_sub$variable),]
# test_points_df_converted_long_sub <- 
#   test_points_df_converted_long_sub[-grep("point_source_proportion",
#                                           test_points_df_converted_long_sub$variable),]
# unique(test_points_df_converted_long_sub$variable)
# ggplot(test_points_df_converted_long_sub %>% 
#          filter(variable %in% 
#                   unique(test_points_df_converted_long_sub$variable)[c(15,16,17)]),
#        aes(x = variable, 
#            y = value,
#            fill = class, group = class)) + 
#   geom_col(position = "dodge") +
#   scale_fill_manual(values = c("red", "blue", "darkgreen")) +
#   theme(axis.text.x = element_text(angle = 90)) +
#   facet_wrap(~region) +
#   coord_flip() +
#   theme_cowplot(10)
# ggplot(test_points_df_converted_long_sub %>% 
#          filter(variable %in% 
#                   unique(test_points_df_converted_long_sub$variable)[c(15,16,17)]),
#        aes(x = variable, 
#            y = value,
#            fill = class, group = class)) + 
#   geom_col(position = "dodge") +
#   scale_fill_manual(values = c("red", "blue", "darkgreen")) +
#   theme(axis.text.x = element_text(angle = 90)) +
#   facet_wrap(~region) +
#   coord_flip() +
#   theme_cowplot(10)
# 
# test_points_df_converted_long_sub %>% group_by(region, class, variable) %>%
#   summarise(mean(value))
# write.csv(test_points_df_converted_long_sub, 
#           "D:/Jakob//dk_nationwide_lidar/qa_local/test_points.csv")
# 
# 
# # Gnereate 4k points in each of the three areas
# #             x       y
# # Aarhus Min: 550006  6210039 
# # Aarhus Max: 579969  6239996
# # Zealand Min: 680075  6180163
# # Zealand Max: 727700  6225883
# # Bornholm Min: 862523  6109819
# # Bornholm Max: 894749  6142680
# 
# xmin <- c(550006, 680075, 862523)
# xmax <- c(579969, 727700, 894749)
# ymin <- c(6210039, 6180163, 6109819)
# ymax <- c(6239996, 6225883, 6142680)
# 
# sampling_locations <- data.frame(
#   point_id = c(paste0(rep("Aaarhus_", 4000), seq(1,4000,1)),
#                paste0(rep("Zeqland_", 4000), seq(1,4000,1)),
#                paste0(rep("Bornholm_", 4000), seq(1,4000,1))),
#   x = c(runif(4000, xmin[1], xmax[1]),
#         runif(4000, xmin[2], xmax[2]),
#         runif(4000, xmin[3], xmax[3])),
#   y = c(runif(4000, ymin[1], ymax[1]),
#         runif(4000, ymin[2], ymax[2]),
#         runif(4000, ymin[3], ymax[3]))) %>%
#   st_as_sf(coords = c("x", "y"),
#            crs = crs(dtm_stack))
# 
# # Extract data
# dtm_sample<- raster:::extract(dtm_stack, sampling_locations, df = T)[-1]
# colnames(dtm_sample) <- names(dtm_stack)
# lidar_sample <- raster:::extract(lidar_stack, sampling_locations, df = T)[-1]
# colnames(lidar_sample) <- gsub("_\\.", "_-", 
#                                gsub("m\\.", "m-", names(lidar_sample)))
# sample_df <- bind_cols(
#   data.frame(point_id = as.data.frame(sampling_locations)[,-2]),
#   dtm_sample,
#   lidar_sample)
# sample_df <- sample_df[sample_df$`ground_point_count_-01m-01m` != 0,]
# 
# 
# # Check min and  max
# min_vals <- apply(as.matrix(na.omit(sample_df[,c(-1, -9, -10, -70, -71, -73)])),
#                   2, function(x) min(x))
# max_vals <- apply(as.matrix(na.omit(sample_df[,c(-1, -9, -10, -70, -71, -73)])),
#                   2, function(x) max(x))
# min_max_df <- data.frame(variable = names(min_vals),
#                          min = min_vals,
#                          max = max_vals)
# 
# # Apply conversion factors
# conv_fac <- read.csv("D:/Jakob/dk_nationwide_lidar/data/auxillary_files/conversion_factors.csv",
#                      stringsAsFactors = F)
# sample_df_converted <- sample_df %>% 
#   colnames %>%
#   map_dfc(function(col_name){
#     if(col_name %in% conv_fac$ï..var_name){
#       conv_factor <- filter(conv_fac, ï..var_name == !!col_name) %>% 
#         pull(conv_fac) %>%
#         pluck(1)
#       column_df <- sample_df %>% 
#         select(col_name) 
#       print(paste0("Factor ", conv_factor, " applied to ", col_name))
#       return(column_df * conv_factor)
#     } else  {
#       print(paste0("No conversion applied to ", col_name))
#       return(sample_df %>% select(!!col_name))
#     }
#   }) 




