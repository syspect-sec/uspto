# USPTOLogger.py
# USPTO Bulk Data Parser - Processes for Managing Logs
# Description: Processes handles log files.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# Import Python Modules
import logging
import traceback
import time
import os
import sys
import pprint

# Import USPTO Parser Functions
import USPTOProcessLinks

# Setup logging
def setup_logger(log_level, log_file):

    # Define logger object
    logger = logging.getLogger('USPTO_Database_Construction')
    log_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    # Set the log level verbosity
    if log_level == 1:
        logger.setLevel(logging.ERROR)
    elif log_level == 2:
        logger.setLevel(logging.WARNING)
    elif log_level == 3:
        logger.setLevel(logging.INFO)

# Check the args_array log_lock_file and switch and write file as 'Processed'
# TODO accept a passed arg to also write the log as processing, if needed by
# to balance loads using log file in main_process.
def write_process_log(args_array):

    # Set the document type for processing
    document_type = args_array['document_type']
    # Import Logger
    logger = logging.getLogger("USPTO_Database_Construction")

    # Print message to stdout and log file
    print("Updating the log for processed file: " + args_array['url_link'])
    logger.info("Updating the log for processed file: " + args_array['url_link'])

    # Set the log file to check and rewrite based on the document_type passed
    if document_type == "grant" : log_file_to_rewrite = args_array['grant_process_log_file']
    elif document_type == "application" : log_file_to_rewrite = args_array['application_process_log_file']
    elif document_type == "class" : log_file_to_rewrite = args_array['classification_process_log_file']
    elif document_type == "PAIR" : log_file_to_rewrite = args_array['pair_process_log_file']
    elif document_type == "legal" : log_file_to_rewrite = args_array['legal_process_log_file']

    # Variable hold while loop running
    log_rewrite_success = 0

    try:

        while log_rewrite_success == 0:

            # Create an array to store all lines to be rewritten after
            log_rewrite_array = []

            # Open log_lock_file to check status
            print("-- File locking log file for complete " + document_type + " file: " + args_array['url_link'])
            logger.info("-- File locking log file for complete " + document_type + " file: " + args_array['url_link'])
            log_lock = open(args_array["log_lock_file"], "r")
            locked_status = log_lock.read().strip()
            log_lock.close()

            # If the log lock file is set to open, rewrite log with changes and end while loop
            if locked_status == "0":
                # Write log lock as closed
                log_lock = open(args_array["log_lock_file"], "w")
                log_lock.write("1")
                log_lock.close()
                # Open the appropriate log file
                log_file = open(log_file_to_rewrite, "r")
                # Separate into array of arrays of original csv
                log_file_data_array = log_file.readlines()
                log_file.close()

                # Loop through each line in the file
                for line in log_file_data_array:
                    # If the first element in line is the link we have just processed
                    line = line.split(",")
                    if line[0] == args_array["url_link"]:
                        print("-- Found the URL link in log file")
                        logger.info("-- Found the URL link: " + args_array['url_link'] + " in log file")
                        # Append the line with "Processed"
                        log_rewrite_array.append([line[0], line[1], "Processed\n"])
                    # If the first element is not the line we are looking for
                    else:
                        # Append the line as is
                        log_rewrite_array.append(line)

                # Rewrite the new array to the log file in csv
                log_file = open(log_file_to_rewrite, "w")
                #print log_rewrite_array
                for line in log_rewrite_array:
                    #print line[0] + "," + line[1] + "," + line[2]
                    log_file.write(",".join(line))
                log_file.close()

                # Set the log_lock to open again and close the file.
                log_lock = open(args_array["log_lock_file"], "w")
                log_lock.write("0")
                log_lock.close()

                # Print message to stdout and log file
                print("-- Log updated for processed file: " + args_array['url_link'])
                logger.info("-- Log updated for processed file: " + args_array['url_link'])

                # End the while loop while by setting file_locked
                log_rewrite_success = 1

            # If the file was found to be locked by another process, close file then wait 1 second
            else:
                #print "waiting on log lock to be opened"
                log_lock.close()
                time.sleep(1)

    except Exception as e:
        # Print and log general fail comment
        print("-- Exception during the writing of " + document_type + " log file: " + args_array['url_link'])
        logger.error("-- Exception during the writing of " + document_type + " log file: " + args_array['url_link'])
        traceback.print_exc()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())


