### Functions for point cloud handling for the DK Lidar project
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

## Imports
import multiprocessing
import re
import os
import opals
import subprocess
import settings
import time
import numpy
import glob

##### Function definitions

## Functio to import a single tile into ODM
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
    return(return_value)


## Define function to load neighbourhood of tiles into ODM
def odm_import_mosaic(tile_id):
    """
        Imports a tile (specified by tile_id) and it's 3 x 3 neighbourhood into a shared ODM file for subsequent
        processing.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns execution status.
    """
    # Initiate return value
    return_value = ''

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
        log_output = tile_id + ' importing point clouds into ODM mosaic...\n' + 'Number of neighbours = ' + str(n_neighbours) + '. Complete!\n'
    else:
        log_output = tile_id + ' importing point clouds into ODM mosaic...\n' + 'Warning! Number of neighbours = ' + str(n_neighbours) + '. Incomplete. Edge effects possible!\n'


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
        log_output = log_output + tile_id + ' success.\n\n'
        return_value = return_value + 'complete'
        if n_neighbours != 9: return_value = 'Warning: Incomplete Neighbourhood!'
    except:
        return_value = 'opalsError'
        log_output = log_output + tile_id + ' failed. OpalsError.\n\n'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # return status output
    return(return_value)

## Def: Export tile footprint
def odm_generate_footprint(tile_id):
    """
    Exports footprint from a laz file based on the tile_id in the DK nationwide dataset
    :param laz_tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns execution status.
    """

    # Initiate return value
    return_value = ''

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
        log_output = '\n' + tile_id + ' temporary raster export successful.\n\n'
    except:
        return_value = 'opalsError'
        log_output = '\n' + tile_id + ' temporary raster export failed.\n\n'

    # Try generating footprint from temp tif
    try:
        # Specify gdal command
        cmd = settings.gdaltlindex_bin + ' ' + footprint_file + ' ' + temp_tif_file
        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' footprint generation... \n' + \
            subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT) + \
                     tile_id + ' successful.\n\n'
        # set exit status
        return_value = 'complete'
    except:
        log_output = log_output + '\n' + tile_id + ' footprint generation... \n' + tile_id + ' failed.\n\n'
        if return_value == 'opalsError': pass
        else: return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temp raster file
    os.remove(temp_tif_file)

    # return status output
    return(return_value)


## Def: Retrieve CRS
def odm_validate_crs(tile_id):
    """
    Function to validate the crs for odm files (single tile and odm)
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # Initiate return value
    return_value = ''

    # Generate odm files pathnames
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    odm_mosaic = settings.odm_mosaics_folder + '/odm_mosaic_' + tile_id + '.odm'

    # Retrieve CRS string for single tile
    try:
        odm_dm = opals.pyDM.Datamanager.load(odm_file)
        crs_str = odm_dm.getCRS()
        if crs_str == settings.crs:
            return_value = 'Single: match; '
        elif crs_str == '':
            odm_dm.setCRS(settings.crs)
            return_value = 'Single: empty - set; '
        else:
            return_value = 'Single: warning - no match; '
        odm_dm = None
    except:
        return_value = 'Single: error; '

    # Retrieve CRS string for mosaic
    try:
        odm_dm = opals.pyDM.Datamanager.load(odm_mosaic)
        crs_str = odm_dm.getCRS()
        if crs_str == settings.crs:
            return_value = return_value + 'Mosaic: match;'
        elif crs_str == '':
            odm_dm.setCRS(settings.crs)
            return_value = return_value + 'Mosaic: empty - set;'
        else:
            return_value = return_value + 'Mosaic: warning - no match;'
        odm_dm = None
    except:
        return_value = return_value + 'Mosaic: error;'

    return(return_value)


def odm_add_normalized_z(tile_id, mosaic = False):
    """
    Adds a adding a "normalizedZ' variable to each point in and ODM file by normalising the height using the DTM.
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
        dtm_file = settings.dtm_folder + '/dtm_mosaic_' + tile_id + '.tif'

    # Normalise the point cloud data
    try:
        add_normalized_z = opals.AddInfo.AddInfo()
        add_normalized_z.inFile = odm_file
        add_normalized_z.gridFile = dtm_file
        add_normalized_z.attribute = 'normalizedZ = z - r[0]'
        add_normalized_z.commons.screenLogLevel = opals.Types.LogLevel.none
        add_normalized_z.commons.nbThreads = settings.nbThreads # Might need to be used to reduce strain on machine
        add_normalized_z.run()

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Return exist status
    return(return_value)


