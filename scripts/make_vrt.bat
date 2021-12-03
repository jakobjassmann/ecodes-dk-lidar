REM quick batch script to generate a vrt file
REM generates vrt file from currentfolder with first argument as file name
REM Jakob Assmann j.assmannbios.au.dk

REM extract variable name from path in argument (if one was given)
For %%A in ("%1") do (
    Set filename=%%~nxA
)

REM make list of tif files in current folder

dir /b *.tif > list_of_files.txt

REM remember directory for return after gdbuildvrt execution
set curdir=%cd%

REM make vrt
call C:\OSGeo4W\OSGeo4W.bat gdalbuildvrt -input_file_list list_of_files.txt %filename%.vrt -te 441000 6049000 894000 6403000

REM go back and delet list of files
cd %curdir%
del "list_of_files.txt"