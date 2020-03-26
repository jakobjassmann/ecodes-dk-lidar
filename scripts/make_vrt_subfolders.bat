REM Short script to create VRT files for all tifs in subfolders by subfolder.
REM Jakob Assmann j.assmann@bios.au.dk 25 March 2020

REM remember home directory
set back=%cd%

REM loop through subdirs execute make_vrt script, come back to home dir.
for /R /D %%i in (*) do (
cd %%i
call D:\Jakob\dk_nationwide_lidar\scripts\make_vrt.bat %%i
cd %back%
)
