import opals
import os
from dklidar import settings
import glob
import subprocess
opals.loadAllModules()
tile_id = '6210_570'

# Initate return value
return_value = ''

# Initiate log output
log_output = ''

# Set file path
odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'

# Set output paths
out_folder = settings.output_folder + '/point_source_info'
out_folder_ids = out_folder + '/point_source_ids'
out_folder_nids = out_folder + '/point_source_nids'
out_folder_counts = out_folder + '/point_source_counts'
out_folder_prop = out_folder + '/point_source_proportion'

if not os.path.exists(out_folder): os.mkdir(out_folder)
if not os.path.exists(out_folder_ids): os.mkdir(out_folder_ids)
if not os.path.exists(out_folder_nids): os.mkdir(out_folder_nids)
if not os.path.exists(out_folder_counts): os.mkdir(out_folder_counts)
if not os.path.exists(out_folder_prop): os.mkdir(out_folder_prop)

# get current work dir string
temp_wd = os.getcwd()

## Look up unique point source ids found in odm file
try:
    # Open odm in python DM
    dm = opals.pyDM.Datamanager.load(odm_file)

    # Create layout and add 'PointSourceID' column
    lf = opals.pyDM.AddInfoLayoutFactory()
    lf.addColumn(dm, 'PointSourceId', True)
    layout = lf.getLayout()

    # Get set of histograms for layout (this will only have one item, the histogram for the point source id column)
    histograms_set = dm.getHistogramSet(layout)

    # Initate list of point source ids
    point_source_ids = []

    # Load unique point source ids from histogram
    # The histogram set does not allow subsetting, so we loop through it. As it will only have one object, this does not
    # matter
    for histo in histograms_set.histograms():
        for value, count in histo.values():
            point_source_ids.append(value)

    # Remove dm object and close connection to odm file for later use
    del dm

    # Next use opals cell to extact point counts for each point source id
    for point_source_id in point_source_ids:
        # Initate opals cell module
        export_point_count = opals.Cell.Cell()

        # Initate filter string
        point_classes = [2, 3, 4, 5, 6, 9]
        class_filter = 'Generic[Classification == ' + \
                       ' OR Classification == '.join([str(point_class) for point_class in point_classes]) + ']'

        # Export point count
        export_point_count.inFile = odm_file
        export_point_count.outFile = 'temp_count_' + str(point_source_id) + '.tif'
        export_point_count.filter = class_filter + \
                                    ' AND Generic[PointSourceId == ' + str(point_source_id) + ']'
        export_point_count.feature = 'pcount'
        export_point_count.cellSize = settings.out_cell_size
        export_point_count.limit = 'corner'  # This switch is really important when working with tiles!
        # It sets the ROI to the extent to the bounding box of points in the ODM
        export_point_count.commons.screenLogLevel = opals.Types.LogLevel.none
        export_point_count.commons.nbThreads = settings.nbThreads
        export_point_count.run()

        export_point_count.reset()

    ## Merge files into one:
    # Specify gdal command
    # construct infile string
    in_files_string = '.tif ' + temp_wd + '/temp_count_'
    in_files_string = temp_wd + '/temp_count_' + in_files_string.join([str(i) for i in point_source_ids]) + '.tif'
    # construct command string
    cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + out_folder_counts + \
          '/point_source_counts_' + tile_id + '.tif ' + in_files_string

    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' merging point source point count files... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    ## Determine the number of uniuqe point source ids per cell
    # Prep gdal command
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z']
    files_string = ''
    sum_string = []
    for i in range(len(point_source_ids)):
        files_string = files_string + ' -' + alphabet[i] + ' ' + temp_wd + '/temp_count_' + str(
            point_source_ids[i]) + '.tif '
        sum_string.append(alphabet[i])
    sum_string = '1*greater(' + ',0)+1*greater('.join(sum_string) + ',0)'

    # Specify gdal command
    cmd = settings.gdal_calc_bin + files_string + '--outfile=' + out_folder_nids + '/point_source_nids_' + tile_id + \
          '.tif' + ' --calc=' + sum_string + ' --NoDataValue=-9999'
    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' extracting number of uniuqe point source ids... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    ## Calculate proportion of hits pre cell per point source
    # Prep gdal command
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z']
    files_string = ''
    sum_string = []
    for i in range(len(point_source_ids)):
        files_string = files_string + ' -' + alphabet[i] + ' ' + temp_wd + '/temp_count_' + str(
            point_source_ids[i]) + '.tif '
        sum_string.append(alphabet[i])
    sum_string = '+'.join(sum_string)

    # Specify gdal command
    cmd = settings.gdal_calc_bin + files_string + '--outfile=' + temp_wd + '/temp_total_points.tif --calc=' + sum_string + \
          ' --NoDataValue=-9999'
    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' creating temporary total point count file... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    ## Calculate proportions
    for point_source_id in point_source_ids:
        # Specify gdal command
        cmd = settings.gdal_calc_bin + '-A ' + temp_wd + '/temp_count_' + str(
            point_source_id) + '.tif ' + '-B ' + temp_wd + '/temp_total_points.tif ' + \
              '--outfile=' + temp_wd + '/point_source_prop_' + str(
            point_source_id) + '.tif --calc=A/B ' + '--NoDataValue=-9999'
        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' calculating proportions for ' + point_source_id + '... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # Merge files into one:
    # Specify gdal command
    in_files_string = '.tif ' + temp_wd + '/point_source_prop_'
    in_files_string = temp_wd + '/point_source_prop_' + in_files_string.join(
        [str(i) for i in point_source_ids]) + '.tif'
    cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + out_folder_prop + '/point_source_prop_' + tile_id + '.tif ' + \
          in_files_string

    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' merging point source proportions... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    ## Create a layer with presence / absence of point source id indicated by the point source id itself
    for point_source_id in point_source_ids:
        # Specify gdal command
        cmd = settings.gdal_calc_bin + '-A ' + temp_wd + '/temp_count_' + str(point_source_id) + '.tif ' + \
              '--outfile=' + temp_wd + '/temp_presence_' + str(point_source_id) + '.tif --calc=' + str(
            point_source_id) + '*greater(A,0)' + \
              ' --NoDataValue=-9999'
        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' creating temporary presence layer for ' + point_source_id + '... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    ## Merge files into one:
    # Specify gdal command
    in_files_string = '.tif ' + temp_wd + '/temp_presence_'
    in_files_string = temp_wd + '/temp_presence_' + in_files_string.join(
        [str(i) for i in point_source_ids]) + '.tif'
    cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + out_folder_ids + '/point_source_ids_' + tile_id + '.tif ' + \
          in_files_string

    # Execute gdal command
    log_output = log_output + '\n' + tile_id + ' merging temporary layers in point source ids file... \n' + \
                 subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    # The 'majority' stat produced by opals is not reliable... leaving the below code for leagcy reasons.
    # 'majority statistics will have to be calculate from the above generated rasters by hand.
    # ## Extract mode of point count ids
    # # Initate opals cell module
    # export_point_mode = opals.Cell.Cell()
    #
    # # Export point count
    # export_point_mode.inFile = odm_file
    # export_point_mode.outFile = out_folder_mode + '/point_source_mode_' + tile_id + '.tif'
    # export_point_mode.filter = settings.ground_and_veg_classes_filter
    # export_point_mode.attribute = 'PointSourceId'
    # export_point_mode.feature = 'majority'
    # export_point_mode.cellSize = settings.out_cell_size
    # export_point_mode.limit = 'corner'  # This switch is really important when working with tiles!
    # # It sets the ROI to the extent to the bounding box of points in the ODM
    # export_point_mode.commons.screenLogLevel = opals.Types.LogLevel.none
    # export_point_mode.commons.nbThreads = settings.nbThreads
    # export_point_mode.run()

    print(os.getcwd())
    # Remove temp files
    temp_tifs = glob.glob('*.tif')
    for tif in temp_tifs: os.remove(tif)

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    return_value = 'success'
except:
    return_value = 'opalsError'