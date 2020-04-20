@echo off

REM Quick script to kill all python processes to halt DK nationwide LiDAR processing 
REM with the process_tiles.py script.
REM Jakob Assmann j.assmann@bios.au.dk 20 April 2020

echo. 
echo --------------------------------------------------------------------------------
echo DK Lidar: Helper script to halt processing of process_tiles.py
echo. 
echo WARNING: This will kill ALL active Python processes owned by the user,
echo          including all non-DK lidar Python processes! 
echo.
echo Proceed [y/n]?
set /p car=
if %car% == y goto kill
if %car% == n goto skip
:kill
echo Terminating all python.exe processsess... 
taskkill /IM "python.exe" /F
echo done.
goto:eof
:skip
echo User interruption. Killing no processes, exiting script.
