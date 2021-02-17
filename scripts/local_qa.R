# Local quality control script for DK Nationwide LiDAR outputs
# Jakob Assmann j.assmann@bio.au.dk

# Dependencies
library(raster)
library(cowplot)
library(tidyverse)
library(ggcorrplot)
library(sf)

list_of_vrts <- read.csv("D:/Jakob/dk_nationwide_lidar/data/outputs/list_of_vrts.txt",
                         header = F,
                         stringsAsFactors = F)
# Load stack of VRT files
big_stack <- raster::stack(as.list(list_of_vrts))

# Conpare extent
lapply(list_of_vrts$V1, function(x) {
  print(x)
  extent(raster(paste0("D:/Jakob/dk_nationwide_lidar/data/outputs/", x)))
  }
  )

# for the large sample the extends to not match, make dtm and lidar stacks
dtm_stack <- raster::stack(as.list(list_of_vrts$V1[c(1:7,71,72)]))
lidar_stack <- raster::stack(as.list(list_of_vrts$V1[-c(1:7,71,72)]))

# Removed following vrts from list of vrt file
#inland_water_mask.vrt
#sea_mask.vrt
#point_source_counts.vrt
#point_source_ids.vrt
#point_source_proportion.vrt

# Sample raster
sample_locations <- sampleRandom(dtm_stack, 100)

sample_df <- cbind(data.frame(sampleRandom(big_stack, 10000)))
sample_corr <- cor(as.matrix(sample_df))
corr_plot <- ggcorrplot(sample_corr, ggtheme = theme_cowplot(20))
save_plot("D:/Jakob/dk_nationwide_lidar/qa_local/corr_plot.png", corr_plot,
          base_height = 20)

# Find maximum canopy height in sample
row_max_height <- sample_df[which(sample_df$canopy_height == 3847),]
veg_profile_count <- row_max_height %>% select(contains("vegetation") & contains("count")) %>% 
  pivot_longer(cols = everything(), names_to = "variable", values_to = "value")
ggplot(veg_profile_count, aes(x = variable, y = value))+ geom_col() +theme_cowplot(15) +
  theme(axis.text.x = element_text(angle = 90))
veg_profile_prop <- row_max_height %>% select(contains("vegetation") & contains("proportion")) %>% 
  pivot_longer(cols = everything(), names_to = "variable", values_to = "value")
ggplot(veg_profile_prop, aes(x = variable, y = value))+ geom_col() +theme_cowplot(15) +
  theme(axis.text.x = element_text(angle = 90))
veg_profile2 <- row_max_height %>% select(contains("count")) %>% 
  pivot_longer(cols = everything(), names_to = "variable", values_to = "value")

sample_df_long <- sample_df %>% 
         pivot_longer(cols = everything(), 
                      names_to = "variable", 
                      values_to = "value") %>%
         mutate(variable_fac = ordered(variable, 
                                       levels = unique(variable)))
       
list_hist_plots <- lapply(
  levels(sample_df_long$variable_fac), 
  function(x) {
    data <- sample_df_long %>% filter(variable == x)
    if(x == "amplitude_mean") data <- data %>% filter(value <= 1000)
    if(x == "amplitude_sd") data <- data %>% filter(value <= 1000)
    hist_plot <- ggplot(data, 
                       aes(x = value)) +
      ggtitle(x) +
      geom_histogram() +
      theme_cowplot(15) +
      theme(plot.title= element_text(size= 10))
    return(hist_plot)
  })
hist_grid <- plot_grid(plotlist = list_hist_plots, nrow = 8, ncol = 9)
save_plot("D:/Jakob/dk_nationwide_lidar/qa_local/hist_plot.png", hist_grid,
          base_height = 20)

# Known test points in Aarhus, Bornholm and Zealand.
test_points_df <- data.frame(
  region = c(rep("Aarhus", 3), rep("Zealand",3), rep("Bornholm", 3)),
  class = rep(c("forest","city", "field"), 3),
  x = c(576684,
        574660,
        567624,
        704533,
        704104,
        701802,
        878338,
        863757,
        866273),  
  y = c(6218621,
        6224141,
        6235996,
        6211657,
        6203399,
        6220799,
        6122788,
        6120852,
        6129505))
test_points_sf <- st_as_sf(
  test_points_df,
  coords = c("x", "y"),
  crs = crs(dtm_stack))

st_write(test_points_sf, "D:/Jakob/dk_nationwide_lidar/qa_local/test_points.shp",
         delete_layer = T)
# Extract variables
dtm_values <- raster:::extract(dtm_stack, test_points_sf, df = T)[-1]
colnames(dtm_values) <- names(dtm_stack)
lidar_values <- raster:::extract(lidar_stack, test_points_sf, df = T)[-1]
colnames(lidar_values) <- gsub("_\\.", "_-", 
                               gsub("m\\.", "m-", names(lidar_values)))
