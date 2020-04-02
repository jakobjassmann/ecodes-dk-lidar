library(raster)
library(cowplot)
library(tidyverse)
library(ggcorrplot)
list_of_vrts <- read.csv("D:/Jakob/dk_nationwide_lidar/data/sample/outputs/list_of_vrts.csv", 
                         header = F,
                         stringsAsFactors = F)

big_stack <- raster::stack(as.list(list_of_vrts$V1))
lapply(list_of_vrts$V1, function(x) {
  print(x)
  extent(raster(x))
  }
  )

# Removed following vrts from list of vrt file
#inland_water_mask.vrt
#sea_mask.vrt
#point_source_counts.vrt
#point_source_ids.vrt
#point_source_proportion.vrt

# Sample raster
sample_df <- data.frame(sampleRandom(big_stack, 10000))
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
