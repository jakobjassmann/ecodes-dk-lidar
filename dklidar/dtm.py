### Functions for DTM raster file handling for DK Lidar project
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

import os
import subprocess
import multiprocessing
import re
import pandas

from typing import Union

from dklidar import settings

#### Function definitions

## Generate tile footprint
def dtm_generate_footprint(tile_id):
    """
    Generates a footprint file using gdal
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return execution status
    """

    # Initiate return value and log output
    return_value = ''
    log_output = ''

    try:
        cmd = settings.gdaltlindex_bin + \
          settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
          settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif'
        cmd_return = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        log_output = log_output + '\n' + tile_id + ' footprint generation... \n' + cmd_return + \
                     '\n' + tile_id + ' successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' footprint generation failed. \n' + cmd_return
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    return return_value


## Create neighbourhood mosaic
def dtm_mosaic_neighbours(tile_id):
    """
    Generates a tif mosaic with all existing 8 neighbouring cells
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    input_folder: folder location for input dtm files. ouput_folder ouput location for dtm mosaics.
    :return: execution status
    """

    # Initate return value
    return_value = ''

    # Generate temporay wd for parallel worker, this will allow for smooth logging and opals sessions to run in parallel
    wd = os.getcwd()
    current_pid =  re.sub('[(),]', '', str(multiprocessing.current_process()._identity))
    temp_wd = settings.scratch_folder + '/temp_' + current_pid
    if not os.path.exists(temp_wd):
        os.mkdir(temp_wd)
    os.chdir(temp_wd)

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
        tile_file_name = settings.dtm_folder + '/DTM_1km_' + tile_to_load + '.tif'
        if os.path.exists(tile_file_name):
            tile_file_names.append(tile_file_name)
    n_neighbours = len(tile_file_names)
    tile_file_names = ' '.join(tile_file_names)

    if n_neighbours == 9:
        log_output = tile_id + ' mosaicing...\n' + 'Number of neighbours = ' + str(n_neighbours) + '. Complete!\n'
    else:
        log_output = tile_id + ' mosaicing...\n' + 'Warning! Number of neighbours = ' + str(n_neighbours) + '. Incomplete. Edge effects possible!\n'

    # Construct command:
    cmd = settings.gdalwarp_bin + ' ' + tile_file_names + ' ' + \
        settings.dtm_mosaics_folder + '/dtm_mosaic' + \
        tile_id + '.tif '

    # Execute command as subprocess and return message:
    try:
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        log_output = log_output + tile_id + ' successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + tile_id + ' failed.\n\n'
        return_value = "gdalError"

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Change back to original working directory
    os.chdir(wd)

    return return_value