# Check the args_array log_lock_file and switch and write file as 'Verified'
# TODO accept a passed arg to also write the log as processing, if needed by
# to balance loads using log file in main_process.
def write_verified_log(args_array):

    # Set the document type for processing
    document_type = args_array['document_type']

    logger = logging.getLogger("USPTO_Database_Construction")

    # Print message to stdout and log file
    print("[Updating the log for verified file: " + args_array['url_link'] + "]")
    logger.info("[Updating the log for verified file: " + args_array['url_link'] + "]")

    # Set the log file to check and rewrite based on the document_type passed
    if document_type == "grant" : log_file_to_rewrite = args_array['grant_process_log_file']
    elif document_type == "application" : log_file_to_rewrite = args_array['application_process_log_file']
    elif document_type == "class" : log_file_to_rewrite = args_array['classification_process_log_file']
    elif document_type == "PAIR" : log_file_to_rewrite = args_array['pair_process_log_file']
    elif document_type == "legal" : log_file_to_rewrite = args_array['legal_process_log_file']

    # Variable hold while loop running
    log_rewrite_success = 0
    # Hold the loop until log has been modified
    while log_rewrite_success == 0:

        # Create an array to store all lines to be rewritten after
        log_rewrite_array = []
        # Open log_lock_file to check status
        log_lock = open(args_array["log_lock_file"], "r")
        locked_status = log_lock.read().strip()
        log_lock.close()

        # If the log lock file is set to open, rewrite log with changes and end while loop
        if locked_status == "0":
            # Write log lock as closed
            log_lock = open(args_array["log_lock_file"], "w")
            log_lock.write("1")
            log_lock.close()
            # Open the appropriate log file
            log_file = open(log_file_to_rewrite, "r")
            # Separate into array of arrays of original csv
            log_file_data_array = log_file.readlines()
            log_file.close()

            # Loop through each line in the file
            for line in log_file_data_array:
                # If the first element in line is the link we have just processed
                line = line.split(",")
                if line[0] == args_array["url_link"]:
                    print("-- Found the URL link in log file")
                    # Append the line with "Processed"
                    log_rewrite_array.append([line[0], line[1], "Processed", "Verified\n"])
                # If the first element is not the line we are looking for
                else:
                    # Append the line as is
                    log_rewrite_array.append(line)

            # Rewrite the new array to the log file in csv
            log_file = open(log_file_to_rewrite, "w")
            for line in log_rewrite_array:
                #print line[0] + "," + line[1] + "," + line[2]
                log_file.write(",".join(line))
            log_file.close()

            # Set the log_lock to open again and close the file.
            log_lock = open(args_array["log_lock_file"], "w")
            log_lock.write("0")
            log_lock.close()

            # Print message to stdout and log file
            print("[Log updated for verified file: " + args_array['url_link'] + "]")
            logger.info("[Log updated for verified file: " + args_array['url_link'] + "]")

            # End the while loop while by setting file_locked
            log_rewrite_success = 1

        # If the file was found to be locked by another process, close file then wait 1 second
        else:
            log_lock.close()
            time.sleep(1)

# Write all log links to files
def write_link_arrays_to_file(all_links_array, args_array):

    # Import logger
    logger = logging.getLogger("USPTO_Database_Construction")
    # Log writing of link arrays to file
    logger.info('Writing all required links to file ' + time.strftime("%c"))

    # Write all required links into file
    grant_process_file = open(args_array['grant_process_log_file'], "w")
    application_process_file = open(args_array['application_process_log_file'], "w")
    classification_process_file = open(args_array['classification_process_log_file'], "w")
    pair_process_file = open(args_array['pair_process_log_file'], "w")
    legal_process_file = open(args_array['legal_process_log_file'], "w")

    # Write all grant and application links to separate files
    for item in all_links_array["grants"]:
        grant_process_file.write(item[0] + "," + item[1] + ",Unprocessed\n")
    for item in all_links_array["applications"]:
        application_process_file.write(item[0] + "," + item[1] + ",Unprocessed\n")
    for item in all_links_array["classifications"]:
        classification_process_file.write(item[0] + "," + item[1] + ",Unprocessed\n")
    for item in all_links_array["PAIR"]:
        pair_process_file.write(item[0] + "," + item[1] + ",Unprocessed\n")
    for item in all_links_array["legal"]:
        legal_process_file.write(item[0] + "," + item[1] + ",Unprocessed\n")

    # Close files
    grant_process_file.close()
    application_process_file.close()
    classification_process_file.close()
    pair_process_file.close()
    legal_process_file.close()

    # Write finished message to log
    logger.info('Finished writing all patent data links to files. Finshed Time: ' + time.strftime("%c"))
    print("Finished writing all patent data links to files. Finshed Time: " + time.strftime("%c"))