def odm_export_normalized_z(tile_id):
    """
    Exports mean and standard deviation of the normalisedZ variable to the 10 m x 10 m raster grid.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''

    # Generate file paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    out_folder = settings.output_folder + '/normalized_z'
    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/mean'): os.mkdir(out_folder + '/mean')
    if not os.path.exists(out_folder + '/sd'): os.mkdir(out_folder + '/sd')

    out_file_mean = out_folder + '/mean/normalized_z_mean_' + tile_id + '.tif'
    out_file_sd = out_folder + '/sd/normalized_z_sd_' + tile_id + '.tif'

    # Export normalized z raster mean and sd
    try:
        # Initialise exporter
        export_normalized_z = opals.Cell.Cell()

        # Export mean
        export_normalized_z.inFile = odm_file
        export_normalized_z.outFile = out_file_mean
        export_normalized_z.attribute = 'normalizedZ'
        export_normalized_z.feature = 'mean'
        export_normalized_z.cellSize = settings.out_cell_size
        export_normalized_z.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_normalized_z.commons.screenLogLevel = opals.Types.LogLevel.none
        export_normalized_z.commons.nbThreads = settings.nbThreads
        export_normalized_z.run()

        # Reset  exporter
        export_normalized_z.reset()

        # Export sd
        export_normalized_z = opals.Cell.Cell()
        export_normalized_z.inFile = odm_file
        export_normalized_z.outFile = out_file_sd
        export_normalized_z.attribute = 'normalizedZ'
        export_normalized_z.feature = 'stdDev'
        export_normalized_z.cellSize = settings.out_cell_size
        export_normalized_z.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_normalized_z.commons.screenLogLevel = opals.Types.LogLevel.none
        export_normalized_z.commons.nbThreads = settings.nbThreads
        export_normalized_z.run()
        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Return exist status
    return (return_value)


def odm_export_canopy_height(tile_id):
    """
    Exports the canopy height (95 percentile of normalised height only for points classified as vegetation) to the 10 m x 10 m raster grid.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''
    log_output = ''

    # Generate file paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    temp_file = os.getcwd() + '/' + tile_id + '_temp.tif'
    out_folder = settings.output_folder + '/canopy_height'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    out_file = out_folder + '/canopy_height_' + tile_id + '.tif'

    # Export canopy height
    try:
        # Initialise exporter
        export_canopy_height = opals.Cell.Cell()

        # Export mean
        export_canopy_height.inFile = odm_file
        export_canopy_height.outFile = temp_file
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

    # Use gdal_translate to set Nodata value to -9999 (this will not affect any cell values only the file header)
    try:
        # Specify gdal command
        cmd = settings.gdal_translate_bin + ' -a_nodata -9999 ' + temp_file + ' ' + out_file
        log_output = log_output + '\n' + tile_id + ' setting no data value... \n' + \
            subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT) + \
                     tile_id + ' successful.\n\n'
        # set exit status
        return_value = 'success'
    except:
        log_output = log_output + tile_id + ' setting no data value... \n' + tile_id + ' failed.\n\n'
        if return_value == 'opalsError': pass
        else: return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temp raster file
    os.remove(temp_file)

    # Return exist status
    return (return_value)


