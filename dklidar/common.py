### Common module for the dklidar reporcessing - general functions likely used by all scripts
### Jakob Assmann j.assmann@bios.au.dk 29 January 2019

# Imports
import settings
import os
#
def gather_logs(n_processes, global_log_file, global_opalsLog = None, global_opalsErrors = None):
    """
    Small helper to gather all logs from the parallel processes and append them to the global log file.
    :param n_processes: number of processes to search for in scratch folder
    :param global_log_file: file connection to global log_file
    :param global_opalsLog: file connection to global opalsLog file (default = None)
    :param global_opalsErrors: file connection to global opalsErrors file (default = None)
    :return: Nothing.
    """
    for pid in range(1, n_processes):
        # Check whether log file exists
        # Generate string to temp folder of process
        temp_folder = settings.scratch_folder + '/temp_' + str(pid)
        if os.path.exists(temp_folder + '/log.txt'):
            # Open connection to process log file and read
            log_file = open(temp_folder + '/log.txt', 'r')
            log_text = log_file.read()
            # Write log text to global log file
            global_log_file.write('\n\n!!! SOF Log for pid ' + str(pid) + ':\n' +
                              log_text +
                              '\n\n!!! EOF Log for pid ' + str(pid) + '.\n')
            # Close process log file
            log_file.close()
            # Remove temporary log file for process
            os.remove(temp_folder + '/log.txt')
        else:
            # Write log text to global log file
            global_log_file.write('\n\n!!! SOF Log for pid ' + str(pid) + ':\n' +
                              'File does not exists.' +
                              '\n\n!!! EOF Log for pid ' + str(pid) + '.\n')

        # Check whether opalsLog file connection was supplied
        if not global_opalsLog is None:
            if os.path.exists(temp_folder + '/opalsLog.xml'):
                # Open connection to process Log file and read
                opalsLog_file = open(temp_folder + '/opalsLog.xml', 'r')
                opalsLog_text = opalsLog_file.read()
                # Write log text to global log file
                global_opalsLog.write('\n\n!!! SOF opalsLog.xml for pid ' + str(pid) + ':\n' +
                                  opalsLog_text +
                                  '\n\n!!! EOF opalsLog.xmlo for pid ' + str(pid) + '.\n')
                # Close process opalsLog file
                opalsLog_file.close()

                # Remove temporary log file for process
                os.remove(temp_folder + '/opalsLog.xml')
            else:
                # Write log text to global log file
                global_log_file.write('\n\n!!! SOF opalsLog.xml for pid ' + str(pid) + ':\n' +
                                'File does not exists.' +
                                '\n\n!!! EOF opalsLog.xml for pid ' + str(pid) + '.\n')

        # Check whether opalsError file connection was supplied

        if not global_opalsLog is None:
            if os.path.exists(temp_folder + '/opalsLog.xml'):
                # Open connection to process Log file and read
                opalsErrors_file = open(temp_folder + '/opalsErrors.txt', 'r')
                opalsErrors_text = opalsErrors_file.read()
                # Write log text to global log file
                global_opalsErrors.write('\n\n!!! SOF opalsErrors for pid ' + str(pid) + ':\n' +
                                     opalsErrors_text +
                                     '\n\n!!! EOF opalsErros for pid ' + str(pid) + '.\n')
                # Close process opalsLog file
                opalsErrors_file.close()

                # Remove temporary log file for process
                os.remove(temp_folder + '/opalsErrors.txt')
            else:
                # Write log text to global log file
                global_log_file.write('\n\n!!! SOF opalsErrors.txt for pid ' + str(pid) + ':\n' +
                                      'File does not exists.' +
                                      '\n\n!!! EOF opalsErrors.txt for pid ' + str(pid) + '.\n')