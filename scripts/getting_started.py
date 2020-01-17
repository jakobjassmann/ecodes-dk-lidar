# This is a simple script to explore data handling options with OPALS
# Jakob Assmann j.assmann@bios.au.dk 17 January 2020

# Imports
import glob
import re

# Set folder locations
laz_folder = 'data/sample/laz'
dtm_folder = 'data/sample/dtm'

# Obtain tile ids from laz file names
laz_files = glob.glob(laz_folder + '/*.laz')

# initiate dictionary
tile_ids = {}

# file dictionary with tile_id, as well as row number and column number
for file_name in laz_files:
    tile_id = re.sub('.*PUNKTSKY_1km_(\d*_\d*).laz', '\g<1>', file_name)
    row = int(re.sub('.*PUNKTSKY_1km_(\d+)_\d+.laz', '\g<1>', file_name))
    col = int(re.sub('.*PUNKTSKY_1km_\d+_(\d+).laz', '\g<1>', file_name))
    tile_ids[tile_id] = {'row': row, 'col': col}
print(tile_ids)

# For trial purposes set tile id:
tile_id = tile_ids['6214_576']

# Determine rows and colums to load this results in a 3 x 3 window
rows_to_load = [tile_id['row'] - 1, tile_id['row'], tile_id['row'] + 1]
cols_to_load = [tile_id['col'] - 1, tile_id['col'], tile_id['col'] + 1]
# create list of tile_ids for tiles to load
tiles_to_load = []
for row in rows_to_load:
    for col in cols_to_load:
        tile_id = str(row) + '_' + str(col)
        tiles_to_load.extend([tile_id])
print tiles_to_load

