#!/usr/bin/env python
# -*- coding: utf-8 -*-
# USPTO Bulk Data Parser
# Description: Check README.md for instructions on seting up the paser with configuration settings.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# Import Python modules
import time
import os
import sys
import multiprocessing
import traceback
import string
import psutil

# Import USPTO Parser Functions
import USPTOLogger
import SQLProcessor
import USPTOSanitizer
import USPTOProcessLinks
import USPTOCSVHandler
import USPTOProcessAPSGrant
import USPTOProcessXMLGrant
import USPTOProcessXMLApplication
import USPTOExtractXML4Grant
import USPTOExtractXML2Grant
import USPTOExtractXML4Application
import USPTOExtractXML1Application
import USPTOStoreGrantData
import USPTOStoreApplicationData

# Prints the ASCII header of the USPTO application
def print_ascii_header():
    print("""

UUUUUUUU     UUUUUUUU   SSSSSSSSSSSSSSS PPPPPPPPPPPPPPPPP   TTTTTTTTTTTTTTTTTTTTTTT     OOOOOOOOO
U::::::U     U::::::U SS:::::::::::::::SP::::::::::::::::P  T:::::::::::::::::::::T   OO:::::::::OO
U::::::U     U::::::US:::::SSSSSS::::::SP::::::PPPPPP:::::P T:::::::::::::::::::::T OO:::::::::::::OO
UU:::::U     U:::::UUS:::::S     SSSSSSSPP:::::P     P:::::PT:::::TT:::::::TT:::::TO:::::::OOO:::::::O
 U:::::U     U:::::U S:::::S              P::::P     P:::::PTTTTTT  T:::::T  TTTTTTO::::::O   O::::::O
 U:::::D     D:::::U S:::::S              P::::P     P:::::P        T:::::T        O:::::O     O:::::O
 U:::::D     D:::::U  S::::SSSS           P::::PPPPPP:::::P         T:::::T        O:::::O     O:::::O
 U:::::D     D:::::U   SS::::::SSSSS      P:::::::::::::PP          T:::::T        O:::::O     O:::::O
 U:::::D     D:::::U     SSS::::::::SS    P::::PPPPPPPPP            T:::::T        O:::::O     O:::::O
 U:::::D     D:::::U        SSSSSS::::S   P::::P                    T:::::T        O:::::O     O:::::O
 U:::::D     D:::::U             S:::::S  P::::P                    T:::::T        O:::::O     O:::::O
 U::::::U   U::::::U             S:::::S  P::::P                    T:::::T        O::::::O   O::::::O
 U:::::::UUU:::::::U SSSSSSS     S:::::SPP::::::PP                TT:::::::TT      O:::::::OOO:::::::O
  UU:::::::::::::UU  S::::::SSSSSS:::::SP::::::::P                T:::::::::T       OO:::::::::::::OO
    UU:::::::::UU    S:::::::::::::::SS P::::::::P                T:::::::::T         OO:::::::::OO
      UUUUUUUUU       SSSSSSSSSSSSSSS   PPPPPPPPPP                TTTTTTTTTTT           OOOOOOOOO

USPTO Bulk-Data Parser by Ripple Software Consulting - joseph@ripplesoftware.ca\n\n""")

