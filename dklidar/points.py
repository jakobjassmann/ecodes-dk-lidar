### Functions for point cloud handling for the DK Lidar project
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

## Imports
import re
import os
import opals
import subprocess
import numpy
import glob
import shutil

from dklidar import common
from dklidar import settings

##### Function definitions

## Import a single tile into ODM
def odm_import_single_tile(tile_id):
    """
        Imports a single tile (specified by tile_id) into an ODM for subsequent processing
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns execution status.
    """
    # Initiate return value
    return_value = ''

    # Generate relevant file names:
    laz_file = settings.laz_folder + '/PUNKTSKY_1km_' + tile_id + '.laz'
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'

    # Try import
    try:
        # Import tile id
        import_tile = opals.Import.Import()
        import_tile.inFile = laz_file
        import_tile.outFile = odm_file
        import_tile.commons.screenLogLevel = opals.Types.LogLevel.none
        import_tile.run()
        return_value = 'complete'
    except:
        return_value = 'opalsError'

    # return execution status
    return return_value


## Load neighbourhood of tiles into ODM (this is currently not neede by any of the funcitons below)
def odm_import_mosaic(tile_id):
    """
        Imports a tile (specified by tile_id) and it's 3 x 3 neighbourhood into a mosaiced ODM file for subsequent
        processing.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns execution status.
    """
    # Initiate return value, open log file
    return_value = ''
    log_file = open('log.txt', 'a+')

    # Retrieve row and col numbers for the current tile_id
    center_row = int(re.sub('(\d+)_\d+', '\g<1>', tile_id))
    center_col = int(re.sub('\d+_(\d+)', '\g<1>', tile_id))

    # Determine row and column numbers for tiles in the 3 x 3 window
    rows_to_load = [center_row - 1, center_row, center_row + 1]
    cols_to_load = [center_col - 1, center_col, center_col + 1]

    # Generate list of tile_ids for tiles to load
    tiles_to_load = []
    for row in rows_to_load:
        for col in cols_to_load:
            tile_to_load = str(row) + '_' + str(col)
            tiles_to_load.extend([tile_to_load])

    # Prep filenames and check if files exists:
    tile_file_names = []
    for tile_to_load in tiles_to_load:
        tile_file_name = settings.laz_folder + '/PUNKTSKY_1km_' + tile_to_load + '.laz'
        if os.path.exists(tile_file_name):
            tile_file_names.append(tile_file_name)
    n_neighbours = len(tile_file_names)

    # Update log output depending of the number of valid neighbours
    if n_neighbours == 9:
        log_file.write(' importing point clouds into ODM mosaic...\n' +
                       'Number of neighbours = ' + str(n_neighbours) + '. Complete!\n')
    else:
        log_file.write(tile_id + ' importing point clouds into ODM mosaic...\n' +
                       'Warning! Number of neighbours = ' + str(n_neighbours) +
                       '. Incomplete. Edge effects possible!\n')

    # Generate output file name string
    odm_file = settings.odm_mosaics_folder + '/odm_mosaic_' + tile_id + '.odm'

    # Execute command as subprocess and return message:
    try:
        # Import tiles into odm.
        import_tile = opals.Import.Import()
        import_tile.inFile = tile_file_names
        import_tile.outFile = odm_file
        import_tile.commons.screenLogLevel = opals.Types.LogLevel.none
        import_tile.run()
        log_file.write(tile_id + ' success.\n\n')
        return_value = return_value + 'complete'
        if n_neighbours != 9: return_value = 'Warning: Incomplete Neighbourhood!'
    except:
        return_value = 'opalsError'
        log_file.write(tile_id + ' failed. OpalsError.\n\n')

    # Write log output to log file
    log_file.close()

    # return status output
    return return_value


## Def: Export tile footprint
def odm_generate_footprint(tile_id):
    """
    Exports footprint from an odm file based on the tile_id in the DK nationwide dataset
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns execution status.
    """

    # Initiate return value
    return_value = ''
    log_file = open('log.txt', 'a+')

    # Generate relevant file names:
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    temp_tif_file = os.getcwd() + '/temp_' + tile_id + '.tif'
    footprint_file = settings.odm_footprint_folder + '/footprint_' + tile_id + '.shp'

    # Try token raster export to temp tif
    try:
        # Export temporary tif
        export_tif = opals.Cell.Cell()
        export_tif.inFile = odm_file
        export_tif.outFile = temp_tif_file
        export_tif.feature = 'min'
        export_tif.cellSize = 10 # This is also the default cell size, so technically not needed.
        export_tif.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_tif.commons.screenLogLevel = opals.Types.LogLevel.none
        export_tif.run()
        log_file.write('\n' + tile_id + ' temporary raster export successful.\n\n')
    except:
        return_value = 'opalsError'
        log_file.write('\n' + tile_id + ' temporary raster export failed.\n\n')

    # Try generating footprint from temp tif
    try:
        # Specify gdal command
        cmd = settings.gdaltlindex_bin + ' ' + footprint_file + ' ' + temp_tif_file
        # Execute gdal command
        log_file.write('\n' + tile_id + ' footprint generation... \n' + \
            subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT) + \
                     tile_id + ' successful.\n\n')
        # set exit status
        return_value = 'complete'
    except:
        log_file.write('\n' + tile_id + ' footprint generation... \n' + tile_id + ' failed.\n\n')
        if return_value == 'opalsError': pass
        else: return_value = 'gdalError'

    # Close log file
    log_file.close()

    # Remove temp raster file
    try:
        os.remove(temp_tif_file)
    except:
        pass

    # return status output
    return return_value


