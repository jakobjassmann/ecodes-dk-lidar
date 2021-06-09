import multiprocessing
import pandas
import subprocess
import re
import datetime
import os
import opals
from dklidar import settings

# initate opals
opals.loadAllModules()

# make folder for temp odms
os.mkdir('temp_odms')
os.chdir('temp_odms')

# load missing tiles
missing_dtms = pandas.read_csv(settings.dtm_folder + '../missing_dtm_tile_ids.csv')['tile_id'].tolist()

print('Generating dems for ' + str(len(missing_dtms)) + ' tiles...')

for tile_id in missing_dtms:
    os.mkdir(tile_id)
    os.chdir(tile_id)

    laz_file = settings.laz_folder + '/PUNKTSKY_1km_' + tile_id + '.laz'
    odm_file = tile_id + '_temp.odm'
    dtm_file = settings.dtm_folder + '/DTM_1km_' + tile_id

    # 1) Import tile into temporary odm
    try:
        import_tile = opals.Import.Import()
        import_tile.inFile = laz_file
        import_tile.outFile = odm_file
        import_tile.commons.screenLogLevel = opals.Types.LogLevel.none
        import_tile.run()
        print('Imported ' + tile_id + '. '),
    except:
        print('Unable to import ' + tile_id + '.'),

    #1) Validate CRS
    try:
        odm_dm = opals.pyDM.Datamanager.load(odm_file)
        crs_str = odm_dm.getCRS()
        # Check whether CRS exists, if not assign, if different throw error.
        if crs_str == settings.crs_wkt_opals:
            print ('crs: match. '),
        elif crs_str == '':
            odm_dm.setCRS(settings.crs_wkt_opals)
            print('crs: empty - set. '),
        else:
            print('crs: warning - no match. '),
        odm_dm = None  # This is needed as opals locks the file connection otherwise.
    except:
        print('crs validation error. '),

    #2) Generate DEM
    # Section adapted from Jesper Moeslunds code in ALS Calculator.py
    # ---
    try:
        dtm_export = opals.DTM.DTM()
        dtm_export.inFile = odm_file
        dtm_export.feature = opals.Types.GridFeature.sigmaz
        dtm_export.outFile = dtm_file
        dtm_export.gridSize = 0.4
        dtm_export.filter = "Generic[Classification == 2]"
        dtm_export.multiBand = False
        dtm_export.neighbours = 8  # recommendation by TU Wien (Markus Hollaus)
        dtm_export.searchRadius = 6  # recommendation by TU Wien (Markus Hollaus)
        dtm_export.commons.screenLogLevel = opals.Types.LogLevel.none
        dtm_export.run()
        print('dtm export success.'),
    except:
        print('dtm export failed. '),
    # ---

    # tidy up
    try:
        os.rename((dtm_file + '_dtm.tif'), (dtm_file + '.tif'))
        os.remove(dtm_file + '_sigmaz.tif')
        print('tidy up successfull')
    except:
        print('tidy up failed.')

    out_file = open(settings.laz_folder + '../missing_dtms_generated.txt', 'a+')
    out_file.write(dtm_file + '.tif\n')
    out_file.close()

    os.chdir('..')