def start_thread_processes(links_array, args_array, database_args):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Define array to hold processes to multithread
    processes = []

    # Calculate the total length of all links to collect
    total_links_count = len(links_array['grants']) + len(links_array['applications']) + len(links_array['classifications']) + + len(links_array['PAIR'])
    # Define how many threads should be started
    try:
        # If number_of_threads is set in args
        if "number_of_threads" in args_array["command_args"]:
            # Set number_of_threads appropriately
            # If requesting more threads than number of links to grab
            if int(args_array["command_args"]['number_of_threads']) > total_links_count:
                # Set number of threads at number of links
                number_of_threads = total_links_count
            # If number of threads acceptable
            else:
                # Set to command args number of threads
                number_of_threads = int(args_array["command_args"]['number_of_threads'])
        else:
            number_of_threads = args_array['default_threads']
    except Exception as e:
        # If there is a problem creating the number of threads set again and log the error
        number_of_threads = 10
        print("Calculating number of threads failed... ")
        traceback.print_exc()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

    # Create a Queue to hold link pile and share between threads
    link_queue = multiprocessing.Queue()
    # Put all the links into the queue
    #TODO write classification parser and also append to queue
    for link in links_array['classifications']:
        link.append("class")
        link_queue.put(link)
    for link in links_array['grants']:
        link.append("grant")
        link_queue.put(link)
    for link in links_array['applications']:
        link.append("application")
        link_queue.put(link)
    for link in links_array['PAIR']:
        link.append("PAIR")
        link_queue.put(link)
    for link in links_array['legal']:
        link.append("legal")
        link_queue.put(link)

    print("Starting " + str(number_of_threads) + " process(es)... ")
    logger.info("Starting " + str(number_of_threads) + " process(es)... ")

    # Loop for number_of_threads and append threads to process
    for i in range(number_of_threads):
        # Set an argument to hold the thread number for spooling up downloads.
        # Create a thread and append to list
        processes.append(multiprocessing.Process(target=main_process, args=(link_queue, args_array, database_args, i)))

    # Append the load balancer thread once to the loop
    processes.append(multiprocessing.Process(target=load_balancer_thread, args=(link_queue, args_array)))

    # Loop through and start all processes
    for p in processes:
        p.start()

    print("All " + str(number_of_threads) + " initial main process(es) have been loaded... ")
    logger.info("All " + str(number_of_threads) + " initial main process(es) have been loaded... ")

    # This .join() function prevents the script from progressing further.
    for p in processes:
        p.join()

# Main function for multiprocessing
def main_process(link_queue, args_array, database_args, spooling_value):

    # Set process start time
    process_start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Check the spooling value in args_array and set a wait time
    args_array['spooling_value'] = spooling_value
    if args_array['spooling_value'] > 4:
        print('[Sleeping thread for initial spooling thread number ' + str(spooling_value) + '...]')
        logger.info('Sleeping thread for initial spooling thread number ' + str(spooling_value) + '...')
        time.sleep((args_array['spooling_value']) * args_array['thread_spool_delay'])
        print('[Thread number ' + str(spooling_value) + ' is waking from sleep...]')
        logger.info('Thread number ' + str(spooling_value) + ' is waking from sleep...')

        args_array['spooling_value'] = 0

    print('Process {0} is starting to work! Start Time: {1}'.format(os.getpid(), time.strftime("%c")))

    # Create the database connection here so that each process uses its own connection,
    # hopefully to increase the bandwith to the database.
    if "database" in args_array["command_args"]:
        # Create a database connection for each thread processes
        database_connection = SQLProcessor.SQLProcess(database_args)
        database_connection.connect()
        args_array['database_connection'] = database_connection

    # Go through each link in the array passed in.
    while not link_queue.empty():

        # Set process time
        start_time = time.time()

        # Get the next item in the queue
        item = link_queue.get()
        # Separate link item into link and file_type and append to args_array for item
        args_array['url_link'] = item[0]
        args_array['uspto_xml_format'] = item[1]
        args_array['document_type'] = item[3]
        # File_name is used to keep track of the .zip base filename
        args_array['file_name'] = os.path.basename(args_array['url_link']).replace(".zip", "").replace(".csv", "").replace(".txt", "")

        print("Processing " + args_array['uspto_xml_format'] + " file: " + args_array['url_link'] + " Started at: " + time.strftime("%c"))

        # If using `each` database insertion check if the args_array['file_name']
        # has previously been partially processed.
        # If it has, then remove all records from the previous partial processing.
        # If it has not, then insert into STARTED_FILES as having been started.
        if "database" in args_array['command_args'] and args_array['database_insert_mode'] != "bulk":
            database_connection.remove_previous_file_records(args_array['document_type'], args_array['file_name'])

        # Call the function to collect patent data from each link
        # and store it to specified place (csv and/or database)
        try:
            USPTOProcessLinks.process_link_file(args_array)
            # Print and log notification that one .zip package is finished
            print('[Finished processing one .zip package! Time consuming:{0} Time Finished: {1}]'.format(time.time() - start_time, time.strftime("%c")))
            logger.info('Finished processing one .zip package! Time consuming:{0} Time Finished: {1}]'.format(time.time() - start_time, time.strftime("%c")))

        except Exception as e:
            # Print and log general fail comment
            print("Processing a file failed... " + args_array['file_name'] + " from link " + args_array['url_link'] + " at: " + time.strftime("%c"))
            logger.error("Processing a file failed... " + args_array['file_name'] + " from link " + args_array['url_link'])
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())


    # TODO: check for unprocessed (will have to add "processing" flag.) and add a check before starting
    # processing to avoid collisions of link piles.  Make link_pile loop into a function and
    # then call it again.  OR... make link pile a super global, and somehow be able to check against
    # other processes and rebalance and pop off from link piles.

    # Print message that process is finished
    print('[Process {0} is finished. Time consuming:{1} Time Finished: {1}]'.format(time.time() - process_start_time, time.strftime("%c")))


