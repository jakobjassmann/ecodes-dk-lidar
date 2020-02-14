import opals
import os
from dklidar import settings
import glob
import subprocess

opals.loadAllModules()

dm = opals.pyDM.Datamanager.load('D:\Jakob\dk_nationwide_lidar\data\sample\odm\odm_6210_570.odm')

lf = opals.pyDM.AddInfoLayoutFactory()
lf.addColumn(dm, "PointSourceId", True)
layout = lf.getLayout()

histograms_set = dm.getHistogramSet(layout)
point_source_ids = []
for histo in histograms_set.histograms():
    print(histo)
    for value, cell in histo.values():
        point_source_ids.append(value)
del dm
print('-' * 80)

print point_source_ids
#
# for point_source_id in point_source_ids:
#     filter_string = 'Generic[PointSourceId == ' + str(point_source_id) + ']'
#     print point_source_id
#     print filter_string
#
#     temp_wd = os.getcwd()
#     temp_file = temp_wd + '/temp_count_' + str(point_source_id) + '.tif'
#     print temp_file
#
#     # Initate opals cell module
#     export_point_count = opals.Cell.Cell()
#
#     # Export point count
#     export_point_count.inFile = 'D:\Jakob\dk_nationwide_lidar\data\sample\odm\odm_6210_570.odm'
#     export_point_count.outFile = temp_file
#     export_point_count.filter = filter_string
#     #export_point_count.filter =  settings.ground_and_veg_classes_filter +\
#     #                             ' AND Generic[PointSourceId == ' + str(point_source_id) + ']'
#     export_point_count.feature = 'pcount'
#     export_point_count.cellSize = 10
#     export_point_count.limit = 'corner'  # This switch is really important when working with tiles!
#     # It sets the ROI to the extent to the bounding box of points in the ODM
#     #export_point_count.commons.screenLogLevel = opals.Types.LogLevel.none
#     export_point_count.commons.nbThreads = 1
#     export_point_count.run()
temp_wd = os.getcwd()
# in_files_string = '.tif ' +temp_wd + '/temp_count_'
# in_files_string = temp_wd + '/temp_count_' + in_files_string.join([str(i) for i in point_source_ids]) + '.tif'
# cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + temp_wd + '/point_count_' + 'test_tile' + '.tif ' + in_files_string
# print(cmd)
# # Execute gdal command
# subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

## Calculate proportion of hits pre cell per point source
# # Prep gdal command
# alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
#             'V', 'W', 'X', 'Y', 'Z']
# files_string = ''
# sum_string = []
# for i in range(len(point_source_ids)):
#     files_string = files_string + ' -' + alphabet[i] + ' ' + temp_wd + '/temp_count_' + str(point_source_ids[i]) + '.tif '
#     sum_string.append(alphabet[i])
# sum_string = '+'.join(sum_string)
#
# # Specify gdal command
# cmd = settings.gdal_calc_bin + files_string + '--outfile=' + temp_wd + '/temp_total_points.tif --calc=' + sum_string + \
#       ' --NoDataValue=-9999'
# # Execute gdal command
# subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
#
# # calculate proportions
# for point_source_id in point_source_ids:
#     # Specify gdal command
#     cmd = settings.gdal_calc_bin + '-A ' + temp_wd + '/temp_count_' + str(point_source_id) + '.tif ' + '-B ' + temp_wd + '/temp_total_points.tif ' + \
#           '--outfile=' + temp_wd + '/point_source_prop_' + str(point_source_id) + '.tif --calc=A/B ' + '--NoDataValue=-9999'
#     # Execute gdal command
#     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
#
# # Merge files into one:
# # Specify gdal command
# in_files_string = '.tif ' + temp_wd + '/point_source_prop_'
# in_files_string = temp_wd + '/point_source_prop_' + in_files_string.join([str(i) for i in point_source_ids]) + '.tif'
# cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + temp_wd + '/temp_prop_points_' + 'test_id' + '.tif ' + \
#       in_files_string
#
# # Execute gdal command
# subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
#
## Create a layer with presence / absence of point source id indicated by the point source id itself
out_folder_ids = temp_wd
tile_id = 'test_id'

# for point_source_id in point_source_ids:
#     # Specify gdal command
#     cmd = settings.gdal_calc_bin + '-A ' + temp_wd + '/temp_count_' + str(point_source_id) + '.tif ' + \
#     '--outfile=' + temp_wd + '/temp_presence_' + str(point_source_id) + '.tif --calc=' + str(point_source_id) + '*greater(A,0)' +\
#     ' --NoDataValue=-9999'
#     # Execute gdal command
#     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
#
# ## Merge files into one:
# # Specify gdal command
# in_files_string = '.tif ' + temp_wd + '/temp_presence_'
# in_files_string = temp_wd + '/temp_presence_' + in_files_string.join([str(i) for i in point_source_ids]) + '.tif'
# cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + out_folder_ids + '/point_sources_' + tile_id + '.tif ' + \
#       in_files_string
#
# # Execute gdal command
# subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

# ## Extract mode of point count ids
# # Initate opals cell module
# export_point_mode = opals.Cell.Cell()
#
# # Export point count
# export_point_mode.inFile = 'D:\Jakob\dk_nationwide_lidar\data\sample\odm\odm_6210_570.odm'
# export_point_mode.outFile =  temp_wd + '/point_source_mode_' + tile_id + '.tif'
# export_point_mode.filter = settings.ground_and_veg_classes_filter
# export_point_mode.attribute = 'PointSourceID'
# export_point_mode.feature = 'majority'
# export_point_mode.cellSize = settings.out_cell_size
# export_point_mode.limit = 'corner'  # This switch is really important when working with tiles!
# # It sets the ROI to the extent to the bounding box of points in the ODM
# export_point_mode.commons.screenLogLevel = opals.Types.LogLevel.none
# export_point_mode.commons.nbThreads = settings.nbThreads
# export_point_mode.run()

temp_tifs = glob.glob('*.tif')
for tif in temp_tifs: os.remove(tif)