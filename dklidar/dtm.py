### Functions for DTM raster file handling for DK Lidar project
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

import os
import subprocess
import re
import pandas
import opals
import glob

from dklidar import settings
from dklidar import common

#### Function definitions

## Generate tile footprint
def dtm_generate_footprint(tile_id):
    """
    Generates a footprint file using gdal.
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
def dtm_neighbourhood_mosaic(tile_id):
    """
    Generates a tif mosaic with all existing 8 neighbouring cells
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    input_folder: folder location for input dtm files. ouput_folder ouput location for dtm mosaics.
    :return: execution status
    """

    # Initate return value and log
    return_value = ''
    log_output = ''

    # get current (temporary) work directory
    temp_wd = os.getcwd()

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
        settings.dtm_mosaics_folder + '/dtm_' + tile_id + '_mosaic.tif '

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

    return return_value


## Aggregate dem to 10 m
def dtm_aggregate_tile(tile_id):
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

        # Execute gdal command
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' aggregating dtm_10m successful.\n\n'

        out_file = out_folder + '/dtm_10m_' + tile_id + '.tif'

        # Stretch by 100, round and store as int16
        # Specify gdal command
        cmd = settings.gdal_calc_bin + \
              '-A ' + wd + '/dtm_10m_' + tile_id + '_float.tif ' + \
              ' --outfile=' + out_file + \
              ' --calc=rint(100*A)' + ' --type=Int16' + ' --NoDataValue=-9999'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' converting dtm_10m to int16... \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Apply mask(s)
        common.apply_mask(out_file)

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


## Calculate slope for file
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
            settings.dtm_mosaics_folder + '/dtm_' + tile_id + '_mosaic.tif ' + \
            wd + '/slope_' + tile_id + '_mosaic.tif '
        log_output = tile_id + ' slope calculation... \n ' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Crop slope mosaic output to original tile size and aggregate to 10 m scale by median
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
               '-tr 10 10 -r med -crop_to_cutline -overwrite ' + \
              wd + '/slope_' + tile_id + '_mosaic.tif ' + \
              wd + '/slope_' + tile_id + '_mosaic_cropped.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' cropped slope.\n\n'

        # Round and store slope as int16
        cmd = settings.gdal_calc_bin + \
              '-A ' + wd + '/slope_' + tile_id + '_mosaic_cropped.tif ' + \
              ' --outfile=' + out_folder + '/slope_' + tile_id + '.tif ' + \
              ' --calc=rint(A) --type=Int16 --NoDataValue=-9999'
        log_output = log_output + '\n' + tile_id + ' rounding slope and calculation successful. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Apply mask(s)
        common.apply_mask(out_folder + '/slope_' + tile_id + '.tif ')

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
        os.remove(wd + '/slope_' + tile_id + '_mosaic_cropped.tif ')
    except:
        pass

    # Return return value
    return return_value


## Calculate aspect for a tile
def dtm_calc_aspect(tile_id):
    """
    Calculates the aspect for all 10 m cells in a DTM neighbourhood mosaic and crops to original tile_size
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
        # Calculate aspect
        cmd = settings.gdaldem_bin + ' aspect -zero_for_flat ' + \
              settings.dtm_mosaics_folder + '/dtm_' + tile_id + '_mosaic.tif ' + \
              wd + '/aspect_' + tile_id + '_mosaic.tif '
        log_output = tile_id + ' aspect calculation... \n ' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Crop aspect output to original tile size and aggregate to 10 m:
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
              '-tr 10 10 -r med -crop_to_cutline -overwrite ' + \
              wd + '/aspect_' + tile_id + '_mosaic.tif ' + \
              wd + '/aspect_' + tile_id + '_mosaic_cropped.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                 '\n' + tile_id + ' aspect mosaic cropped.\n\n'

        # Round and store as int16
        cmd = settings.gdal_calc_bin + \
              '-A ' + wd + '/aspect_' + tile_id + '_mosaic_cropped.tif ' + \
              ' --outfile=' + out_folder + '/aspect_' + tile_id + '.tif ' + \
              ' --calc=rint(A) --type=Int16 --NoDataValue=-9999'
        log_output = log_output + '\n' + tile_id + ' rounding aspect to int16 and calculation success. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Apply mask(s)
        common.apply_mask(out_folder + '/aspect_' + tile_id + '.tif ')

        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' aspect calculation failed.\n\n'
        return_value = 'gdalError'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary file
    try:
        os.remove(wd + '/aspect_' + tile_id + '_mosaic.tif ')
        os.remove(wd + '/aspect_' + tile_id + '_mosaic_cropped.tif ')
    except:
        pass

    return return_value


