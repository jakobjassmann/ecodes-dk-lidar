

## Def: Export tile footprint
def laz_grid_footprint(laz_tile_id):
    """
    Exports footprint from a laz file based on the tile_id in the DK nationwide dataset
    :param laz_tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: returns nothing, but creates a
    """
    wd = os.getcwd()
    # Generate temporay wd for parallel worker this will allow opals sessions to run in parallel
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = wd + '/data/scratch/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)

    # Generate relevant file names:
    laz_file = wd + '/' + laz_folder + '/PUNKTSKY_1km_' + laz_tile_id + '.laz'
    odm_file = wd + '/' + odm_folder + '/odm_' + laz_tile_id + '.odm'
    temp_tif_file = wd + '/data/scratch/temp_' + laz_tile_id + '.tif'
    footprint_file = wd + '/' + odm_footprint_folder + '/footprint_' + laz_tile_id + '.shp'

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
    cmd = gdaltlindex_bin + ' ' + footprint_file + ' ' + temp_tif_file
    output = '\n' + tile_id + ' footprint generation... \n' + \
           subprocess.check_output(cmd, shell=False,  stderr=subprocess.STDOUT)

    # Remove temp raster file
    os.remove(temp_tif_file)

    # change back to main workdir
    os.chdir(wd)

    return output


## Def: Retrieve CRS
def laz_validate_crs(laz_tile_id):
    """
    Function to validate the crs of a dk nationwide LiDAR
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return:
    """
    # Generate temporay wd for parallel worker this will allow opals sessions to run in parallel
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = wd + '/data/scratch/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)

    # Generate odm file pathname
    odm_file = wd + '/' + odm_folder + '/odm_' + laz_tile_id + '.odm'
    #odm_file = 'O:/ST_Ecoinformatics/B_Read/Projects/LIDAR_ANDRAS_Project/DK_nationwide_output/dk_nationwide_odms' + \
    #            '\\\\' + laz_tile_id + '.odm'
    print(odm_file)
    crs_str = ''
    try:
        odm_dm = opals.pyDM.Datamanager.load(odm_file)
        crs_str = odm_dm.getCRS()
        odm_dm = None
    except:
        print('Could not load: ' + odm_file)

    os.chdir(wd)

    return crs_str