## Calculcate heat index
def dtm_calc_heat_index(tile_id):
    """
    Calculates the aspect from DTM neighbourhood mosaic and crops to original tile_size
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Intialise return value and log
    return_value = ''
    log_output = ''

    # Get current wd
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/heat_load_index'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:

        # Specify path to aspect raster A
        aspect_file = '-A ' + settings.output_folder + '/aspect/aspect_' + tile_id + '.tif '

        # Construct numpy equation
        solar_rad_eq = '10000*((1-cos(radians(A-45)))/2)'

        # Specify output path
        out_file = out_folder + '/heat_load_index_' + tile_id + '.tif '

        # Specify equation
        # Construct gdal command:
        cmd = settings.gdal_calc_bin + aspect_file + '--outfile=' + out_file + \
              ' --calc=' + solar_rad_eq + ' --type=Int16' + ' --NoDataValue=-9999 --overwrite'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' calculating solar radiation... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    except:
        log_output = tile_id + ' calculating heat index failed. \n '
        return_value = 'gdal_error'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    os.remove(settings.output_folder + '/dtm_slope/slope_' + tile_id + '_mosaic.tif ')

def dtm_calc_solar_radiation(tile_id):
    """
    Returns cell by cell solar radiation following McCune and Keon 2002. Slope and aspect must have been calculated
    beforehand using dtm_calc_slope and dtm_valc_aspect
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # The calculation of the solar radiation is a thre step process
    # 1) Obtain a raster with the latitude of the centre of the cell in radians
    # 2) Fold the aspect around the North-South line (see McCune and Keon).
    # 3) Calculate the solar radiation using the formula form McCune and Keom

    # initiate return value and log ouptut
    return_value = ''
    log_output = ''

    # Get current wd
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/solar_rad'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:
        # 1) Create raster with latitude of the centre of a cell
        # Construct gdal command to export xyz file in utm

        dtm_file = settings.output_folder + '/slope/slope_' + tile_id + '.tif'
        out_file = wd + '/xyz_' + tile_id + '.xyz'
        cmd = settings.gdal_translate_bin + ' -of xyz -co COLUMN_SEPARATOR="," -co ADD_HEADER_LINE=YES ' + \
              dtm_file + ' ' + \
              out_file

        log_output = tile_id + ' generating xyz... \n ' + subprocess.check_output(cmd, shell=False,
                                                                                  stderr=subprocess.STDOUT)

        # Read in xyz as a pandas dataframe
        xyz = pandas.read_csv('xyz_' + tile_id + '.xyz')
        xy = xyz[["X", "Y"]]
        xy.to_csv('xy_' + tile_id + '.csv', index=False, header=False, sep=' ')

        # Construct gdal commands to transform cell coordinates from utm to lat long
        in_file = wd + '/xy_' + tile_id + '.csv'
        out_file = 'xy_' + tile_id + '_latlong.csv'
        cmd = '(' + settings.gdaltransform_bin + ' -s_srs EPSG:25832 -t_srs WGS84 ' + \
              ' < ' + in_file + ') > ' + out_file

        # And execute the gdal command
        log_output = tile_id + ' transforming to lat long... \n ' + subprocess.check_output(cmd, shell=True)

        # Load lat long file
        xy_latlong = pandas.read_csv('xy_' + tile_id + '_latlong.csv', sep='\s+', names=['X', 'Y', 'return_status'],
                                     skiprows=1)

        # check data frames are of the same lenght
        if len(xyz.index) != len(xy_latlong.index):
            log_output = log_output + '\n lenght of dataframes did not match \n'
            raise Exception("")

        # Assign lat (deg) to UTM z coordinate
        xyz["Z"] = xy_latlong["Y"]
        xyz.to_csv('xyz_' + tile_id + '.xyz', index=False, header=False, sep=' ')

        # Convert back to geotiff
        in_file = wd + '/xyz_' + tile_id + '.xyz'
        out_file = wd + '/lat_' + tile_id + '.tif'
        cmd = settings.gdal_translate_bin + ' -of GTiff -a_srs EPSG:25832 ' + \
              in_file + ' ' + out_file

        log_output = tile_id + ' generating xyz... \n ' + subprocess.check_output(cmd, shell=False,
                                                                                  stderr=subprocess.STDOUT)
        # Intermediate clean up
        os.remove('xyz_' + tile_id + '.xyz')
        os.remove('xy_' + tile_id + '.csv')
        os.remove('xy_' + tile_id + '_latlong.csv')
        del (xy)
        del (xy_latlong)
        del (xyz)

        ## Calculate Solar radiation
        # The equation from McCune and Keon goes as follows:
        # solar radiation =  0.339 +
        #                    0.808 x cos(lat) x cos(slope) +
        #                   -0.196 x sin(lat) x sin(slope) +
        #                   -0.482 x cos(asp) x sin(slope)
        # Aspect must be foldered around the S-N line:
        # asp = 180 - |180 - asp|
        # and all values mus be in radians:
        # rad = deg * pi / 180 or using numpy simply: rad = radians(deg)

        # Specify path to latitude raster L
        lat_file = '-L ' + wd + '/lat_' + tile_id + '.tif '

        # Specify path to slope raster as raster S
        slope_file = '-S ' + settings.output_folder + '/slope/slope_' + tile_id + '.tif '

        # Specify path to aspect raster A
        aspect_file = '-A ' + settings.output_folder + '/aspect/aspect_' + tile_id + '.tif '

        # Construct numpy equation
        solar_rad_eq = '1000*(0.339+0.808*cos(radians(L))*cos(radians(S))-0.196*sin(radians(L))*sin(radians(S))-0.482*cos(radians(180-absolute(180-A)))*sin(radians(S)))'

        # Specify output path
        out_file = out_folder + '/solar_rad_' + tile_id + '.tif '

        # Construct gdal command:
        cmd = settings.gdal_calc_bin + lat_file + slope_file + aspect_file + '--outfile=' + out_file + \
              ' --calc=' + solar_rad_eq + ' --type=Int16' + ' --NoDataValue=-9999 --overwrite'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' calculating solar radiation... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    except:
        log_output = tile_id + ' calculating solar radiation failed. \n '
        return_value = 'gdal_error'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    print(return_value)





## Calculate slope parameter for file
def dtm_calc_slope(tile_id):
    """
    Calculates the slope parameter for a DTM neighbourhood mosaic and crops to original tile_size
    Requires dtm_generate_mosaic to be executed.
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: stdout and stderr command line output of gdal command execution.
    """

    # Initiate return value and log output
    return_value = ''
    log_output = ''

    # Get current wd
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/slope'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:
        # Calculate slope parameter
        cmd = settings.gdaldem_bin + ' slope ' + \
            settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
            wd + '/slope_' + tile_id + '_mosaic.tif '
        log_output = tile_id + ' slope calculation... \n ' + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Croping slope output to original tile size and aggregate to 10 m scale by median
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
               '-tr 10 10 -r med -ot Int16 ' + '-crop_to_cutline -overwrite ' + \
              wd + '/slope_' + tile_id + '_mosaic.tif ' + \
              settings.output_folder + '/slope/slope_' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' slope calculation successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' slope calculation failed. \n\n'
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    try:
        os.remove(wd + '/slope_' + tile_id + '_mosaic.tif ')
    except:
        pass

    # Return return value
    return return_value