# Spool down the thread balance when load is too high
def spool_down_load_balance():

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")
    print("[Calculating load balancing proccess... ]")
    logger.info("[Calculating load balacing process... ]")

    # Get the count of CPU cores
    try:
        core_count = psutil.cpu_count()
    except Exception as e:
        core_count = 4
        print("Number of CPU cores could not be detected. Setting number of CPU cores to 4")
        logger.info("Number of CPU cores could not be detected. Setting number of CPU cores to 4")
        traceback.print_exc()

    # Set flag to keep loop running
    # TODO should I use a break here
    immediate_load_too_high = True
    load_check_count = 1

    # Loop while load balance is too high
    while immediate_load_too_high is True:
        # Calulate the immediate short term load balance of last minute average
        one_minute_load_average = os.getloadavg()[0] / core_count
        # If load balance is too high sleep process and print msg to stdout and log
        if one_minute_load_average > 2:
            print("Unacceptable load balance detected. Process " + os.getpid() + " taking a break...")
            logger.info("Unacceptable load balance detected. Process " + os.getpid() + " taking a break...")
            load_check_count = load_check_count + 1
            time.sleep(30)
        # Else if the thread had been sleeping for 5 minutes, start again
        elif load_check_count >= 10:
            immediate_load_too_high = False
        # If load balance is OK, then keep going
        else:
            immediate_load_too_high = False