test_points_df <- bind_cols(
  test_points_df,
  dtm_values,
  lidar_values)

# Apply converison factors
conv_fac <- read.csv("D:/Jakob/dk_nationwide_lidar/data/auxillary_files/conversion_factors.csv",
                     stringsAsFactors = F)
test_points_df_converted <- test_points_df %>% 
  colnames %>%
  map_dfc(function(col_name){
    if(col_name %in% conv_fac$ï..var_name){
      conv_factor <- filter(conv_fac, ï..var_name == !!col_name) %>% 
        pull(conv_fac) %>%
        pluck(1)
      column_df <- test_points_df %>% 
        select(col_name) 
      print(paste0("Factor ", conv_factor, " applied to ", col_name))
      return(column_df * conv_factor)
    } else  {
      print(paste0("No conversion applied to ", col_name))
       return(test_points_df %>% select(!!col_name))
      }
    }) 
test_points_df == test_points_df_converted

# Check whether proportions were correctly calculated
counts <- colnames(test_points_df)[grep("vegetation_point_count", colnames(test_points_df))]
props_df <- test_points_df[,counts]
props_df <- props_df[,-1] / props_df[,1]
props_df <- props_df %>% 
  map_dfc(function(x){
  x[is.nan(x)] <- 0
  return(x)
  }) %>%
  round(4) %>% as.data.frame()
names(props_df) <- gsub("point_count", "proportion", names(props_df))

props_orig_df <- test_points_df_converted %>% select(contains("vegetation_proportion"))
apply(apply(apply(props_df[,-11], 2, as.character), 2, as.numeric) == 
  apply(apply(as.data.frame(test_points_df_converted %>% select(contains("vegetation_proportion"))),
        2, as.character), 2, as.numeric), 2, sum)
# They were though floating point conversion is a pain as always.

# Let's graph it:
test_points_df_converted_long <- pivot_longer(test_points_df_converted,
                                              cols = 5:76, 
                                              names_to = "variable",
                                              values_to = "value")
ggplot(test_points_df_converted_long[grep("vegetation_proportion",
                                                  test_points_df_converted_long$variable),],
       aes(x = variable, 
           y = value,
           fill = class, group = class)) + 
  geom_col(position = "dodge") +
  scale_fill_manual(values = c("red", "blue", "darkgreen")) +
  theme(axis.text.x = element_text(angle = 90)) +
  facet_wrap(~region) +
  coord_flip() +
  theme_cowplot(10)

test_points_df_converted_long_sub <- 
  test_points_df_converted_long[-grep("vegetation_proportion",
                                     test_points_df_converted_long$variable),]
test_points_df_converted_long_sub <- 
  test_points_df_converted_long_sub[-grep("point_count",
                                          test_points_df_converted_long_sub$variable),]
test_points_df_converted_long_sub <- 
  test_points_df_converted_long_sub[-grep("point_source_counts",
                                          test_points_df_converted_long_sub$variable),]
test_points_df_converted_long_sub <- 
  test_points_df_converted_long_sub[-grep("point_source_ids",
                                          test_points_df_converted_long_sub$variable),]
test_points_df_converted_long_sub <- 
  test_points_df_converted_long_sub[-grep("point_source_proportion",
                                          test_points_df_converted_long_sub$variable),]
unique(test_points_df_converted_long_sub$variable)
ggplot(test_points_df_converted_long_sub %>% 
         filter(variable %in% 
                  unique(test_points_df_converted_long_sub$variable)[c(15,16,17)]),
       aes(x = variable, 
           y = value,
           fill = class, group = class)) + 
  geom_col(position = "dodge") +
  scale_fill_manual(values = c("red", "blue", "darkgreen")) +
  theme(axis.text.x = element_text(angle = 90)) +
  facet_wrap(~region) +
  coord_flip() +
  theme_cowplot(10)
ggplot(test_points_df_converted_long_sub %>% 
         filter(variable %in% 
                  unique(test_points_df_converted_long_sub$variable)[c(15,16,17)]),
       aes(x = variable, 
           y = value,
           fill = class, group = class)) + 
  geom_col(position = "dodge") +
  scale_fill_manual(values = c("red", "blue", "darkgreen")) +
  theme(axis.text.x = element_text(angle = 90)) +
  facet_wrap(~region) +
  coord_flip() +
  theme_cowplot(10)

test_points_df_converted_long_sub %>% group_by(region, class, variable) %>%
  summarise(mean(value))
write.csv(test_points_df_converted_long_sub, 
          "D:/Jakob//dk_nationwide_lidar/qa_local/test_points.csv")


# Gnereate 4k points in each of the three areas
#             x       y
# Aarhus Min: 550006  6210039 
# Aarhus Max: 579969  6239996
# Zealand Min: 680075  6180163
# Zealand Max: 727700  6225883
# Bornholm Min: 862523  6109819
# Bornholm Max: 894749  6142680

