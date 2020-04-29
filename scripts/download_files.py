import multiprocessing
import pandas
import subprocess
import re
import datetime
import os
from dklidar import settings

remote_url_laz = "https://download.kortforsyningen.dk/system/files/Statsaftalen/DANMARK/3_HOJDEDATA/PUNKTSKY/"
remote_url_dtm = "https://download.kortforsyningen.dk/system/files/Statsaftalen/DANMARK/3_HOJDEDATA/DTM/"

file_list_laz = 'D:/Jakob/dk_nationwide_lidar/data/file_lists_kortforsyningen/all_laz_files.csv'
file_list_dtm = 'D:/Jakob/dk_nationwide_lidar/data/file_lists_kortforsyningen/all_dtm_files.csv'

#  A cookie is needd to access the data. To generate the following curl command you can use Google Chrome.
#  First, log into the kortforsyningen website then select one tile from the laz files in the catalogues and check out
#  Open the "Mine downloads" section of the website and activate the Chrome Developer Mode by pressing "F12".
#  In the newly opened panel, select the "Network" tap and pres "crtl + R" to activate the monitoring for the website.
#  Then start the download of the file that you checked out and right-click on the associated item in the network tab.
#  Click "copy" and select "curl CMD". Then replace the following cookie string with the cookie string in
#  the copied curl command. You may have to adapt the curl command in download_file() accordingly if you change system.
cookie = 'Cookie: nmstat=1571735317171; _1d3fe=http://10.0.0.177:80; MY_SESSION=rd4o00000000000000000000ffffac1105c7o80; has_js=1; SESS1fef01291fb7205e2d46065129ba3bc3=jrFlh_HehTZC8-4x7l0loZ92TuhL0ikAewDwXNCpKiQ; downloadticket=1853700203f2d9b03cce33e4cb0c8c37'

def download_file(file_name):
    """ Wee helper function to download file from Kortforsyningen server
    :param file_name - file name on server and to be saved as
    :returns exit code of curl download command
    """
    remote_url = 'empty_url'
    local_path = '/empty_path'

    if not(re.match('.*LAZ.*', file_name) is None):
        remote_url = remote_url_laz + file_name
        local_path = settings.laz_folder + file_name
    if not (re.match('.*DTM.*', file_name) is None):
        remote_url = remote_url_dtm + file_name
        local_path = settings.dtm_folder + file_name

    curl_cmd = '"C:/Program Files/Git/mingw64/bin/curl.exe" ' + \
               '"' + remote_url + '" ' +\
               '-H "Connection: keep-alive" ' +\
               '-H "Upgrade-Insecure-Requests: 1" ' + \
               '-H "User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36" ' + \
               '-H "Sec-Fetch-Dest: iframe" ' + \
               '-H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" ' + \
               '-H "Sec-Fetch-Site: same-origin"  ' +  \
               '-H "Sec-Fetch-Mode: navigate" ' +\
               '-H "Sec-Fetch-User: ?1" ' + \
               '-H "Referer: https://download.kortforsyningen.dk/mine/downloads" ' + \
               '-H "Accept-Language: en,da-DK;q=0.9,da;q=0.8,en-US;q=0.7" ' + \
               '-H ' + '"' + cookie + '" ' +\
               '--compressed ' + \
               '--output ' + '"' + local_path + '"'

    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(curl_cmd, stdout=FNULL, stderr=subprocess.STDOUT)
        return_value = 'success'
    except subprocess.CalledProcessError as error:
        return_value = 'curl non-zero exit status: ' + str(error.returncode)
    print '.',

    return return_value

