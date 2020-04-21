@echo off
REM Script to batch download LAZ and DTM files for the Punktsky dataset from the Kortforsyningen website
REM Jakob Assmann j.assmann@bios.au.dk 15 April 2019

SETLOCAL EnableExtensions
SETLOCAL EnableDelayedExpansion

REM Set path variables
SET "data_path_laz=D:\Jakob\dk_nationwide_lidar\data\laz\"
SET "data_path_dtm=D:\Jakob\dk_nationwide_lidar\data\dtm\"
SET "remote_url_laz=https://download.kortforsyningen.dk/system/files/Statsaftalen/DANMARK/3_HOJDEDATA/PUNKTSKY/"
SET "remote_url_dtm=https://download.kortforsyningen.dk/system/files/Statsaftalen/DANMARK/3_HOJDEDATA/DTM/"

mkdir %data_path_laz%
mkdir %data_path_dtm%

REM download and unzip LAZ files
FOR /F %%A in (D:\Jakob\dk_nationwide_lidar\data\file_lists_kortforsyningen\all_laz_files.txt) DO (
  echo downloading %%A ... 
  REM NB: A cookie is needd to access the data. To generate the following curl command you can use Google Chrome.
  REM     First, log into the kortforsyningen website then select one tile from the laz files in the catalogues and check out
  REM     Open the "Mine downloads" section of the website and activate the Chrome Developer Mode by pressing "F12".
  REM     In the newly opened panel, select the "Network" tap and pres "crtl + R" to activate the monitoring for the website.
  REM     Then start the download of the file that you checked out and right-click on the associated item in the network tab.
  REM	  Click "copy" and select "curl CMD". Then replace the URL with "%remote_url_laz%%%A" and add '--output "%data_path_laz%%%A"'
  REM     to the end of the call. You do not have to repeat this for the dtm, the cooky / command should work for both file types.
  "C:\Program Files\Git\mingw64\bin\curl.exe" "%remote_url_laz%%%A" -H "Connection: keep-alive" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36" -H "Sec-Fetch-Dest: iframe" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" -H "Sec-Fetch-Site: same-origin" -H "Sec-Fetch-Mode: navigate" -H "Sec-Fetch-User: ?1" -H "Referer: https://download.kortforsyningen.dk/mine/downloads" -H "Accept-Language: en,da-DK;q=0.9,da;q=0.8,en-US;q=0.7" -H "Cookie: nmstat=1571735317171; _1d3fe=http://10.0.0.177:80; MY_SESSION=rd4o00000000000000000000ffffac1105c7o80; has_js=1; downloadticket=24d6755364779354323033a99b0ca109; SESS1fef01291fb7205e2d46065129ba3bc3=tEv8dRJZDLCR4NVudF7FUif3YNDs92DFruXTZ56ElKM" --compressed --output "%data_path_laz%%%A"
  "C:\Program Files\7-Zip\7z" e -y %data_path_laz%%%A -o%data_path_laz%
  del %data_path_laz%%%A
  echo %%A >> download_files.log
)

REM download and unzip DTM files
FOR /F %%A in (D:\Jakob\dk_nationwide_lidar\data\file_lists_kortforsyningen\all_dtm_files.txt) DO (
  echo downloading %%A ... 
  REM See not above on how to construct the following curl command. Here replace the URI with "%remote_url_dtm%%%A"  and
  REM add --output "%data_path_dtm%%%A to the curl command retrieved from Google Chrome. 
  "C:\Program Files\Git\mingw64\bin\curl.exe" "%remote_url_dtm%%%A" -H "Connection: keep-alive" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36" -H "Sec-Fetch-Dest: iframe" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" -H "Sec-Fetch-Site: same-origin" -H "Sec-Fetch-Mode: navigate" -H "Sec-Fetch-User: ?1" -H "Referer: https://download.kortforsyningen.dk/mine/downloads" -H "Accept-Language: en,da-DK;q=0.9,da;q=0.8,en-US;q=0.7" -H "Cookie: nmstat=1571735317171; _1d3fe=http://10.0.0.177:80; MY_SESSION=rd4o00000000000000000000ffffac1105c7o80; has_js=1; downloadticket=24d6755364779354323033a99b0ca109; SESS1fef01291fb7205e2d46065129ba3bc3=tEv8dRJZDLCR4NVudF7FUif3YNDs92DFruXTZ56ElKM" --compressed --output "%data_path_dtm%%%A"
  "C:\Program Files\7-Zip\7z" e -y %data_path_dtm%%%A -o%data_path_dtm%
  del %data_path_dtm%%%A
  echo %%A >> download_files.log
)