## Calculcate heat index
def dtm_calc_heat_index(tile_id):
    """
    Calculates the heat index from McCune and Keon (2002) based on the aspect only. Aspect must have been
    calculated using dtm_calc_aspect().
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

        # Construct numpy equation, stretch by 10k and round
        heat_index = 'rint(10000*((1-cos(radians(A-45)))/2))'

        # Specify output path
        out_file = out_folder + '/heat_load_index_' + tile_id + '.tif '

        # Construct gdal command, save file as Int16:
        cmd = settings.gdal_calc_bin + \
              aspect_file + \
              '--outfile=' + out_file + \
              ' --calc=' + heat_index + \
              ' --type=Int16 --NoDataValue=-9999 --overwrite'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' calculating heat index success. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Apply mask(s)
        common.apply_mask(out_file)

        return_value = 'success'
    except:
        log_output = tile_id + ' calculating heat index failed. \n '
        return_value = 'gdal_error'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    return return_value


## Calculate solar radiation
def dtm_calc_solar_radiation(tile_id):
    """
    Returns cell by cell solar radiation following McCune and Keon 2002. Slope and aspect must have been calculated
    beforehand using dtm_calc_slope and dtm_calc_aspect.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # The calculation of the solar radiation is a two step process
    # 1) Obtain a raster with the latitude of the centre of the cell in radians
    # 2) Calculate the solar radiation using the formula form McCune and Keon 2002

    # initiate return value and log ouptut
    return_value = ''
    log_output = ''

    # Get current wd
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/solar_radiation'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:
        # 1) Create raster with latitude of the centre of a cell
        # Construct gdal command to export xyz file in utm
        dtm_file = settings.output_folder + '/slope/slope_' + tile_id + '.tif'
        out_file = wd + '/xyz_' + tile_id + '.xyz'
        cmd = settings.gdal_translate_bin + \
              ' -of xyz -co COLUMN_SEPARATOR="," -co ADD_HEADER_LINE=YES ' + \
              dtm_file + ' ' + \
              out_file
        # Execute gdal command and log
        log_output = log_output + '\n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' generated xyz. \n\n '

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
        log_output = log_output + '\n' + \
                     subprocess.check_output(cmd, shell=True) + \
                     '\n' + tile_id + ' transformed to lat long. \n\n '

        # Load lat long file as pandas df
        xy_latlong = pandas.read_csv('xy_' + tile_id + '_latlong.csv', sep='\s+', names=['X', 'Y', 'return_status'],
                                     skiprows=1)

        # check data frames are of the same length
        if len(xyz.index) != len(xy_latlong.index):
            log_output = log_output + '\n lenght of dataframes did not match \n'
            raise Exception("")

        # Assign lat (deg) to UTM z coordinate
        xyz["Z"] = xy_latlong["Y"]
        xyz.to_csv('xyz_' + tile_id + '.xyz', index=False, header=False, sep=' ')

        # Convert back to geotiff, prepare gdal translate command
        in_file = wd + '/xyz_' + tile_id + '.xyz'
        out_file = wd + '/lat_' + tile_id + '.tif'
        cmd = settings.gdal_translate_bin + \
              ' -of GTiff -a_srs EPSG:25832 ' + \
              in_file + ' ' + \
              out_file
        # Execute command and log
        log_output = log_output + '\n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' generated lat tif. \n\n'
        # Intermediate clean up
        os.remove(wd + '/xyz_' + tile_id + '.xyz')
        os.remove(wd + '/xy_' + tile_id + '.csv')
        os.remove(wd + '/xy_' + tile_id + '_latlong.csv')
        del (xy)
        del (xy_latlong)
        del (xyz)

        ## 2) Calculate Solar radiation

        # The equation from McCune and Keon goes as follows:
        # solar radiation =  0.339 +
        #                    0.808 x cos(lat) x cos(slope) +
        #                   -0.196 x sin(lat) x sin(slope) +
        #                   -0.482 x cos(asp) x sin(slope)
        # Aspect must be foldered around the S-N line:
        # asp = 180 - |180 - asp|
        # and all values mus be in radians:
        # rad = deg * pi / 180 or using numpy simply: rad = radians(deg)
        # Finally, the result needs to be stretched by 1000 and rounded for storage as an Int16

        # Specify path to latitude raster L
        lat_file = '-L ' + wd + '/lat_' + tile_id + '.tif '

        # Specify path to slope raster as raster S
        slope_file = '-S ' + settings.output_folder + '/slope/slope_' + tile_id + '.tif '

        # Specify path to aspect raster A
        aspect_file = '-A ' + settings.output_folder + '/aspect/aspect_' + tile_id + '.tif '

        # Construct numpy equation (based on McCune and Keon 2002) and stretch by 1000 and round to nearest int.
        solar_rad_eq = 'rint(1000*(0.339+0.808*cos(radians(L))*cos(radians(S))-0.196*sin(radians(L))*sin(radians(S))-0.482*cos(radians(180-absolute(180-A)))*sin(radians(S))))'

        # Specify output path
        out_file = out_folder + '/solar_rad_' + tile_id + '.tif '

        # Construct gdal command:
        cmd = settings.gdal_calc_bin + \
              lat_file + \
              slope_file + \
              aspect_file + \
              '--outfile=' + out_file + \
              '--calc=' + solar_rad_eq + ' ' + \
              '--type=Int16 --NoDataValue=-9999 --overwrite'

        # Execute gdal command
        log_output = log_output + '\n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' calculated solar radiation. \n\n'

        # Apply mask(s)
        common.apply_mask(out_file)

        # Remove latitude tif
        os.remove(wd + '/lat_' + tile_id + '.tif')
        return_value = 'success'
    except:
        log_output = log_output + '\n\n' + tile_id + ' calculating solar radiation failed. \n '
        return_value = 'gdal_error'

    # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    return return_value


