import opals
import os
from dklidar import settings
import glob
import subprocess

def odm_calc_proportions(tile_id, prop_name, point_count_id1, point_count_id2):
    """
    Function to calculate point count proportions
    :param tile_id: tile id in the format "rrrr_ccc" where rrrr is the row number and ccc is the column number.
    :param prop_name: name to be assinged to the proportions output
    :param point_count_id1: name of point count to be rationed (numerator)
    :param point_count_id2: name of point count to be rationed to (denominator)
    :return: execution status
    """
    return_value = ''

    # Generate paths
    num_file = settings.output_folder + '/point_count/' + point_count_id1 + '/' + point_count_id1 + '_' + tile_id + '.tif'
    den_file = settings.output_folder + '/point_count/' + point_count_id2 + '/' + point_count_id2 + '_' + tile_id + '.tif'

    out_folder = settings.output_folder + '/proportions'
    out_file = out_folder + '/' + prop_name + '/' + prop_name + '_' + tile_id + '.tif'

    if not os.path.exists(out_folder): os.mkdir(out_folder)
    if not os.path.exists(out_folder + '/' + prop_name): os.mkdir(out_folder + '/' + prop_name)

    try:
        # Specify gdal command
        cmd = settings.gdal_calc_bin + '-A ' + num_file + ' -B ' + den_file + ' --outfile=' + out_file + \
              ' --calc=1000*A/B' + ' --type=Int16' + ' --NoDataValue=-9999'
        print cmd
        # Execute gdal command
        subprocess.check_output(cmd)
        return_value = 'success'
    except:
        return_value = 'gdalError'

    return return_value

odm_calc_proportions('6210_570', 'canopy_openness', 'ground_and_water_point_count_-1m-1m',
                         'total_point_count_-1m-50m')