## Def: Validiate CRS
def odm_validate_crs(tile_id):
    """
    Function to validate the crs for odm files (single tile and mosaic)
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # Initiate return value
    return_value = ''

    # Generate odm files path names
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    odm_mosaic = settings.odm_mosaics_folder + '/odm_mosaic_' + tile_id + '.odm'

    # Retrieve CRS string for single tile
    try:
        odm_dm = opals.pyDM.Datamanager.load(odm_file)
        crs_str = odm_dm.getCRS()
        # Check whether CRS exists, if not assign, if different throw error.
        if crs_str == settings.crs:
            return_value = 'Single: match; '
        elif crs_str == '':
            odm_dm.setCRS(settings.crs)
            return_value = 'Single: empty - set; '
        else:
            return_value = 'Single: warning - no match; '
        odm_dm = None  # This is needed as opals locks the file connection otherwise.
    except:
        return_value = 'Single: error; '

    # Retrieve CRS string for mosaic
    try:
        odm_dm = opals.pyDM.Datamanager.load(odm_mosaic)
        crs_str = odm_dm.getCRS()
        # Check whether CRS exists, if not assign, if different throw error.
        if crs_str == settings.crs:
            return_value = return_value + 'Mosaic: match;'
        elif crs_str == '':
            odm_dm.setCRS(settings.crs)
            return_value = return_value + 'Mosaic: empty - set;'
        else:
            return_value = return_value + 'Mosaic: warning - no match;'
        odm_dm = None  # This is needed as opals locks the file connection otherwise.
    except:
        return_value = return_value + 'Mosaic: error;'

    return return_value


## Add height above ground (normalized z) to a tile odm
def odm_add_normalized_z(tile_id, mosaic = False):
    """
    Adds a "normalizedZ' variable to each point in and ODM file by normalising the height using the 0.4 m DTM.
    Can deal with either single tile odms or neighbourhood mosaics (option mosaic).
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :param mosaic: boolean (true or false) specifies whether a single tile pointcloud or a neighbourhood mosaic
    should be normalised.
    :return: execution status
    """
    # Initiate return value
    return_value = ''

    # Generate file paths
    if(mosaic == False):
        odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
        dtm_file = settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif'
    else:
        odm_file = settings.odm_mosaics_folder + '/odm_mosaic_' + tile_id + '.odm'
        dtm_file = settings.dtm_folder + '/dtm_' + tile_id + '_mosaic.tif'

    # Normalise the point cloud data
    try:
        add_normalized_z = opals.AddInfo.AddInfo()
        add_normalized_z.inFile = odm_file
        add_normalized_z.gridFile = dtm_file
        add_normalized_z.attribute = 'normalizedZ = z - r[0]'
        add_normalized_z.commons.screenLogLevel = opals.Types.LogLevel.none
        add_normalized_z.commons.nbThreads = settings.nbThreads
        add_normalized_z.run()

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Return exist status
    return return_value


## Export mean and sd of height above ground for all 10 m cells in a tile
def odm_export_normalized_z(tile_id):
    """
    Exports mean and standard deviation of the normalisedZ variable for the 10 m x 10 m raster grid.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''
    log_file = open('log.txt', 'a+')

    # Set file and folder paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    temp_file_mean = os.getcwd() + '/temp_' + tile_id + '_mean.tif'
    temp_file_sd = os.getcwd() + '/temp_' + tile_id + '_sd.tif'
    out_folder = settings.output_folder + '/normalized_z'
    out_file_mean = out_folder + '/normalized_z_mean/normalized_z_mean_' + tile_id + '.tif'
    out_file_sd = out_folder + '/normalized_z_sd/normalized_z_sd_' + tile_id + '.tif'

    # Create folders if they do not already exists
    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/normalized_z_mean'): os.mkdir(out_folder + '/normalized_z_mean')
    if not os.path.exists(out_folder + '/normalized_z_sd'): os.mkdir(out_folder + '/normalized_z_sd')

    # Export normalized z raster mean and sd
    try:
        # Initialise exporter
        export_normalized_z = opals.Cell.Cell()

        # Export mean
        export_normalized_z.inFile = odm_file
        export_normalized_z.outFile = temp_file_mean
        export_normalized_z.attribute = 'normalizedZ'
        export_normalized_z.feature = 'mean'
        export_normalized_z.cellSize = settings.out_cell_size
        export_normalized_z.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_normalized_z.filter = settings.all_classes
        export_normalized_z.commons.screenLogLevel = opals.Types.LogLevel.none
        export_normalized_z.commons.nbThreads = settings.nbThreads
        export_normalized_z.run()

        # Reset  exporter
        export_normalized_z.reset()

        # Export sd
        export_normalized_z = opals.Cell.Cell()
        export_normalized_z.inFile = odm_file
        export_normalized_z.outFile = temp_file_sd
        export_normalized_z.attribute = 'normalizedZ'
        export_normalized_z.feature = 'stdDev'
        export_normalized_z.cellSize = settings.out_cell_size
        export_normalized_z.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_normalized_z.filter = settings.all_classes
        export_normalized_z.commons.screenLogLevel = opals.Types.LogLevel.none
        export_normalized_z.commons.nbThreads = settings.nbThreads
        export_normalized_z.run()
        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Stretch and convert to 16 bit integer
    try:
        # Construct gdal command for mean
        cmd = settings.gdal_calc_bin + \
              '-A ' + temp_file_mean + ' ' + \
              '--outfile=' + out_file_mean + ' ' + \
              '--calc=rint(A*100) ' + \
              '--type=Int16 --NoDataValue=-9999 '

        # Execute and log command
        log_file.write('\n' + tile_id + ' rounding mean to int16 and calculation success. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))

        # Apply mask(s)
        common.apply_mask(out_file_mean)

        # Construct gdal command for sd
        cmd = settings.gdal_calc_bin + \
              '-A ' + temp_file_sd + ' ' + \
              '--outfile=' + out_file_sd + ' ' + \
              '--calc=rint(A*100) ' + \
              '--type=Int16 --NoDataValue=-9999 '

        # Execute and log command
        log_file.write('\n' + tile_id + ' rounding sd to int16 and calculation success. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))

        # Apply masks
        common.apply_mask(out_file_sd)

        return_value = 'success'
    except:
        if return_value == 'opalsError':
            pass
        else:
            return_value = 'gdalError'
            log_file.write('\n' + tile_id + ' normalized_z export failed. \n')

        # Tidy up
    try:
        os.remove(temp_file_mean)
        os.remove(temp_file_sd)
    except:
        pass

    # Close log file
    log_file.close()

    # Return exist status
    return return_value


## Export canopy height for all 10 m cells in a tile
def odm_export_canopy_height(tile_id):
    """
    Exports the canopy height (95 percentile of normalised height only for points classified as vegetation)
    for the 10 m x 10 m raster grid.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''
    log_file = open('log.txt', 'a+')

    # Generate file paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    temp_file1 = os.getcwd() + '/' + tile_id + '_temp1.tif'
    temp_file2 = os.getcwd() + '/' + tile_id + '_temp2.tif'
    out_folder = settings.output_folder + '/canopy_height'
    out_file = out_folder + '/canopy_height_' + tile_id + '.tif'

    # Create folder if it does not exist
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    # Export canopy height
    try:
        # Initialise exporter
        export_canopy_height = opals.Cell.Cell()

        # Export mean
        export_canopy_height.inFile = odm_file
        export_canopy_height.outFile = temp_file1
        export_canopy_height.attribute = 'normalizedZ'
        export_canopy_height.feature = 'quantile:0.95'
        # Apply extraction only to points classified as vegetation:
        export_canopy_height.filter = settings.veg_classes_filter
        # Set no data value to zero. Later the no data value will be set to -9999 this will assure that there are no
        # holes in the dataset for pixels where there are no points classified as vegetation.
        export_canopy_height.noData = 0
        export_canopy_height.cellSize = settings.out_cell_size
        export_canopy_height.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_canopy_height.commons.screenLogLevel = opals.Types.LogLevel.none
        export_canopy_height.commons.nbThreads = settings.nbThreads
        export_canopy_height.run()

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Stretch by 100, round to Int16 and set Nodata value to -9999
    try:
        # Construct gdal command to set no data value (this is done first to keep no data point counts as 0)
        cmd = settings.gdal_translate_bin + ' -a_nodata -9999 ' + temp_file1 + ' ' + temp_file2

        # Execute gdal commant and add to log output
        log_file.write('\n' + tile_id + ' setting no data value... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     tile_id + ' successful.\n\n')


        # Construct gdal command to stredtch and round to int 16
        cmd = settings.gdal_calc_bin + \
              '-A ' + temp_file2 + ' ' + \
              '--outfile=' + out_file + ' ' + \
              '--calc=rint(A*100) ' + \
              '--type=Int16 ' + \
              '--NoDataValue=-9999'

        # Execute command and log
        log_file.write('\n' + tile_id + ' stretching and rounding success. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))

        # Apply mask(s)
        common.apply_mask(out_file)

        # set exit status
        return_value = 'success'
    except:
        log_file.write(tile_id + ' setting no data value for canopy height failed.\n\n')
        if return_value == 'opalsError': pass
        else: return_value = 'gdalError'

    # Close log file
    log_file.close()

    # Remove temp raster file
    try:
        os.remove(temp_file1)
        os.remove(temp_file2)
    except:
        pass

    # Return exist status
    return return_value


## Export a point count for a specific height range and set of classes for all 10 m cells in a tile
def odm_export_point_count(tile_id, name = 'vegetation_point_count',
                           lower_limit = -1, upper_limit = 50.0,
                           point_classes = None):
    """
    Exports point count for a 10 m x 10 m cell in a given normalised height interval specified by
    the lower and upper limit parameters and for a given set of point classes specified by the pint_classes parameter.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :param name: identifier name for point count used in file and folder naming during export.
    :param lower_limit: lower limit for the height interval to count in (normalised height in m).
    :param upper_limit: upper limit for the height interval to count in (normalised height in m).
    :param point_classes: classes to subset from
    :return: execution status
    """
    # Initiate return value and log_output
    return_value = ''
    log_file = open('log.txt', 'a+')

    # Get temporary working directory
    wd = os.getcwd()

    # Initiate point_classes default value if no value is provided:
    if point_classes is None: point_classes = [3,4,5] # Veg class points

    # Generate paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    out_folder = settings.output_folder + '/point_count'

    if lower_limit < 10 and lower_limit >= 0: lower_limit_str = '0' + str(lower_limit)
    else: lower_limit_str = str(lower_limit)
    if upper_limit < 10 and upper_limit >= 0: upper_limit_str = '0' + str(upper_limit)
    else: upper_limit_str = str(upper_limit)

    prefix = name + '_' + lower_limit_str + 'm-' + upper_limit_str + 'm'
    temp_file = wd + '/temp_' + tile_id +  '.tif'
    out_file = out_folder + '/' + prefix + '/' + prefix + '_' + tile_id + '.tif'

    # Create folders if they don't exist
    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/' + prefix): os.mkdir(out_folder + '/' + prefix)

    # Export point count
    try:
        # Initialise exporter
        export_point_count = opals.Cell.Cell()

        # Specificy filter strings:
        height_filter = 'generic[NormalizedZ >= ' + str(lower_limit) + ' and NormalizedZ < ' + str(upper_limit) + ']'
        class_filter = 'Generic[Classification == ' + \
                       ' OR Classification == '.join([str(point_class) for point_class in point_classes]) + ']'

        # Export point count
        export_point_count.inFile = odm_file
        export_point_count.outFile = temp_file
        export_point_count.filter =  height_filter + ' AND ' + class_filter
        export_point_count.feature = 'pcount'
        export_point_count.cellSize = settings.out_cell_size
        export_point_count.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_point_count.noData = 0
        export_point_count.commons.screenLogLevel = opals.Types.LogLevel.none
        export_point_count.commons.nbThreads = settings.nbThreads
        export_point_count.run()

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Convert to 16 bit integer and set no data value to -9999
    try:
        # Construct gdal command
        cmd = settings.gdal_translate_bin + \
              '-ot Int16 -a_nodata -9999 ' + \
              temp_file + ' ' + \
              out_file
        # Execute and log command
        log_file.write('\n' + tile_id + ' converting to Int16 success. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))

        # Apply mask(s)
        common.apply_mask(out_file)

        return_value = 'success'
    except:
        if return_value == 'opalsError':
            pass
        else:
            log_file.write('\n' + tile_id + ' converting to Int16 for ' + prefix + ' failed. \n')
            return_value = 'gdalError'

    # Tidy up
    try:
        os.remove(temp_file)
    except:
        pass

    # Close log file
    log_file.close()

    # Return exist status
    return return_value


## Export point counts for a pre-defined set of height ranges and classes
def odm_export_point_counts(tile_id):
    """
    Exports point counts for multiple classes and pre defined height intervals by calling the
    odm_export_point_count function.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate empty list for return values
    return_values = []

    ## Ground point count
    return_values.append(odm_export_point_count(tile_id, 'ground_point_count', -1, 1, [2]))

    ## Water point count
    return_values.append(odm_export_point_count(tile_id, 'water_point_count', -1, 1, [9]))

    ## Ground and water point count
    return_values.append(odm_export_point_count(tile_id, 'ground_and_water_point_count', -1, 1, [2,9]))

    ## Vegetation point count
    return_values.append(odm_export_point_count(tile_id, 'vegetation_point_count', 0, 50, [3,4,5]))

    ## Building point counts
    return_values.append(odm_export_point_count(tile_id, 'building_point_count', -1, 50, [6]))

    ## All classes
    return_values.append(odm_export_point_count(tile_id, 'total_point_count', -1, 50, [2,3,4,5,6,9]))

    ## Vegetation point counts for continous height bins

    # 0-2 m at 0.5 m intervals
    for lower in numpy.arange(0, 2.0, 0.5):
        return_values.append(odm_export_point_count(tile_id, 'vegetation_point_count', lower, lower + 0.5, [3,4,5]))

    # 2-20 m at 1 m intervals
    for lower in range(2, 19, 1):
        return_values.append(odm_export_point_count(tile_id, 'vegetation_point_count', lower, lower + 1, [3,4,5]))

    # 20-25 m at 5 m interval
    return_values.append(odm_export_point_count(tile_id, 'vegetation_point_count', 20, 25, [3,4,5]))

    # 25 m to 50 m
    return_values.append(odm_export_point_count(tile_id, 'vegetation_point_count', 25, 50, [3,4,5]))

    # Set return value status
    # There are only two return value states so if there is more than one return value in the list
    # one of them has to be an opalsError
    return_values = set(return_values)

    if len(return_values) > 1:
        return_value = "opalsError"
    else:
        return_value = list(return_values)[0]

    return return_value


## Calculate proportions based on two point counts
def odm_calc_proportions(tile_id, prop_name, point_count_id1, point_count_id2):
    """
    Function to calculate point count proportions for two point counts.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :param prop_name: name to be assinged to the proportions output
    :param point_count_id1: name of point count to be rationed (numerator)
    :param point_count_id2: name of point count to be rationed to (denominator)
    :return: execution status
    """
    return_value = ''
    log_file = open('log.txt', 'a+')

    # Generate paths for numerator and denominator
    num_file = settings.output_folder + '/point_count/' + point_count_id1 + '/' + point_count_id1 + '_' + tile_id + '.tif'
    den_file = settings.output_folder + '/point_count/' + point_count_id2 + '/' + point_count_id2 + '_' + tile_id + '.tif'

    out_folder = settings.output_folder + '/proportions'
    out_file = out_folder + '/' + prop_name + '/' + prop_name + '_' + tile_id + '.tif'

    # Create folders if they do not exist
    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/' + prop_name): os.mkdir(out_folder + '/' + prop_name)

    # get wd
    temp_wd = os.getcwd()

    # specify temp file path
    temp_file = temp_wd + '/temp.tif'

    # Attempt calculating the proportions using gdal_calc
    try:
        # Construct gdal command nb. needed to use true_divide here. A cast into int16 will have to follow separately
        cmd = settings.gdal_calc_bin + \
              '-A ' + num_file + ' ' +\
              '-B ' + den_file + ' ' +\
              '--outfile=' + temp_file + ' ' + \
              '--type=Float32 ' +\
              '--calc=rint(10000*true_divide(A,B)) ' + \
              '--NoDataValue=-9999'
        log_file.write(cmd)
        # Execute gdal command
        log_file.write('\n' + tile_id + ' calculated proportions ' + prop_name + '... \n' + \
            subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT))

        # Round and convert to int16
        cmd = settings.gdal_translate_bin + \
              '-ot Int16 ' + \
              '-a_nodata -9999 ' +\
              temp_file + ' ' +\
              out_file + ' '
        log_file.write(cmd)
        # Execute gdal command
        log_file.write('\n' + tile_id + ' calculated proportions ' + prop_name + '... \n' + \
            subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT))

        os.remove(temp_file)
        # Apply mask(s)
        common.apply_mask(out_file)

        return_value = 'success'
    except:
        log_file.write('\n' + tile_id + ' calculation of proportions ' + prop_name + ' failed. gdalError \n')
        return_value = 'gdalError'

    # Close log file
    log_file.close()

    return return_value


