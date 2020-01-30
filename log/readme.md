## This folder is emtpy on prurpose!
Upon initiating the processing log files will be stored here in the following folder structure:
```
/log/                                                     log folder
    |- process_tiles/                                     subfolder log outputs for process_tiles.py
    |               |- tile_id/                           subfolder log outputs for each tile_id
    |               |         |- step X/                  subfolder log outputs for step X
    |               |         |        |- log.txt         high-level log information for step X
    |               |         |        |- opalsLOG.xml    opalsLog.xml file for step X [optional]
    |               |         |        |- opalsError.txt  opalsError.txt file for step X) [optional]
    |               |         |         
    |               |         |- step ...                 other steps
    |               |         |- status.txt               file with status summary
    |               |           
    |               |- overall_progress.csv               overall progress summary                
    |- ...                                                other log files
´´´