# Write all log links to files
def update_link_arrays_to_file(all_links_array, args_array):

    # Import logger
    logger = logging.getLogger("USPTO_Database_Construction")
    print('Updating all source data links to file ' + time.strftime("%c"))
    logger.info('Updating all source data links to file ' + time.strftime("%c"))

    # Open files and read in data to check lines for links that exist already
    grant_process_file = open(args_array['grant_process_log_file'], "r+")
    application_process_file = open(args_array['application_process_log_file'], "r+")

    grant_process_data_array = grant_process_file.readlines()
    print(str(len(grant_process_data_array)) + " existing grant links were found in the log file")

    application_process_data_array = application_process_file.readlines()
    print(str(len(application_process_data_array)) + " existing application links were found in the log file")

    # Close the process log files
    grant_process_file.close()
    application_process_file.close()

    # Check if new found grant links exist already in file
    for new_item in all_links_array['grants']:
        # Define a flag for if new link found in existing list
        link_found_flag = False
        # Loop through all existing links found in file
        for item in grant_process_data_array:
            # Break the csv format into array
            item = item.split(",")
            # If match between links is found
            if new_item[0] == item[0]:
                # Set flag that link is found
                link_found_flag = True
                break
        # If flag is not found
        if link_found_flag == False:
            print("- New patent grant data file found..." + new_item[0])
            # Append the new links to array
            grant_process_data_array.append(new_item[0] + "," + new_item[1] + ",Processed\n")

    # Check if new found grant links exist already in file
    for new_item in all_links_array['applications']:
        # Define a flag for if new link found in existing list
        link_found_flag = False
        # Loop through all existing links found in file
        for item in application_process_data_array:
            # Break the csv format into array
            item = item.split(",")
            # If match between links is found
            if new_item[0] == item[0]:
                # Set flag that link is found
                link_found_flag = True
                break
        # If flag is not found
        if link_found_flag == False:
            print("- New patent application data file found..." + new_item[0])
            # Append the new links to array
            application_process_data_array.append(new_item[0] + "," + new_item[1] + ",Processed\n")

    grant_process_file = open(args_array['grant_process_log_file'], "w")
    application_process_file = open(args_array['application_process_log_file'], "w")

    # Write the new grant_process_data_array to the original log file
    for item in grant_process_data_array:
        grant_process_file.write(item)
    print('Updated grant links written to log file ' + time.strftime("%c"))
    logger.info('Updated grant links written to log file ' + time.strftime("%c"))
    # Write the new grant_process_data_array to the original log file
    for item in application_process_data_array:
        application_process_file.write(item)
    print('Updated application links written to log file ' + time.strftime("%c"))
    logger.info('Updated application links written to log file ' + time.strftime("%c"))

    # Close files
    grant_process_file.close()
    application_process_file.close()

    print("Finished updating all patent grant and application links to log files. Finshed Time: " + time.strftime("%c"))
    logger.info('Finished updating all patent grant and application links to log files ' + time.strftime("%c"))

