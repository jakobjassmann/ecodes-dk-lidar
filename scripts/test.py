import opals

opals.loadAllModules()

dm = opals.pyDM.Datamanager.load('D:\Jakob\dk_nationwide_lidar\data\sample\odm\odm_6210_570.odm')

lf = opals.pyDM.AddInfoLayoutFactory()
lf.addColumn(dm, "PointSourceId", True)
layout = lf.getLayout()

histograms_set = dm.getHistogramSet(layout)
point_source_ids = []
for histo in histograms_set.histograms():
    print(histo)
    for value in histo.values():
        point_source_ids.append(value)

print('-' * 80)

print point_source_ids