def odm_export_veg_point_count(tile_id, lower_limit = 0.0, upper_limit = 50.0):
    """
    Exports point count for a 10 m x 10 m cell and normalised hight interval specified by the lower and upper limit parameters.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :param lower_limit: lower limit for the height interval to count in (normalised height in m).
    :param upper_limit: upper limit for the height interval to count in (normalised height in m).
    :return: execution status
    """
    # Initiate return value
    return_value = ''

    # Generate paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    out_folder = settings.output_folder + '/point_count'
    prefix = 'veg_point_count_' + str(lower_limit) + 'm-' + str(upper_limit) + 'm'
    out_file = out_folder + '/' + prefix + '/' + prefix + '_' + tile_id + '.tif'

    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/' + prefix): os.mkdir(out_folder + '/' + prefix)

    # Export normalized z raster mean and sd
    try:
        # Initialise exporter
        export_point_count = opals.Cell.Cell()

        # Export mean
        export_point_count.inFile = odm_file
        export_point_count.outFile = out_file
        export_point_count.filter = 'generic[NormalizedZ >= ' + str(lower_limit) + ' and NormalizedZ < ' + \
                                    str(upper_limit) + '] AND ' + settings.veg_classes_filter
        export_point_count.feature = 'pcount'
        export_point_count.cellSize = settings.out_cell_size
        export_point_count.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_point_count.commons.screenLogLevel = opals.Types.LogLevel.none
        export_point_count.commons.nbThreads = settings.nbThreads
        export_point_count.run()

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Return exist status
    return (return_value)


def odm_export_ground_point_count(tile_id, lower_limit = -1, upper_limit = 1):
    """
    Exports point count for a 10 m x 10 m cell and normalised hight interval specified by the lower and upper limit parameters.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :param lower_limit: lower limit for the height interval to count in (normalised height in m).
    :param upper_limit: upper limit for the height interval to count in (normalised height in m).
    :return: execution status
    """
    # Initiate return value
    return_value = ''

    # Generate paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    out_folder = settings.output_folder + '/point_count'
    prefix = 'ground_point_count_' + str(lower_limit) + 'm-' + str(upper_limit) + 'm'
    out_file = out_folder + '/' + prefix + '/' + prefix + '_' + tile_id + '.tif'

    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/' + prefix): os.mkdir(out_folder + '/' + prefix)

    # Export normalized z raster mean and sd
    try:
        # Initialise exporter
        export_point_count = opals.Cell.Cell()

        # Export mean
        export_point_count.inFile = odm_file
        export_point_count.outFile = out_file
        export_point_count.filter = 'generic[NormalizedZ >= ' + str(lower_limit) + ' and NormalizedZ < ' + \
                                    str(upper_limit) + '] AND generic[Classification == 2]'
        export_point_count.feature = 'pcount'
        export_point_count.cellSize = settings.out_cell_size
        export_point_count.limit = 'corner' # This switch is really important when working with tiles!
                                    # It sets the ROI to the extent to the bounding box of points in the ODM
        export_point_count.commons.screenLogLevel = opals.Types.LogLevel.none
        export_point_count.commons.nbThreads = settings.nbThreads
        export_point_count.run()

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Return exist status
    return (return_value)


def odm_export_veg_point_counts(tile_id):
    """
    Exports point counts for multiple, pre definided height intervals by calling the odm_export_point_count function.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate list for return values
    return_values = []

    # Execute point counts for all specified intervals

    # 0-2 m at 0.5 m intervals
    for lower in numpy.arange(0, 1.5, 0.5):
        return_values.append(odm_export_veg_point_count(tile_id, lower, lower + 0.5))

    # 2-20 m at 1 m intervals
    for lower in range(2, 19, 1):
        return_values.append(odm_export_veg_point_count(tile_id, lower, lower + 1))

    # 20-25 m at 5 m interval
    return_values.append(odm_export_veg_point_count(tile_id, 20, 25))

    # 25 m to 50 m
    return_values.append(odm_export_veg_point_count(tile_id, 25, 50))

    # Set return value status
    # There are only two return value states so if there is more than one return value in the list
    # one of them has to be an opalsError
    return_values = set(return_values)

    if len(return_values) > 1:
        return_value = "opalsError"
    else:
        return_value = list(return_values)[0]

    return return_value


def odm_export_amplitude(tile_id):
    """
    Exports mean and variacne for the lidar amplitude at the 10 m x 10 m grid cell.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''

    # Generate file paths
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    out_folder = settings.output_folder + '/amplitude'
    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/mean'): os.mkdir(out_folder + '/mean')
    if not os.path.exists(out_folder + '/sd'): os.mkdir(out_folder + '/sd')

    out_file_mean = out_folder + '/mean/amplitude_mean_' + tile_id + '.tif'
    out_file_sd = out_folder + '/sd/amplitude_mean_' + tile_id + '.tif'

    # Export normalized z raster mean and sd
    try:
        # Initialise exporter
        export_amplitude = opals.Cell.Cell()

        # Export mean
        export_amplitude.inFile = odm_file
        export_amplitude.outFile = out_file_mean
        export_amplitude.attribute = 'amplitude'
        export_amplitude.feature = 'mean'
        export_amplitude.cellSize = settings.out_cell_size
        export_amplitude.filter = settings.ground_and_veg_classes_filter # ground and veg points only
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
        export_amplitude.filter = settings.ground_and_veg_classes_filter  # ground and veg points only
        export_amplitude.limit = 'corner'  # This switch is really important when working with tiles!
        # It sets the ROI to the extent to the bounding box of points in the ODM
        export_amplitude.commons.screenLogLevel = opals.Types.LogLevel.none
        export_amplitude.commons.nbThreads = settings.nbThreads
        export_amplitude.run()

        return_value = 'success'
    except:
        return_value = 'opalsError'

    # Return exist status
    return (return_value)