## Calculate slope for a tile
def dtm_calc_aspect(tile_id):
    """
    Calculates the slope parameter for a DTM neighbourhood mosaic and crops to original tile_size
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # Initiate return valule and log output
    return_value = ''
    log_output = ''

    # get temporary work directory
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/aspect'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:
        # Calculate slope parameter
        cmd = settings.gdaldem_bin + ' aspect -zero_for_flat ' + \
        settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
        wd + '/aspect_' + tile_id + '_mosaic.tif '
        log_output = tile_id + ' aspect calculation... \n ' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Crop slope output to original tile size:
        cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
           '-tr 10 10 -r med -ot Int16 ' + '-crop_to_cutline -overwrite ' + \
          wd + '/aspect_' + tile_id + '_mosaic.tif ' + \
          settings.output_folder + '/aspect/aspect_' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aspect calculation successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' slope calculation failed.\n\n'
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    try:
        os.remove(wd + '/aspect_' + tile_id + '_mosaic.tif ')
    except:
        pass

    return return_value

## Calculate SAGA Wetness Index for a tile
def dtm_saga_wetness(tile_id):
    """
    Calculates the saga wetness index for a tile mosaic then crops to the original tile.
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # Initiate return valule and log output
    return_value = ''
    log_output = ''

    # get temporary work directory
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/wetness_index'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:
        # Calculate wetness index at DTM scale
        cmd = settings.saga_wetness_bin + '-DEM ' + \
        settings.dtm_mosaics_folder + '/DTM_' + tile_id + '_mosaic.tif ' + \
        wd + '/wetness_index' + tile_id + '_mosaic.tif '
        log_output = tile_id + ' wetness index calculation... \n ' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)


        # Crop slope output to original tile size:
        cmd = settings.gdalwarp_bin + \
          ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
            '-tr 10 10 -r med ' + '-crop_to_cutline -overwrite ' + \
          wd + '/wetness_index' + tile_id + '_mosaic.tif ' + \
          wd + '/wetness_index_' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' cropping wetness index mosaic.\n\n'
        return_value = 'success'

        # Set input file path
        in_file = wd + '/wetness_index_' + tile_id + '.tif '
        # Set output file path
        out_file = out_folder + '/wetness_index_' + tile_id + '.tif '

        # Stretch to by 10000 and convert to int 16
        # Construct gdal command:
        cmd = settings.gdal_calc_bin +  + '--outfile=' + out_file + \
              ' --calc=10000*A --type=Int16' + ' --NoDataValue=-9999 --overwrite'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' converting to integer... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

    except:
        log_output = log_output + '\n' + tile_id + ' wetness index calculation failed.\n\n'
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    try:
        os.remove(wd + '/wetness_index' + tile_id + '_mosaic.tif ' )
        os.remove(wd + '/wetness_index_' + tile_id + '.tif ')
    except:
        pass

    return return_value
# SAGA Wetness Index
#"C:\OSGeo4W64\apps\saga-ltr\saga_cmd.exe" ta_hydrology 15 -DEM D:\Jakob\dk_nationwide_lidar\data\sample\dtm_mosaics\DTM_6210_570_mosaic.tif -TWI TWI_621_570.tif
# Then convert ot geotiff using gdal
# "C:/OSGeo4W64/OSGeo4W.bat" gdalwarp -tr 10 10 -r med TWI_621_570.sdat TWI_6210_570.tif

## Aggregate dem to 10 m
def dtm_aggregate(tile_id):
    """
    Aggregates the 0.4 m DTM to 10 m size for final output and other calculations.
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # Initiate return valule and log output
    return_value = ''
    log_output = ''

    # get temporary work directory
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/dtm_10m'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:
        ## Aggregate dtm to temporary file:
        # Specify gdal command
        cmd = settings.gdalwarp_bin + \
              '-tr 10 10 -r average ' + \
              settings.dtm_folder + '/DTM_1km_' + tile_id + '.tif ' + \
              wd + '/dtm_10m_' + tile_id + '_float.tif '
        print cmd
        # Execute gdal command
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' aggregating dtm_10m successful.\n\n'

        out_file = out_folder + '/dtm_10m_' + tile_id + '.tif'

        # Multiply by 100 and store as int16
        # Specify gdal command
        cmd = settings.gdal_calc_bin + '-A ' + wd + '/dtm_10m_' + tile_id + '_float.tif ' + ' --outfile=' + out_file + \
              ' --calc=100*A' + ' --type=Int16' + ' --NoDataValue=-9999'
        print cmd
        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' converting dtm_10m to int16... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' dtm_10m aggregation failed.\n\n'
        return_value = 'gdalError'

        # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary files
    try:
        os.remove(wd + '/dtm_10m_' + tile_id + '_float.tif')
    except:
        pass

    return return_value

## Calculate landscape openness
#def dtm_