xmin <- c(550006, 680075, 862523)
xmax <- c(579969, 727700, 894749)
ymin <- c(6210039, 6180163, 6109819)
ymax <- c(6239996, 6225883, 6142680)

sampling_locations <- data.frame(
  point_id = c(paste0(rep("Aaarhus_", 4000), seq(1,4000,1)),
               paste0(rep("Zeqland_", 4000), seq(1,4000,1)),
               paste0(rep("Bornholm_", 4000), seq(1,4000,1))),
  x = c(runif(4000, xmin[1], xmax[1]),
        runif(4000, xmin[2], xmax[2]),
        runif(4000, xmin[3], xmax[3])),
  y = c(runif(4000, ymin[1], ymax[1]),
        runif(4000, ymin[2], ymax[2]),
        runif(4000, ymin[3], ymax[3]))) %>%
  st_as_sf(coords = c("x", "y"),
           crs = crs(dtm_stack))

# Extract data
dtm_sample<- raster:::extract(dtm_stack, sampling_locations, df = T)[-1]
colnames(dtm_sample) <- names(dtm_stack)
lidar_sample <- raster:::extract(lidar_stack, sampling_locations, df = T)[-1]
colnames(lidar_sample) <- gsub("_\\.", "_-", 
                               gsub("m\\.", "m-", names(lidar_sample)))
sample_df <- bind_cols(
  data.frame(point_id = as.data.frame(sampling_locations)[,-2]),
  dtm_sample,
  lidar_sample)
sample_df <- sample_df[sample_df$`ground_point_count_-01m-01m` != 0,]


# Check min and  max
min_vals <- apply(as.matrix(na.omit(sample_df[,c(-1, -9, -10, -70, -71, -73)])),
                  2, function(x) min(x))
max_vals <- apply(as.matrix(na.omit(sample_df[,c(-1, -9, -10, -70, -71, -73)])),
                  2, function(x) max(x))
min_max_df <- data.frame(variable = names(min_vals),
                         min = min_vals,
                         max = max_vals)

# Apply confersion factors
conv_fac <- read.csv("D:/Jakob/dk_nationwide_lidar/data/auxillary_files/conversion_factors.csv",
                     stringsAsFactors = F)
sample_df_converted <- sample_df %>% 
  colnames %>%
  map_dfc(function(col_name){
    if(col_name %in% conv_fac$ï..var_name){
      conv_factor <- filter(conv_fac, ï..var_name == !!col_name) %>% 
        pull(conv_fac) %>%
        pluck(1)
      column_df <- sample_df %>% 
        select(col_name) 
      print(paste0("Factor ", conv_factor, " applied to ", col_name))
      return(column_df * conv_factor)
    } else  {
      print(paste0("No conversion applied to ", col_name))
      return(sample_df %>% select(!!col_name))
    }
  }) 

# Convert into long form and calculate min and max
sample_df_converted_long <- sample_df_converted %>% 
  pivot_longer(cols = 2:73, 
               names_to = "variable", 
               values_to = "value") %>%
  mutate(variable_fac = ordered(variable, 
                                levels = unique(variable)))
sample_df_min_max <- sample_df_converted_long %>%
  group_by(variable) %>%
  summarise(min = min(value, na.rm = T),
            max = max(value, na.rm = T))
# Historgram plot
list_hist_plots <- lapply(
  levels(sample_df_converted_long$variable_fac), 
  function(x) {
    data <- sample_df_converted_long %>% filter(variable == x)
    if(x == "amplitude_mean") data <- data %>% filter(value <= 1000)
    if(x == "amplitude_sd") data <- data %>% filter(value <= 1000)
    hist_plot <- ggplot(data, 
                        aes(x = value)) +
      ggtitle(paste0(x,
                     " \nmin: ",
                     filter(sample_df_min_max, variable == x) %>%
                       pull(min) %>% pluck(1) %>% round(3),
                     " max: ",
                     filter(sample_df_min_max, variable == x) %>%
                       pull(max) %>% pluck(1) %>% round(3))
              ) +
      geom_histogram() +
      theme_cowplot(15) +
      theme(plot.title= element_text(size= 10))
    return(hist_plot)
  })
hist_grid <- plot_grid(plotlist = list_hist_plots, nrow = 8, ncol = 9)
save_plot("D:/Jakob/dk_nationwide_lidar/qa_local/hist_plot.png", hist_grid,
          base_height = 20)

# Correlation plot

sample_corr <- cor(as.matrix(na.omit(sample_df[,c(-1, -9, -10, -70, -71,-73)])))
corr_plot <- ggcorrplot(sample_corr, ggtheme = theme_cowplot(20))
save_plot("D:/Jakob/dk_nationwide_lidar/qa_local/corr_plot.png", corr_plot,
          base_height = 20)


