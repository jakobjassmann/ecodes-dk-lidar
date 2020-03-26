REM Batch script to prepare working environment for the DK nationwide LiDAR processing
REM Jakob Assmann j.assmann@bios.au.dk 16 January 2020

REM Set extensions and expansion
SETLOCAL EnapleExtensions 
SETLOCAL EnableDelayedExpansion


REM Copy files from server:
robocopy /MIR O:\ST_Ecoinformatics\B_Read\Denmark\Elevation\GST_2014\Punktsky\laz ..\data\laz\
robocopy /MIR O:\ST_Ecoinformatics\B_Read\Denmark\Elevation\GST_2014\DTM_tif ..\data\dtm\

REM Create MD5 checksums for pointcloud files
for %%f in (..\data\laz\*.laz) do (
	certutil -hashfile %%f MD5 | findstr /i [0-9a-f][0-9a-f].[0-9a-f][0-9a-f].[0-9a-f][0-9a-f] > temp.md5
	set /p MD5=<temp.md5
	set MD5=!MD5: =!
	echo !MD5! > %%f.local_md5
	del temp.md5
)

REM Create MD5 checksums for DTM rasters
for %%f in (..\data\dtm\*.tif) do (
	certutil -hashfile %%f MD5 | findstr /i [0-9a-f][0-9a-f].[0-9a-f][0-9a-f].[0-9a-f][0-9a-f] > temp.md5
	set /p MD5=<temp.md5
	set MD5=!MD5: =!
	echo !MD5! > %%f.local_md5
	del temp.md5
)

REM Next run python script (checksum_qa.py) to verify checksum accuracy.
REM End of File 
