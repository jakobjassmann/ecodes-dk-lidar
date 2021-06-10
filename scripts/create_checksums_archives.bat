@echo off
REM DK nationwide LiDAR script to create local MD5 checksums for all laz and md5 files after downloading.
REM Jakob Assmann j.assmann@bios.au.dk 20 April 2019

REM Note: change folder destinations accrodingly

setlocal ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS

echo. 
echo --------------------------------------------------------------------------------
echo DK LiDAR: Calculating checksums for archived and compressed outputs. 
echo. 

REM Create MD5 checksums for pointcloud files

echo Calculating checksums for archives...
for %%f in (D:\Jakob\dk_nationwide_lidar\data\zipped_outputs\*.tar.bz2) do (
	echo %%f
	certutil -hashfile %%f MD5 | findstr /i [0-9a-f][0-9a-f].[0-9a-f][0-9a-f].[0-9a-f][0-9a-f] > temp.md5
	set /p MD5=<temp.md5
	set MD5=!MD5: =!
	echo %%F !MD5! >> D:\Jakob\dk_nationwide_lidar\data\zipped_outputs\checksums.md5
	del temp.md5
)
echo done.
echo.

echo.
echo Finished checksum calculation.