def extract_file(file_name):
    """ Wee helper function to download file from Kortforsyningen server
    :param file_name - file name on server and to be saved as
    :returns exit code of curl download command
    """
    local_path = '/empty_path'
    dest_folder = '/empty_path'

    if not(re.match('.*LAZ.*', file_name) is None):
        local_path = settings.laz_folder + file_name
        dest_folder = settings.laz_folder
    if not (re.match('.*DTM.*', file_name) is None):
        local_path = settings.dtm_folder + file_name
        dest_folder = settings.dtm_folder

    extract_cmd = '"C:/Program Files/7-Zip/7z" ' + \
                  'e ' + \
                  '-y ' + local_path + ' ' + \
                  '-o' + dest_folder

    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(extract_cmd, stdout=FNULL, stderr=subprocess.STDOUT)
        return_value = 'success'
    except subprocess.CalledProcessError as error:
        return_value = '7zip non-zero exit status: ' + str(error.returncode)
    print '.',

    return return_value

#### Main body of script
if __name__ == '__main__':

    # Start timer
    startTime = datetime.datetime.now()

    print('\n')
    print('-' * 80)
    print("DK nationwide LiDAR download script")
    print(str(startTime))

    # Load file lists as data frames:
    laz_files_df = pandas.read_csv(file_list_laz)
    dtm_files_df = pandas.read_csv(file_list_dtm)

    if not ('download' in laz_files_df): laz_files_df['download'] = 'pending'
    if not ('extraction' in laz_files_df): laz_files_df['extraction'] = 'pending'

    if not ('download' in dtm_files_df): dtm_files_df['download'] = 'pending'
    if not ('extraction' in dtm_files_df): dtm_files_df['extraction'] = 'pending'

    # Prepare download lists
    laz_files_to_download = laz_files_df['file_name'][laz_files_df['download'] != 'success'].tolist()
    dtm_files_to_download = dtm_files_df['file_name'][laz_files_df['download'] != 'success'].tolist()

    # Prep processing pool
    multiprocessing.set_executable(settings.python_exec_path)
    pool = multiprocessing.Pool(processes=4)

    # Download LAZ files
    if len(laz_files_to_download) > 0:
        print(datetime.datetime.now().strftime('%X') + ' Downloading ' +  str(len(laz_files_to_download)) + ' laz files: '),
        download_pool = pool.map_async(download_file, laz_files_to_download)
        download_pool.wait()
        laz_files_df['download'] = download_pool.get()
    else: print('No LAZ files to download.')
    print('\n')

    # Download DTM files
    if len(dtm_files_to_download) > 0:
        print(datetime.datetime.now().strftime('%X') + ' Downloading ' + str(len(dtm_files_to_download)) + ' dtm files: '),
        download_pool = pool.map_async(download_file, dtm_files_to_download)
        download_pool.wait()
        dtm_files_df['download'] = download_pool.get()
    else: print('No DTM files to download.')
    print('\n')

    # Prepare extraction lists
    laz_files_to_extract = laz_files_df['file_name'][laz_files_df['extraction'] != 'success'].tolist()
    dtm_files_to_extract = dtm_files_df['file_name'][dtm_files_df['extraction'] != 'success'].tolist()


    # # Extract LAZ files
    if len(laz_files_to_extract) > 0:
        print(datetime.datetime.now().strftime('%X') + ' Extracting ' + str(len(laz_files_to_extract)) + ' laz files: '),
        download_pool = pool.map_async(extract_file, laz_files_to_extract)
        download_pool.wait()
        laz_files_df['extraction'] = download_pool.get()
    else: print('No LAZ files to extract.')
    print('\n')

    # Extract DTM files
    if len(dtm_files_to_extract) > 0:
        print(datetime.datetime.now().strftime('%X') + ' Extracting ' + str(len(dtm_files_to_extract)) + ' dtm files: '),
        download_pool = pool.map_async(extract_file, dtm_files_to_extract)
        download_pool.wait()
        dtm_files_df['extraction'][dtm_files_df['extraction'] != 'success'] = download_pool.get()
    else: print('No LAZ files to extract.')
    print('\n')

    laz_files_df.to_csv(file_list_laz, index=False, header=True)
    dtm_files_df.to_csv(file_list_dtm, index=False, header=True)

    print('-' * 80 + '\nDone.\nTime elapsed: ' + str(datetime.datetime.now() - startTime))