# Load balancer thread function
def load_balancer_thread(link_queue, args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Print to stdout and log that load balancing process starting
    # Check if CPU load is set to be balanced
    if "balance" in args_array['command_args']:
        print("[Starting load balancing proccess... ]")
        logger.info("Starting load balancing process...")
    else:
        print("[Load balancing inactive... ]")
        logger.info("Load balancing inactive...")

    # Get the count of CPU cores
    try:
        core_count = psutil.cpu_count()
        print(str(core_count) + " CPU cores were detected...")
        logger.info(str(core_count) + " CPU cores were detected...")
    except Exception as e:
        core_count = 4
        print("Number of CPU cores could not be detected. Setting number of CPU cores to 4")
        logger.info("Number of CPU cores could not be detected. Setting number of CPU cores to 4")
        traceback.print_exc()

    # While there is still links in queue
    while not link_queue.empty():
        # Sleep the balancer for 5 minutes to allow initial threads and CPU load to balance
        time.sleep(300)
        # Check the 5 minute average CPU load balance
        five_minute_load_average = os.getloadavg()[1] / core_count

        # Check if CPU load is set to be balanced
        if "balance" in args_array['command_args']:
            # If the load average is very small, start a group of new threads
            if five_minute_load_average < args_array['target_load_float']:
                # Print message and log that load balancer is starting another thread
                print("Starting another thread group due to low CPU load balance of: " + str(five_minute_load_average * 100) + "%")
                logger.info("Starting another thread group due to low CPU load balance of: " + str(five_minute_load_average * 100) + "%")
                # Start another group of threads and pass in i to stagger the downloads
                # TODO: calculate the number of new threads to start
                for i in range(1):
                    start_new_thread = multiprocessing.Process(target=main_process,args=(link_queue, args_array, i))
                    start_new_thread.start()
                    time.sleep(2)

            # If load average less than 1 start single thread
            elif five_minute_load_average < 1:
                print("Starting another single thread due to low CPU load balance of: " + str(five_minute_load_average * 100) + "%")
                logger.info("Starting another single thread due to low CPU load balance of: " + str(five_minute_load_average * 100) + "%")
                # Start another thread and pass in 0 to start right away
                start_new_thread = multiprocessing.Process(target=main_process,args=(link_queue, args_array, 1))
                start_new_thread.start()

        else:
            print("Reporting CPU load balance: " + str(five_minute_load_average * 100) + "%")
            logger.info("Reporting CPU load balance: " + str(five_minute_load_average * 100) + "%")

# Check existing app structure and create it if required
def validate_existing_file_structure(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    try:
        # Check that the structure required for the app to function are in place
        # If not then create directory structure
        for required_directory in args_array['required_directory_array']:
            if not os.path.exists(args_array['working_directory'] + required_directory):
                os.makedirs(args_array['working_directory'] + required_directory)

        # Create the log file lock and set to open.
        log_lock = open(log_lock_file, "w")
        log_lock.write("0")
        log_lock.close()

        print("Finished creating required directory structure " + time.strftime("%c"))
        logger.info('Finished creating required directory structure ' + time.strftime("%c"))

        # Return `True` that file structure has been created
        return True

    except Exception as e:
        # Log finished building all zip filepaths
        print("Failed to create require directory structure " + time.strftime("%c"))
        traceback.print_exc()
        logger.error('Failed to create require directory structure ' + time.strftime("%c"))
        # Log exception error messages
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(str(e) + str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        # Return false to main function
        return False


# Parses the command argument sys.arg into command set, also encrypt password for use
def build_command_arguments(argument_array, args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    try:
        # Create an array to store modified command line arguemnts
        command_args = {}

        # Pop off the first element of array because it's the application filename
        argument_array.pop(0)

        # For loop to modify elements and strip "-" and check if arguement expected
        for i in range(len(argument_array)):
            skip = 0
            if skip + i == len(argument_array):
                break
            if argument_array[i] in args_array['allowed_args_array']:
                # Check for help menu requested
                if argument_array[i] == "-h" or argument_array[i] == "-help":
                    # Print out full argument help menu
                    print(build_argument_output())
                    exit()
                elif argument_array[i] == "-t":
                    # Check that next argument is integer between 0 and 20
                    if int(argument_array[i + 1]) > 0 and int(argument_array[i + 1]) < 31:
                        command_args['number_of_threads'] = argument_array[i + 1]
                        # Pop the value off
                        argument_array.pop(i + 1)
                        # Increment i to avoid the number of threads value
                        skip = skip + 1
                    # If the argument for number_of_threads is invalid return error
                    else:
                        # Argument length is not ok, print message and return False
                        print("Command argument error [illegal number of threads]....")
                        # Print out full argument help menu
                        print(build_argument_output())
                        exit()
                # If command to select bibliographic or full-text source
                elif argument_array[i] == "-biblio":
                    command_args['source_type'] = "biblio"
                elif argument_array[i] == "-full":
                    command_args['source_type'] = "full"
                else:
                    # If the argument is expected but not requiring a second
                    # setting argument append as key to command_args
                    command_args[argument_array[i].replace('-', '')] = True
            else:
                # Argument is not expected, print message and return False
                print("Command argument error [illegal argument]....")
                # Print out full argument help menu
                print(build_argument_output())
                exit()

        # Finally correct that number_of_threads value is definitely in the array
        if "number_of_threads" not in command_args:
            command_args['number_of_threads'] = args_array['default_threads']

        # If source_type was not specificed, then set to the default value
        if "source_type" not in command_args:
            command_args['source_type'] = args_array['default_source_type']

        # If arguments passed then return array of arguments
        return command_args

    except Exception as e:
        print('Failed to build command arguments: ')
        traceback.print_exc()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # Log error with creating filepath
        logger.error('Failed to build command arguments: ' + str(e) + str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        return False

def build_argument_output():

    # Print the ASCII header
    print_ascii_header()

    # Build the command line output
    argument_output = "\nUsage : USPTOParser.py [-t [int]] & [-csv, &| -database] | [-update]\n\n"
    # Add the description of how to run the parser
    argument_output += "USPTOParser.py requires data destination (-csv, -database) when running for the first time. \n"
    argument_output += "Database credentials are defined in the main function.\n"
    argument_output += "After the script has been run the first time, use the -update flag.\n"
    # Add a list of arguments that are accepted
    argument_output += "\nArgument flags:\n\n"
    argument_output += "-h, -help   : print help menu.\n"
    argument_output += "-t [int]    : set the number of threads.  Must be 1-20 default = 10.\n"
    argument_output += "-balance    : if set turns on CPU load balancer.\n"
    argument_output += "-csv        : write the patent data files to csv.  Setting will be saved and used on update or restart.\n"
    argument_output += "-database   : write the patent data to database.  Setting will be saved on update or restart.\n"
    argument_output += "-biblio     : (default) parse the USPTO bulk-data Red Book Biliographic data-set.\n"
    argument_output += "-full       : parse the USPTO bulk-data Red Book full-text data-set.\n"
    argument_output += "-update     : check for new patent bulk data files and process them\n"
    return argument_output

# Set the config settings in file based on command arguments
def set_config_using_command_args(args_array):
    # User wants to update but but no data destination specified,

    # Set the sandbox mode if in command args
    if 'sandbox' in args_array['command_args']:
        args_array['sandbox'] = True

    # Collect previous configuration settings
    if "update" in args_array['command_args']:
        # Check for previous settings
        #if "csv" not in args_array['command_args'] and "database" not in args_array['command_args']:
        config_settings = open(args_array['app_config_file'], "r")
        for line in config_settings.readlines():
            line = line.strip()
            print("Previous setting: " + str(line.strip()) + " found...")
            # Catch the settigs for source_type
            if line == "biblio" or line == "full":
                args_array['command_args']['source_type'] = line
            else:
                args_array['command_args'][line] = True
        config_settings.close()

    # If command line args include data destination, then write to file
    if "csv" in args_array['command_args'] or "database" in args_array['command_args'] or "source_type" in args_array['command_args']:
        config_settings = open(args_array['app_config_file'], "w")
        for argument, value in args_array['command_args'].items():
            if argument == "source_type":
                config_settings.write(value + "\n")
            # Do not write update command to the file
            elif argument != "update":
                config_settings.write(argument + "\n")
        config_settings.close()

    # Return the modified args_array
    return args_array

# Handles the closing of the application
def handle_application_close(start_time, all_files_processed, args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Close the database connection if opened
    if "database" in args_array['command_args']:
        if "database_connection" in args_array:
            args_array['database_connection'].close()

    # Print final completed message to stdout
    if all_files_processed == True:
        # Print final completed message to stdout
        print(('[All USPTO files have been processed Time consuming:{0} Time Finished: {1}'.format(time.time()-start_time, time.strftime("%c"))))
        logger.info('All USPTO files have been processed.Time consuming:{0} Time Finished: {1}'.format(time.time()-start_time, time.strftime("%c")))
    else:
        # Print final error message to stdout
        print(('There was an error attempting to proccess the files. Check log for details. Time consuming:{0} Time Finished: {1}'.format(time.time()-start_time, time.strftime("%c"))))
        logger.info('There was an error attempting to proccess the files. Check log for details. Time consuming:{0} Time Finished: {1}'.format(time.time()-start_time, time.strftime("%c")))

# MAIN FUNCTON
# The Main function defines required variables such as filepaths, and arguments to be passed through functions
# The workflow of the main function is as follows:
# (1) Setup Logger
# (2) Parse and validate command line arguments
# (3) Collect previous configuration settings
# (4) Check for existing and if nessesary build required directory and file structure for the app
# (5) Check for existing data, look for log files and parse into workflow
# (6) Collect links if needed or look for new links if `-update` argument flag is set


if __name__=="__main__":

    # If running sandbox mode or not
    # Sandbox mode will keep all downloaded data files locally to
    # prevent having to download them multiple times, this can be
    # set from the command line argument '-sandbox'
    sandbox = False
    # Log levels
    log_level = 1 # Log levels 1 = error, 2 = warning, 3 = info
    stdout_level = 1 # Stdout levels 1 = verbose, 0 = non-verbose

    # Declare variables
    start_time=time.time()
    working_directory = os.getcwd()
    allowed_args_array = [
        "-csv", "-database", "-update", "-t",
        "-biblio", "-full",
        "-balance", "-sandbox", "-h", "-help"
    ]
    default_threads = 5
    database_insert_mode = "bulk" # values include `each` and `bulk`

    # Declare filepaths
    app_temp_dirpath = working_directory + "/TMP/"
    #app_temp_dirpath = "/Volumes/Thar/uspto/TMP/downloads"
    app_csv_dirpath = working_directory + "/CSV/"
    app_log_file = working_directory + "/LOG/USPTO_app.log"
    app_config_file = working_directory + "/.USPTO_config.cnf"
    log_lock_file = working_directory + "/LOG/.logfile.lock"
    grant_process_log_file = working_directory + "/LOG/grant_links.log"
    application_process_log_file = working_directory + "/LOG/application_links.log"
    application_pair_process_log_file = working_directory + "/LOG/application_pair_links.log"
    pair_process_log_file = working_directory + "/LOG/pair_links.log"
    legal_process_log_file = working_directory + "/LOG/legal_links.log"
    classification_process_log_file = working_directory + "/LOG/class_links.log"
    us_classification_text_filename = working_directory + "/installation/CLS/usclass.txt"
    cpc_classification_text_filename = working_directory + "/installation/CLS/cpcclass.csv"
    mysql_database_reset_filename = working_directory + "/installation/uspto_create_database_mysql.sql"
    postgresql_database_reset_filename = working_directory + "/installation/uspto_create_database_postgres.sql"
    sandbox_downloads_dirpath = working_directory + "/TMP/downloads/"
    #sandbox_downloads_dirpath = "/Volumes/Thar/uspto/TMP/downloads/"

    # Database args
    database_args = {
        #"database_type" : "postgresql", # choose 'mysql' or 'postgresql'
        "database_type" : "mysql", # choose 'mysql' or 'postgresql'
        "host" : "127.0.0.1",
        #"port" : 5432, # PostgreSQL port
        "port" : 3306, # MySQL port
        "user" : "uspto",
        #"passwd" : "Ld58KimTi06v2PnlXTFuLG4", # PostgreSQL password
        "passwd" : "R5wM9N5qCEU3an#&rku8mxrVBuF@ur", # MySQL password
        "db" : "uspto",
        "charset" : "utf8"
    }

    # Used to create all required directories when application starts
    required_directory_array = [
        "/CSV/CSV_A",
        "/CSV/CSV_G",
        "/CSV/CSV_P",
        "/CSV/CSV_C",
        "/CSV/CSV_L",
        "/LOG",
        "/TMP",
        "/TMP/downloads",
        "/TMP/unzip"
        ]

    # Create an array of args that can be passed as a group
    # and appended to as needed
    args_array = {
        "bulk_data_source" : "uspto", # uspto or reedtech
        "uspto_bulk_data_url" : 'https://bulkdata.uspto.gov/',
        "reedtech_bulk_data_url" : "https://patents.reedtech.com/",
        "uspto_classification_data_url" : 'https://www.uspto.gov/web/patents/classification/selectnumwithtitle.htm',
        "uspto_PAIR_data_url" : "https://bulkdata.uspto.gov/data/patent/pair/economics/2017/",
        "uspto_legal_data_url" : "https://bulkdata.uspto.gov/data/patent/litigation/2016/",
        "sandbox" : sandbox,
        "log_level" : log_level,
        "stdout_level" : stdout_level,
        "working_directory" : working_directory,
        "default_threads" : default_threads,
        'default_source_type' : "biblio",
        "target_load_float" : 0.75,
        "thread_spool_delay" : 3600,
        "database_type" : database_args['database_type'],
        "database_args" : database_args,
        "database_insert_mode" : database_insert_mode,
        "required_directory_array" : required_directory_array,
        "app_config_file" : app_config_file,
        "allowed_args_array" : allowed_args_array,
        "log_lock_file" : log_lock_file,
        "classification_process_log_file" : classification_process_log_file,
        "us_classification_text_filename" : us_classification_text_filename,
        "cpc_classification_text_filename" : cpc_classification_text_filename,
        "grant_process_log_file" : grant_process_log_file,
        "application_process_log_file" : application_process_log_file,
        "application_pair_process_log_file" : application_pair_process_log_file,
        "legal_process_log_file" : legal_process_log_file,
        "pair_process_log_file" : pair_process_log_file,
        "temp_directory" : app_temp_dirpath,
        "csv_directory" : app_csv_dirpath,
        "sandbox_downloads_dirpath" : sandbox_downloads_dirpath
    }

    # Setup logger
    USPTOLogger.setup_logger(args_array['log_level'], app_log_file)
    # Include logger in the main function
    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Perform analysis of command line args and store in args_array
    args_array["command_args"] = build_command_arguments(sys.argv, args_array)

    # If command_args are checked OK! Start app
    if args_array["command_args"]:

        # Print the ASCII header
        print_ascii_header()

        # Set saved app configuration based on current command arguments
        # and collect existing config settings from file and append to args_array
        args_array = set_config_using_command_args(args_array)

        logger.info('Starting USPTO Patent Database Builder ' + time.strftime("%c"))
        print("Starting USPTO Patent Database Builder " + time.strftime("%c"))

        # Check existing app structure and create it if required
        # If true then coninue app process
        if validate_existing_file_structure(args_array):

            # Collect all links, or update with new links to log files
            USPTOLogger.build_or_update_link_files(args_array)

            # Main loop that checks if all links have been processed.
            # Read the list of files to process and eliminate the ones
            # that are marked as processed.
            all_files_processed = False
            while all_files_processed == False:

                # Read list of all required files into array from log files
                # An array is returned with list of links for each type of data to processs
                # (1) Patent Classification Data
                # (2) Patent Grant Documents
                # (3) Application Documents
                # (4) PAIR Data
                # (5) Patent Legal Case Data

                # Collect all links by passing in log files
                # TODO: add classification parsing and PAIR link processing
                all_links_array = USPTOLogger.collect_all_unstarted_links_from_file(args_array)

                # If collecting the links array failed print error and log error
                if not all_links_array:
                    print('Failed to collect links from file ' + time.strftime("%c"))
                    logger.error('Failed to collect links from file ' + time.strftime("%c"))
                    # Set the main loop to exit
                    all_files_processed = "Error"

                # Else if the read list of unprocessed links is not empty
                elif len(all_links_array["grants"]) != 0 or len(all_links_array["applications"]) != 0 or len(all_links_array["PAIR"]) != 0 or len(all_links_array["classifications"]) != 0 or len(all_links_array["legal"]) != 0:
                    # TODO update with classifcation data and PAIR data output
                    print(str(len(all_links_array["grants"])) + " grant links will be collected. Start time: " + time.strftime("%c"))
                    print(str(len(all_links_array["applications"])) + " application links will be collected. Start time: " + time.strftime("%c"))
                    print(str(len(all_links_array["classifications"])) + " classification links will be collected. Start time: " + time.strftime("%c"))
                    print(str(len(all_links_array["PAIR"])) + " PAIR links will be collected. Start time: " + time.strftime("%c"))
                    print(str(len(all_links_array["legal"])) + " legal links will be collected. Start time: " + time.strftime("%c"))
                    logger.info(str(len(all_links_array["grants"])) + " grant links will be collected. Start time: " + time.strftime("%c"))
                    logger.info(str(len(all_links_array["applications"])) + " application links will be collected. Start time: " + time.strftime("%c"))
                    logger.info(str(len(all_links_array["classifications"])) + " classification links will be collected. Start time: " + time.strftime("%c"))
                    logger.info(str(len(all_links_array["PAIR"])) + " PAIR links will be collected. Start time: " + time.strftime("%c"))
                    logger.info(str(len(all_links_array["legal"])) + " legal links will be collected. Start time: " + time.strftime("%c"))

                    # Start the threading processes for the stack of links to process
                    start_thread_processes(all_links_array, args_array, database_args)

                # If both link lists are empty then all files have been processed, set main loop to exit
                else:
                    all_files_processed = True

            # Handle the closing of the application
            handle_application_close(start_time, all_files_processed, args_array)