## Calculate landscape openness mean
def dtm_openness_mean(tile_id):
    """
    Exports the mean landscape openness for all eight cardinal directions with a 150 m search radius
    using the OPALS Openness module.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''
    log_output = ''

    # Get working directory
    wd = os.getcwd()

    # Generate folder paths
    out_folder = settings.output_folder + '/openness_mean'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    # Attempt calculation of mean openness
    try:

        ## Aggregate dtm mosaic to 10 m in a temporary file:
        # Specify gdal command
        cmd = settings.gdalwarp_bin + \
              '-tr 10 10 -r average ' + \
              settings.dtm_mosaics_folder + '/dtm_' + tile_id + '_mosaic.tif ' + \
              wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ' + ' -overwrite'

        # Execute gdal command
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' aggregated dtm_10m mosaic.\n\n'

        # Initialise Opals Openness Module
        export_openness = opals.Openness.Openness()

        # Export positive openness for a given cell cell with a search radius of 150 m (15 cells)
        export_openness.inFile = wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '
        export_openness.outFile = wd + '/openness_150m_' + tile_id + '_mosaic.tif '
        export_openness.feature = opals.Types.OpennessFeature.positive
        export_openness.kernelSize = 15  # 15 x 10 m = 150 m
        export_openness.selMode = 0
        export_openness.noData = -9999
        export_openness.commons.screenLogLevel = opals.Types.LogLevel.none
        export_openness.commons.nbThreads = settings.nbThreads
        export_openness.run()

        # Convert to degrees, round and store as int16
        # Specify gdal command
        cmd = settings.gdal_calc_bin + \
              '-A ' + wd + '/openness_150m_' + tile_id + '_mosaic.tif ' + \
              ' --outfile=' + wd + '/landscape_openness_' + tile_id + '_mosaic.tif ' + \
              ' --calc=rint(degrees(A))' + \
              ' --type=Int16 --NoDataValue=-9999'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' converted and rounded to degrees. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Obtain file extent for cropping then remove outer 150 m of mosaic to avoid edge effects
        cmd = settings.gdalinfo_bin + wd + '/landscape_openness_' + tile_id + '_mosaic.tif '

        mosaic_info = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        upper_left = re.search("Upper *Left *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
        lower_right = re.search("Lower *Right *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
        xmin = float(upper_left.group(1)) + 150
        ymax = float(upper_left.group(2)) - 150
        xmax = float(lower_right.group(1)) - 150
        ymin = float(lower_right.group(2)) + 150

        # remove 150 m on outer edge using gdalwarp
        cmd = settings.gdalwarp_bin + \
              '-te ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + ' -overwrite ' + \
              wd + '/landscape_openness_' + tile_id + '_mosaic.tif ' + \
              wd + '/landscape_openness_' + tile_id + '_mosaic_cropped.tif '

        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' cropping landscape openness mosaic finished.\n\n'

        # Crop openness mosaic to original tile size (this will set all edges removed earlier to NA)
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
              '-crop_to_cutline -overwrite ' + \
              wd + '/landscape_openness_' + tile_id + '_mosaic_cropped.tif ' + \
              out_folder + '/openness_mean' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' landscape openness calculation successful.\n\n'

        # Apply mask(s)
        common.apply_mask(out_folder + '/openness_mean' + tile_id + '.tif ')

        return_value = 'success'

    except:
        return_value = 'opals/gdal/Error'

    # Remove temporary files
    try:
        os.remove(wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ')
        os.remove(wd + '/openness_150m_' + tile_id + '_mosaic.tif ')
        os.remove(wd + '/landscape_openness_' + tile_id + '_mosaic.tif ')
        os.remove(wd + '/landscape_openness_' + tile_id + '_mosaic_cropped.tif ')
        # and are super random files created by OPALS
        for temp_file in glob.glob(wd + '/../*' + tile_id + '_mosaic_dz._dz.tif'):
            os.remove(temp_file)
    except:
        pass

    return return_value


## Calculate landscape openness difference
def dtm_openness_difference(tile_id):
    """
    Exports the difference between the minimum and maximum positive openness within a 50 m search radius
    using the Opals Openness module.
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """
    # Initiate return value
    return_value = ''
    log_output = ''

    # Get working directory
    wd = os.getcwd()

    # Generate folder paths
    out_folder = settings.output_folder + '/openness_difference'
    if not os.path.exists(out_folder): os.mkdir(out_folder)


    # Attempt openness difference calculation
    try:
        ## Aggregate dtm mosaic to 10 m in a temporary file:
        # Specify gdal command
        cmd = settings.gdalwarp_bin + \
              '-tr 10 10 -r average -overwrite ' + \
              settings.dtm_mosaics_folder + '/dtm_' + tile_id + '_mosaic.tif ' + \
              wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '

        # Execute gdal command
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' aggregated dtm_10m mosaic.\n\n'

        # Initialise Opals Openness Module
        export_openness = opals.Openness.Openness()

        # Export minimum positive openness for a given cell cell with a kernel size of 50 m x 50 m
        export_openness.inFile = wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '
        export_openness.outFile = wd + '/openness_50m_min_' + tile_id + '_mosaic.tif '
        export_openness.feature = opals.Types.OpennessFeature.positive
        export_openness.kernelSize = 5  # 5 x 10 m = 50 m
        export_openness.selMode = 1
        export_openness.noData = -9999
        export_openness.commons.screenLogLevel = opals.Types.LogLevel.none
        export_openness.commons.nbThreads = settings.nbThreads
        export_openness.run()

        export_openness.reset()

        # Export maximum positive openness for a given cell with a kernel size of 50 m x 50 m
        export_openness.inFile = wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif '
        export_openness.outFile = wd + '/openness_50m_max_' + tile_id + '_mosaic.tif '
        export_openness.feature = opals.Types.OpennessFeature.positive
        export_openness.kernelSize = 5  # 5 x 10 m = 50 m
        export_openness.selMode = 2
        export_openness.noData = -9999
        export_openness.commons.screenLogLevel = opals.Types.LogLevel.none
        export_openness.commons.nbThreads = settings.nbThreads
        export_openness.run()

        # Calculate difference, round and store as int16
        # Specify gdal command
        cmd = settings.gdal_calc_bin + \
              '-A ' + wd + '/openness_50m_min_' + tile_id + '_mosaic.tif ' + \
              '-B ' + wd + '/openness_50m_max_' + tile_id + '_mosaic.tif ' + \
              ' --outfile=' + wd + '/diff_openness_' + tile_id + '_mosaic.tif ' + \
              ' --calc=rint(degrees(B)-degrees(A))' + \
              ' --type=Int16 --NoDataValue=-9999'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' calculated difference openness. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Obtain file extent for cropping (remove outer 50 m of mosaic)
        cmd = settings.gdalinfo_bin + wd + '/diff_openness_' + tile_id + '_mosaic.tif '

        mosaic_info = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        upper_left = re.search("Upper *Left *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
        lower_right = re.search("Lower *Right *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
        xmin = float(upper_left.group(1)) + 50
        ymax = float(upper_left.group(2)) - 50
        xmax = float(lower_right.group(1)) - 50
        ymin = float(lower_right.group(2)) + 50

        # Remove 50 m on outer edge using gdalwarp
        cmd = settings.gdalwarp_bin + \
              '-te ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + ' -overwrite ' + \
              wd + '/diff_openness_' + tile_id + '_mosaic.tif ' + \
              wd + '/diff_openness_' + tile_id + '_mosaic_cropped.tif '

        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' cropped openness difference mosaic.\n\n'

        # Crop diff openness to original tile size (this will set all edges removed earlier to NA)
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
              '-crop_to_cutline -overwrite ' + \
              wd + '/diff_openness_' + tile_id + '_mosaic_cropped.tif ' + \
              out_folder + '/openness_difference' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' openness calculation successful.\n\n'

        # Apply mask(s)
        common.apply_mask(wd + '/diff_openness_' + tile_id + '_mosaic_cropped.tif ')

        return_value = 'success'

    except:
        return_value = 'opals/gdal/Error'

    # Remove temporary files
    try:
        os.remove(wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ')
        os.remove(wd + '/openness_50m_min_' + tile_id + '_mosaic.tif ')
        os.remove(wd + '/openness_50m_max_' + tile_id + '_mosaic.tif ')
        os.remove(wd + '/diff_openness_' + tile_id + '_mosaic.tif ')
        os.remove(wd + '/diff_openness_' + tile_id + '_mosaic_cropped.tif ')
        # and are super random files created by OPALS
        for temp_file in glob.glob(wd + '/../*' + tile_id + '_mosaic_dz._dz.tif'):
            os.remove(temp_file)
    except:
        pass

    # Return exist status
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
              settings.dtm_mosaics_folder + '/dtm_' + tile_id + '_mosaic.tif ' + \
              '-TWI ' + wd + '/wetness_index_' + tile_id + '_mosaic.tif'
        log_output = tile_id + ' wetness index calculation finished. \n ' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Crop output to original tile size:
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
              '-tr 10 10 -r med -crop_to_cutline -overwrite ' + \
              wd + '/wetness_index_' + tile_id + '_mosaic.sdat ' + \
              wd + '/wetness_index_' + tile_id + '.tif '

        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' cropping wetness index mosaic successful.\n\n'
        return_value = 'success'

        # Set input file path
        in_file = wd + '/wetness_index_' + tile_id + '.tif '
        # Set output file path
        out_file = out_folder + '/wetness_index_' + tile_id + '.tif '

        # Stretch to by 1000, round and convert to int 16
        # Construct gdal command:
        cmd = settings.gdal_calc_bin + \
              '-A ' + wd + '/wetness_index_' + tile_id + '.tif ' + \
              '--outfile=' + out_file + \
              ' --calc=rint(1000*A) --type=Int16 --NoDataValue=-9999 --overwrite'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' rounding and conversion finished. ' \
                                                   'Wetness index calculation successful. \n' + \
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
        os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.sdat ')
        os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.prj ')
        os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.sgrd ')
        os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.mgrd ')
        os.remove(wd + '/wetness_index_' + tile_id + '_mosaic.tif ')
        os.remove(wd + '/wetness_index_' + tile_id + '.tif ')
    except:
        pass

    return return_value


## Calculate landscape openness (mean) using SAGA
def dtm_saga_landscape_openness(tile_id):
    """
    Calculates landscape opennes following Yokoyama et al. 2002 based on an aggregated 10 m dtm and a 150 m search radius.
    :param tile_id: tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :return: execution status
    """

    # Initiate return valule and log output
    return_value = ''
    log_output = ''

    # get temporary work directory
    wd = os.getcwd()

    # Prepare output folder
    out_folder = settings.output_folder + '/landscape_openness'
    if not os.path.exists(out_folder): os.mkdir(out_folder)

    try:
        ## Aggregate dtm mosaic to temporary file:
        # Specify gdal command
        cmd = settings.gdalwarp_bin + \
              '-tr 10 10 -r average ' + \
              settings.dtm_mosaics_folder + '/dtm_' + tile_id + '_mosaic.tif ' + \
              wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ' + ' -overwrite'

        # Execute gdal command
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' aggregating dtm_10m mosaic successful.\n\n'

        # Use saga gis openness module for calculating the openness in 150 m
        cmd = settings.saga_openness_bin + \
              '-DEM ' + wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif ' + \
              '-POS ' + wd + '/openness_10m_' + tile_id + '_mosaic.sdat ' + \
              '-RADIUS 150 -METHOD 1'

        # Execute saga command
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' openness from mosaic successful.\n\n'

        # Obtain file extent for cropping (remove outer 150 m of mosaic)
        cmd = settings.gdalinfo_bin + wd + '/openness_10m_' + tile_id + '_mosaic.sdat '

        mosaic_info = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        upper_left = re.search("Upper *Left *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
        lower_right = re.search("Lower *Right *\( *(\d+.\d+), *(\d+.\d+)\)", mosaic_info)
        xmin = float(upper_left.group(1)) + 150
        ymax = float(upper_left.group(2)) - 150
        xmax = float(lower_right.group(1)) - 150
        ymin = float(lower_right.group(2)) + 150

        # remove 150 m on outer edge using gdal warp
        cmd = settings.gdalwarp_bin + \
              '-te ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + ' -overwrite ' + \
              wd + '/openness_10m_' + tile_id + '_mosaic.sdat ' + \
              wd + '/openness_10m_' + tile_id + '_mosaic.tif '

        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' cropping wetness index mosaic.\n\n'

        # Convert to degrees, round and store as int16
        # Specify gdal command
        cmd = settings.gdal_calc_bin + \
              '-A ' + wd + '/openness_10m_' + tile_id + '_mosaic.tif ' + \
              ' --outfile=' + wd + '/openness_10m_' + tile_id + '_mosaic_deg.tif ' + \
              ' --calc=rint(degrees(A))' + ' --type=Int16' + ' --NoDataValue=-9999'

        # Execute gdal command
        log_output = log_output + '\n' + tile_id + ' converting dtm_10m to int16 successful. \n' + \
                     subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)

        # Crop slope output to original tile size:
        cmd = settings.gdalwarp_bin + \
              ' -cutline ' + settings.dtm_footprint_folder + '/DTM_1km_' + tile_id + '_footprint.shp ' + \
              '-crop_to_cutline -overwrite ' + \
              wd + '/openness_10m_' + tile_id + '_mosaic_deg.tif ' + \
              out_folder + '/openness_10m_' + tile_id + '.tif '
        log_output = log_output + subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT) + \
                     '\n' + tile_id + ' openness calculation successful.\n\n'
        return_value = 'success'
    except:
        log_output = log_output + '\n' + tile_id + ' opennes calculation failed.\n\n'
        return_value = 'gdalError'

        # Write log output to log file
    log_file = open('log.txt', 'a+')
    log_file.write(log_output)
    log_file.close()

    # Remove temporary files
    try:
        os.remove(wd + '/dtm_10m_' + tile_id + '_mosaic_float.tif')
        os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.sdat')
        os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.sgrd')
        os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.prj')
        os.remove(wd + '/openness_10m_' + tile_id + '_mosaic.mgrd')
        os.remove(wd + wd + '/openness_10m_' + tile_id + '_mosaic.tif')
        os.remove(wd + '/openness_10m_' + tile_id + '_mosaic_deg.tif')
    except:
        pass

    return return_value