## Export a pre-defined list of proportions for a tile
def odm_export_proportions(tile_id):
    """
    Exports proportions for: canopy openness, canopy height profile, buildings point counts
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: exit status
    """
    # Initiate return values
    return_values = []

    ## Export canopy openness
    return_values.append(odm_calc_proportions(tile_id, 'canopy_openness', 'ground_and_water_point_count_-1m-1m',
                                              'total_point_count_-1m-50m'))

    ## Export vegeation density
    return_values.append(odm_calc_proportions(tile_id, 'vegetation_density', 'vegetation_point_count_0m-50m',
                                              'total_point_count_-1m-50m'))

    ## Export canopy height profile
    # 0-2 m at 0.5 m intervals
    for lower in numpy.arange(0, 2, 0.5):
        veg_height_bin = 'vegetation_point_count_0' + str(lower) + 'm-0' + str(lower + 0.5) + 'm'
        prop_variable_bin = 'vegetation_proportion_0' + str(lower) + 'm-0' + str(lower + 0.5) + 'm'
        return_values.append(odm_calc_proportions(tile_id, prop_variable_bin, veg_height_bin,
                                                  'vegetation_point_count_0m-50m'))

    # 2-9 m at 1 m intervals
    for lower in range(2, 8, 1):
        veg_height_bin = 'vegetation_point_count_' + str(lower) + 'm-' + str(lower + 1) + 'm'
        prop_variable_bin = 'vegetation_proportion_' + str(lower) + 'm-' + str(lower + 1) + 'm'
        return_values.append(odm_calc_proportions(tile_id, prop_variable_bin, veg_height_bin,
                                                   'vegetation_point_count_0m-50m'))

    # 9-10 m
    return_values.append(odm_calc_proportions(tile_id, 'vegetation_proportion_09m-10m',
                                              'vegetation_point_count_09m-10m',
                                              'vegetation_point_count_0m-50m'))

    # 10-20 m at 1 m intervals
    for lower in range(10, 19, 1):
        veg_height_bin = 'vegetation_point_count_' + str(lower) + 'm-' + str(lower + 1) + 'm'
        prop_variable_bin = 'vegetation_proportion_' + str(lower) + 'm-' + str(lower + 1) + 'm'
        return_values.append(odm_calc_proportions(tile_id, prop_variable_bin, veg_height_bin,
                                                  'vegetation_point_count_0m-50m'))

    # 20-25 m
    return_values.append(odm_calc_proportions(tile_id, 'vegetation_proportion_20m-25m',
                                              'vegetation_point_count_20m-25m',
                                              'vegetation_point_count_0m-50m'))

    # 25-50 m
    return_values.append(odm_calc_proportions(tile_id, 'vegetation_proportion_25m-50m',
                                              'vegetation_point_count_25m-50m',
                                              'vegetation_point_count_0m-50m'))

    # Export building proportion
    return_values.append(odm_calc_proportions(tile_id, 'building_proportion',
                                              'building_point_count_-1m-50m',
                                              'total_point_count_-1m-50m'))

    # Set return value status
    # There are only two return value states so if there is more than one return value in the list
    # one of them has to be an opalsError
    return_values = set(return_values)

    if len(return_values) > 1:
        return_value = "gdalError"
    else:
        return_value = list(return_values)[0]

    return return_value