# Collect all links from file
def collect_all_required_links_from_file(args_array):

    logger = logging.getLogger("USPTO_Database_Construction")

    # Initialize file arrays for temp storage
    grant_temp_array = []
    application_temp_array = []
    classification_temp_array = []
    pair_temp_array = []
    legal_temp_array = []

    print('Reading all required links to download and parse ' + time.strftime("%c"))
    logger.info('Reading all required links to download and parse ' + time.strftime("%c"))

    try:
        # Read all required grant links into array
        with open(args_array['grant_process_log_file'], "r") as grant_process_file:
            for line in grant_process_file:
                print(line)
                # Remove any blank lines
                if line.strip() != "":
                    # If doing verification, collect processed files that are not verified already
                    if "verify" in args_array['command_args']:
                        if line.strip() != "" and line.split(",")[2].replace("\n", "") == "Processed" and len(line.split(",")) == 3:
                            grant_temp_array.append(line.split(","))
                    # If parsing bulk-data, collect all unprocessed files
                    else:
                        if line.strip() != "" and line.split(",")[2].replace("\n", "") != "Processed":
                            grant_temp_array.append(line.split(","))

        # Read all required applicaton links into array
        with open(args_array['application_process_log_file'], "r") as application_process_file:
            for line in application_process_file:
                print(line)
                # Remove any blank lines
                if line.strip() != "":
                    # If doing verification, collect processed files that are not verified already
                    if "verify" in args_array['command_args']:
                        if line.split(",")[2].replace("\n", "") == "Processed"  and len(line.split(",")) == 3:
                            application_temp_array.append(line.split(","))
                    # If parsing bulk-data, collect all unprocessed files
                    else:
                        if line.split(",")[2].replace("\n", "") != "Processed":
                            application_temp_array.append(line.split(","))

        # Read all required classification links into array
        with open(args_array['classification_process_log_file'], "r") as classification_process_file:
            for line in classification_process_file:
                # If doing verification, collect processed files
                if "verify" in args_array['command_args']:
                    if line.split(",")[2].replace("\n", "") == "Processed" and len(line.split(",")) == 3:
                        classification_temp_array.append(line.split(","))
                # If parsing bulk-data, collect all unprocessed files
                else:
                    if line.split(",")[2].replace("\n", "") != "Processed":
                        classification_temp_array.append(line.split(","))

        # Read all required PAIR links into array
        with open(args_array['pair_process_log_file'], "r") as pair_process_file:
            for line in pair_process_file:
                # If doing verification, collect processed files
                if "verify" in args_array['command_args']:
                    if line.split(",")[2].replace("\n", "") == "Processed" and len(line.split(",")) == 3:
                        pair_temp_array.append(line.split(","))
                # If parsing bulk-data, collect all unprocessed files
                else:
                    if line.split(",")[2].replace("\n", "") != "Processed":
                        pair_temp_array.append(line.split(","))

        # Read all required legal links into array
        with open(args_array['legal_process_log_file'], "r") as legal_process_file:
            for line in legal_process_file:
                # If doing verification, collect processed files
                if "verify" in args_array['command_args']:
                    if line.split(",")[2].replace("\n", "") == "Processed" and len(line.split(",")) == 3:
                        legal_temp_array.append(line.split(","))
                # If parsing bulk-data, collect all unprocessed files
                else:
                    if line.split(",")[2].replace("\n", "") != "Processed":
                        legal_temp_array.append(line.split(","))

        print('Finished reading all required links to download and parse ' + time.strftime("%c"))
        logger.info('Finished reading all required links to download and parse ' + time.strftime("%c"))

        # Return the array to main function
        return({
            "grants" : grant_temp_array,
            "applications" : application_temp_array,
            "classifications" : classification_temp_array,
            "PAIR" : pair_temp_array,
            "legal" : legal_temp_array
        })

    except Exception as e:
        print("Failed to get all links from log files " + time.strftime("%c"))
        traceback.print_exc()
        logger.error('Failed to get all links from log files ' + time.strftime("%c"))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(str(e) + str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        return False

# Collect all links, or update with new links to log files
def build_or_update_link_files(args_array):

    logger = logging.getLogger("USPTO_Database_Construction")

    # Check if link log files exists already
    # If not exists, then find and write all links to file
    #TODO: what if only one log file is missing??  How could that happen??
    if not os.path.isfile(args_array['grant_process_log_file']) or not os.path.isfile(args_array['application_process_log_file']) or not os.path.isfile(args_array['classification_process_log_file']) or not os.path.isfile(args_array['legal_process_log_file']):

        # If verification is command then files need to be there already.
        # If they are not, exit execution
        if "verify" in args_array['command_args']:
            print("No existing link file lists found. Exiting verification process.  " + time.strftime("%c"))
            logger.info('No existing link file lists found.  Exiting verification process. ' + time.strftime("%c"))
            exit()

        print("No existing link file lists found. Creating them now.  " + time.strftime("%c"))
        logger.info('No existing link file lists found. Creating them now. ' + time.strftime("%c"))

        try:
            # Get List of all links
            all_links_array = USPTOProcessLinks.get_all_links(args_array)
            if args_array['stdout_level'] == 1: print(all_links_array)
            write_link_arrays_to_file(all_links_array, args_array)
        except Exception as e:
            print("Failed to get all links from USPTO bulk data site " + time.strftime("%c"))
            traceback.print_exc()
            logger.error('Failed to get all links from USPTO bulk data site ' + time.strftime("%c"))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(str(e) + str(exc_type) + str(fname) + str(exc_tb.tb_lineno))

    # Else if the update arg has been passed then update all links files before starting main function
    elif "update" in args_array['command_args']:

        print("Updating process log files... " + time.strftime("%c"))
        logger.info('Updating process log files... ' + time.strftime("%c"))

        try:
            # Get List of all links and update the existing links based on found links
            all_links_array = USPTOProcessLinks.get_all_links(args_array)
            if args_array['stdout_level'] == 1: print(all_links_array)
            update_link_arrays_to_file(all_links_array, args_array)
        except Exception as e:
            print("Failed to get all links from USPTO bulk data site " + time.strftime("%c"))
            traceback.print_exc()
            logger.error('Failed to get all links from USPTO bulk data site ' + time.strftime("%c"))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(str(e) + str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
