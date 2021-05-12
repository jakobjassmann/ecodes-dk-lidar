# Short script to generate a list of all vrt files
import glob
import re
from dklidar import settings

# list vrts
vrts = glob.glob(settings.output_folder + '*/*.vrt')
more_vrts = glob.glob(settings.output_folder + '*/*/*.vrt')
for vrt in more_vrts:
    vrts.append(vrt)

# Clean up file paths
vrts = [re.sub(settings.output_folder[0:len(settings.output_folder)-1], '', vrt) for vrt in vrts]
vrts = [re.sub('\\\\', '/', vrt) for vrt in vrts]
vrts = [re.sub('^/', '', vrt) for vrt in vrts]

# write out to file
out_file = open(settings.output_folder + '/list_of_vrts.txt', 'w')
out_file.write('\n'.join(vrts))
out_file.close()
