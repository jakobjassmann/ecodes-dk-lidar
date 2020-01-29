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

##### Function definitions

## Define function to load neighbourhood of tiles into ODM
def create_tile_mosaic(tile_id):
    """
        Imports a tile (specified by tile_id) and it's 3 x 3 neighbourhood into a shared ODM file for subsequent
        processing.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns nothing.
    """

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
    except:
        log_output = log_output + tile_id + ' failed.\n\n'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()



## Def: Export tile footprint
def laz_grid_footprint(tile_id):
    """
    Exports footprint from a laz file based on the tile_id in the DK nationwide dataset
    :param laz_tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns nothing, but creates a
    """
    # Generate relevant file names:
    laz_file = settings.laz_folder + '/PUNKTSKY_1km_' + tile_id + '.laz'
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'
    temp_tif_file = os.getcwd() + '/temp_' + tile_id + '.tif'
    footprint_file = settings.odm_footprint_folder + '/footprint_' + tile_id + '.shp'

    # Try generating footpring
    try:
        # Import tile id
        import_tile = opals.Import.Import()
        import_tile.inFile = laz_file
        import_tile.outFile = odm_file
        import_tile.run()

        # Export temporary tif
        export_tif = opals.Cell.Cell()
        export_tif.inFile = odm_file
        export_tif.outFile = temp_tif_file
        export_tif.feature = 'min'
        export_tif.cellSize = 10 # This is also the default cell size, so technically not needed.
        export_tif.run()

        # Generate footprint for temp tif
        cmd = settings.gdaltlindex_bin + ' ' + footprint_file + ' ' + temp_tif_file
        log_output = '\n' + tile_id + ' footprint generation... \n' + \
            subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT) + \
                     tile_id + ' successful.\n\n'
    except:
        log_output = '\n' + tile_id + ' footprint generation... \n' + tile_id + ' failed.\n\n'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temp raster file
    os.remove(temp_tif_file)

    # change back to main workdir
    os.chdir(settings.wd)

## Def: Retrieve CRS
def laz_validate_crs(tile_id):
    """
    Function to validate the crs of a dk nationwide LiDAR
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return:
    """

    # Generate odm file pathname
    odm_file = settings.odm_folder + '/odm_' + tile_id + '.odm'

    print(odm_file)
    crs_str = ''
    try:
        odm_dm = opals.pyDM.Datamanager.load(odm_file)
        crs_str = odm_dm.getCRS()
        odm_dm = None
        log_output = '\n' + tile_id + ' CRS string: ' + crs_str + '\n\n'
    except:
        log_output = '\n' + tile_id + ' Unable to load file while retrieving CRS string.\n\n'