def odm_export_point_source_info(tile_id):
    """

    :return:
    """

    # Initate return value
    return_value = ''

    # Set file path
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'

    # Set output paths
    out_folder = settings.output_folder + '/point_source_info'
    out_folder_ids = out_folder + '/point_source_ids'
    out_folder_counts = out_folder + '/point_source_counts'
    out_folder_prop = out_folder + '/point_source_proportion'

    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder_ids): os.mkdir(out_folder_ids)
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
        print point_source_ids

        # Remove dm object and close connection to odm file for later use
        del dm

        # Next use opals cell to extact point counts for each point source id
        for point_source_id in point_source_ids:

            # Initate opals cell module
            export_point_count = opals.Cell.Cell()

            # Export point count
            export_point_count.inFile = odm_file
            export_point_count.outFile = 'temp_count_' + str(point_source_id) + '.tif'
            export_point_count.filter =  settings.ground_and_veg_classes_filter +\
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
        subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # calculate proportions
        for point_source_id in point_source_ids:
            # Specify gdal command
            cmd = settings.gdal_calc_bin + '-A ' + temp_wd + '/temp_count_' + str(
                point_source_id) + '.tif ' + '-B ' + temp_wd + '/temp_total_points.tif ' + \
                  '--outfile=' + temp_wd + '/point_source_prop_' + str(
                point_source_id) + '.tif --calc=A/B ' + '--NoDataValue=-9999'
            # Execute gdal command
            subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Merge files into one:
        # Specify gdal command
        in_files_string = '.tif ' + temp_wd + '/point_source_prop_'
        in_files_string = temp_wd + '/point_source_prop_' + in_files_string.join(
            [str(i) for i in point_source_ids]) + '.tif'
        cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + out_folder_prop + '/point_source_prop_' + tile_id + '.tif ' +\
             in_files_string

        # Execute gdal command
        subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        ## Create a layer with presence / absence of point source id indicated by the point source id itself
        for point_source_id in point_source_ids:
            # Specify gdal command
            cmd = settings.gdal_calc_bin + '-A ' + temp_wd + '/temp_count_' + str(point_source_id) + '.tif ' + \
                  '--outfile=' + temp_wd + '/temp_presence_' + str(point_source_id) + '.tif --calc=' + str(
                point_source_id) + '*greater(A,0)' + \
                  ' --NoDataValue=-9999'
            # Execute gdal command
            subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        ## Merge files into one:
        # Specify gdal command
        in_files_string = '.tif ' + temp_wd + '/temp_presence_'
        in_files_string = temp_wd + '/temp_presence_' + in_files_string.join(
            [str(i) for i in point_source_ids]) + '.tif'
        cmd = settings.gdal_merge_bin + '-a_nodata -9999 -separate ' + '-o ' + out_folder_ids + '/point_source_ids_' + tile_id + '.tif ' + \
              in_files_string

        # Execute gdal command
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

        # Remove temp files
        temp_tifs = glob.glob('*.tif')
        for tif in temp_tifs: os.remove(tif)

        return_value = 'success'
    except:
        return_value = 'opalsError'

    return return_value