## Export mean and sd in the amplitude variable for all 10 m cells in a tile
def odm_export_amplitude(tile_id):
    """
    Exports mean and variance(sd) for the lidar amplitude for all 10 m x 10 m cells in a tile.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''

    # Generate file paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    out_folder = settings.output_folder + '/amplitude'
    out_file_mean = out_folder + '/amplitude_mean/amplitude_mean_' + tile_id + '.tif'
    out_file_sd = out_folder + '/amplitude_sd/amplitude_sd_' + tile_id + '.tif'

    # Create folders if they do not exist
    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/amplitude_mean'): os.mkdir(out_folder + '/amplitude_mean')
    if not os.path.exists(out_folder + '/amplitude_sd'): os.mkdir(out_folder + '/amplitude_sd')

    # Export amplitude mean and sd using OPALS Cell
    try:
        # Initialise exporter
        export_amplitude = opals.Cell.Cell()

        # Export mean
        export_amplitude.inFile = odm_file
        export_amplitude.outFile = out_file_mean
        export_amplitude.attribute = 'amplitude'
        export_amplitude.feature = 'mean'
        export_amplitude.cellSize = settings.out_cell_size
        export_amplitude.filter = settings.all_classes # all classes (2,3,4,5,6,9)
        export_amplitude.limit = 'corner'  # This switch is really important when working with tiles!
        # It sets the ROI to the extent to the bounding box of points in the ODM
        export_amplitude.commons.screenLogLevel = opals.Types.LogLevel.none
        export_amplitude.commons.nbThreads = settings.nbThreads
        export_amplitude.run()

        # Reset  exporter
        export_amplitude.reset()

        # Export sd
        export_amplitude = opals.Cell.Cell()
        export_amplitude.inFile = odm_file
        export_amplitude.outFile = out_file_sd
        export_amplitude.attribute = 'amplitude'
        export_amplitude.feature = 'stdDev'
        export_amplitude.cellSize = settings.out_cell_size
        export_amplitude.filter = settings.all_classes   # all classes (2,3,4,5,6,9)
        export_amplitude.limit = 'corner'  # This switch is really important when working with tiles!
        # It sets the ROI to the extent to the bounding box of points in the ODM
        export_amplitude.commons.screenLogLevel = opals.Types.LogLevel.none
        export_amplitude.commons.nbThreads = settings.nbThreads
        export_amplitude.run()

        # Apply mask(s)
        common.apply_mask(out_file_mean)
        common.apply_mask(out_file_sd)

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Return exist status
    return return_value


## Export flight strip information for all 10 m cells in a tile
def odm_export_point_source_info(tile_id):
    """
    Extracts point source statistics for the 10 m x 10 m cells of the point cloud.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # Initate return value
    return_value = ''

    # Initiate log output
    log_file = open('log.txt', 'a+')

    # get current work dir string
    temp_wd = os.getcwd()

    # Set file paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    out_folder = settings.output_folder + '/point_source_info'
    out_folder_ids = out_folder + '/point_source_ids'
    out_folder_nids = out_folder + '/point_source_nids'
    out_folder_counts = out_folder + '/point_source_counts'
    out_folder_prop = out_folder + '/point_source_proportion'

    # Create folders if they do not exist
    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder_ids): os.mkdir(out_folder_ids)
    if not os.path.exists(out_folder_nids): os.mkdir(out_folder_nids)
    if not os.path.exists(out_folder_counts): os.mkdir(out_folder_counts)
    if not os.path.exists(out_folder_prop): os.mkdir(out_folder_prop)

    ## Look up unique point source ids found in odm file
    try:
        # Open odm in python DM
        dm = opals.pyDM.Datamanager.load(odm_file)

        # Create layout and add 'PointSourceID' column
        lf = opals.pyDM.AddInfoLayoutFactory()
        lf.addColumn(dm, 'PointSourceId', True)
        layout = lf.getLayout()

        # Get set of histograms for layout
        # (this will only have one item, the histogram for the point source id column)
        histograms_set = dm.getHistogramSet(layout)

        # Initate empty list of point source ids
        point_source_ids = []

        # Load unique point source ids from histogram
        # Note: The histogram set does not allow subsetting, so we loop through it.
        # As it will only have one object, this does not matter
        for histo in histograms_set.histograms():
            for value, count in histo.values():
                point_source_ids.append(value)

        # Remove dm object and close connection to odm file for later use
        del dm

        ## Use opals cell to extract point counts for each point source id
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
            export_point_count.noData = 0
            export_point_count.commons.screenLogLevel = opals.Types.LogLevel.none
            export_point_count.commons.nbThreads = settings.nbThreads
            export_point_count.run()

            export_point_count.reset()

        ## Convert to int16 and set no data to -9999 and apply mask
        for point_source_id in point_source_ids:
            cmd = settings.gdal_translate_bin + '-ot Int16 -a_nodata -9999 ' + \
                  temp_wd + '/temp_count_' + str(point_source_id) + '.tif ' + \
                  out_folder_counts + '/point_source_counts_' + tile_id + '_' + str(point_source_id) + '.tif '
            log_file.write('\n' + tile_id + ' ' + str(point_source_id) + ' converted point source file to int16. \n' + \
                           subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))
            common.apply_mask(out_folder_counts +
                              '/point_source_counts_' + tile_id + '_' + str(point_source_id) + '.tif ')

        ## Determine the number of uniuqe point source ids per cell using gdal_calc.
        # Prepare in file string and equation string
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F',
                    'G', 'H', 'I', 'J', 'K', 'L',
                    'M', 'N', 'O', 'P', 'Q', 'R',
                    'S', 'T', 'U', 'V', 'W', 'X',
                    'Y', 'Z']
        files_string = ''
        equation = []
        for i in range(len(point_source_ids)):
            files_string = files_string + ' -' + alphabet[i] + ' ' + out_folder_counts + \
                           '/point_source_counts_' + tile_id + '_' + str(point_source_ids[i]) + '.tif '
            equation.append(alphabet[i])
        equation = '1*greater(' + ',0)+1*greater('.join(equation) + ',0)'

        # Construct gdal command
        cmd = settings.gdal_calc_bin + files_string + \
              '--outfile=' + out_folder_nids + '/point_source_nids_' + tile_id + '.tif' + \
              ' --calc=' + equation + \
              ' --type=Int16 --NoDataValue=-9999'
        # Execute gdal command
        log_file.write('\n' + tile_id + ' extracted number of unique point source ids. \n' + \
                       subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))
        # Apply mask(s)
        common.apply_mask('--outfile=' + out_folder_nids + '/point_source_nids_' + tile_id + '.tif')

        ## Calculate proportion of hits pre cell per point source using gdal_calc

        # Calculate total sum of points per cell, prepare gdal command
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z']
        files_string = ''
        equation = []
        for i in range(len(point_source_ids)):
            files_string = files_string + ' -' + alphabet[i] + ' ' + out_folder_counts + \
                           '/point_source_counts_' + tile_id + '_' + str(point_source_ids[i]) + '.tif '
            equation.append(alphabet[i])
        equation = '+'.join(equation)
        # Construct gdal command
        cmd = settings.gdal_calc_bin + files_string + '--outfile=' + temp_wd + '/temp_total_points.tif ' + \
              '--calc=' + equation + ' --NoDataValue=-9999'
        # Execute gdal command
        print cmd
        log_file.write('\n' + tile_id + ' created temporary total point count file. \n' + \
                       subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))

        ## Calculate proportions using gdal_calc, round, stretch by 10000
        for point_source_id in point_source_ids:
            # Construct gdal command
            cmd = settings.gdal_calc_bin + \
                  '-A ' + out_folder_counts + '/point_source_counts_' + tile_id + '_' + str(point_source_id) + '.tif ' + \
                  '-B ' + temp_wd + '/temp_total_points.tif ' + \
                  '--outfile=' + temp_wd + '/point_source_prop_' + str(point_source_id) + '.tif ' + \
                  '--calc=rint(true_divide(A,B)*10000) ' + '--type=Float32 --NoDataValue=-9999'
            # Execute gdal command
            log_file.write('\n' + tile_id + ' calculated proportions for ' + str(point_source_id) + '. \n' + \
                           subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))

        ## Convert proportions to int16
        for point_source_id in point_source_ids:
            cmd = settings.gdal_translate_bin + '-a_nodata -9999 -ot Int16 ' + \
                  temp_wd + '/point_source_prop_' + str(point_source_id) + '.tif ' + \
                  out_folder_prop + '/point_source_prop_' + tile_id + '_' + str(point_source_id) + '.tif '

            log_file.write('\n' + tile_id + ' ' + str(point_source_id) + ' converted proportion to int16. \n' + \
                           subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))
            # Apply mask(s)
            common.apply_mask(out_folder_prop + '/point_source_prop_' + tile_id + '_' + str(point_source_id) + '.tif')

        ## Create a layer with presence / absence of point source id indicated by the point source id itself
        for point_source_id in point_source_ids:
            # Construct gdal command
            cmd = settings.gdal_calc_bin + \
                  '-A ' + out_folder_counts + '/point_source_counts_' + tile_id + '_' + str(point_source_id) + '.tif ' + \
                  '--outfile=' + temp_wd + '/temp_presence_' + str(point_source_id) + '.tif ' + \
                  '--calc=' + str(point_source_id) + '*greater(A,0)' + \
                  ' --type=Int32 --NoDataValue=-9999'
            # Execute gdal command
            log_file.write('\n' + tile_id + ' created temporary presence layer for ' + \
                           str(point_source_id) + '. \n' + \
                           subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))

        ## Merge files into one using gdal_merge
        # Prepare gdal command
        in_files_string = '.tif ' + temp_wd + '/temp_presence_'
        in_files_string = temp_wd + '/temp_presence_' + in_files_string.join(
            [str(i) for i in point_source_ids]) + '.tif'
        # Construct gdal command
        cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + \
              '-o ' + out_folder_ids + '/point_source_ids_' + tile_id + '.tif ' + \
              in_files_string
        # Execute gdal command
        log_file.write('\n' + tile_id + ' merged temporary layers in point source ids file. \n' + \
                       subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT))
        # Apply mask(s)
        common.apply_mask(out_folder_ids + '/point_source_ids_' + tile_id + '.tif')

        # The 'majority' stat produced by opals is not reliable... I'm leaving the below code for leagcy reasons.
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
        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Close log file
    log_file.close()

    # remove temporary files
    for temp_file in glob.glob(temp_wd + '/*.tif'):
        try:
            os.remove(temp_file)
        except:
            pass
    return return_value


def odm_remove_temp_files(tile_id):
    """
    Removes footprint and odm files to clear up space for subsequent processing.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # initiate return value
    return_value = ''

    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    odm_footprint_files = glob.glob(settings.odm_footprint_folder + '/footprint_' + tile_id + '.*')

    try:
        os.remove(odm_file)
        return_value('success')
    except:
        return_value = 'unable to delete odm file'

    try:
        for file in odm_footprint_files: os.remove(file)
        return_value('success')
    except:
        return_value = return_value + 'unable to delete odm footprint file'

    # return execution status
    return return_value

