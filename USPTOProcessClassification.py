# ImportPython Modules
import time
import os
import sys
import traceback
from csv import reader

# Import USPTO Parser Functions
import USPTOLogger
import USPTOSanitizer
import USPTOCSVHandler
import SQLProcessor
import USPTOStoreClassificationData

# This funtion accepts a line from the class text file and
# parses it and returns a dictionary to build an sql query string
def return_US_class_dict(line):

    # Build a class dictionary
    class_dictionary = {
        "table_name" : "uspto.USCLASSIFICATION",
        "extraction_type" : "usclass",
        "Class" : line[0:3].strip(),
        "SubClass" : line[3:9].strip(),
        "Indent" : line[9:11].strip(),
        "SubClsSqsNum" : line[11:15].strip(),
        "NextHigherSub" : line[15:21].strip(),
        "Title" : line[21:len(line)+1][0:140].replace("[N:", "").replace("]", "").replace("[", "").strip()
    }
    #print(class_dictionary)
    # Return the class dictionary
    return class_dictionary

# Extract the the data from line of CPC titles csv
def extract_CPC_class_dict(line):

    cpc_array = USPTOSanitizer.return_CPC_class_application(line[0])

    # Build a class dictionary
    class_dictionary = {
        "table_name" : "uspto.CPCCLASSIFICATION",
        "extraction_type" : "cpcclass",
        "Section" : cpc_array[0],
        "Class" : cpc_array[1],
        "SubClass" : cpc_array[2],
        "MainGroup" : cpc_array[3],
        "SubGroup" : cpc_array[4],
        "Title" : line[1].replace('"', "").strip()
    }
    #print(class_dictionary)
    # Return the class dictionary
    return class_dictionary

# Extract the the data from line of US to CPC concordance
def extract_USCPC_class_dict(line, file_name):

    class_dict_array = []
    # Get the US class from array
    us_class = line[0]
    position = 1
    # Loop through all other CPC classes and append an item
    for i in range(1, len(line)):

        if line[i].strip() != "":
            # Build a class dictionary
            class_dictionary = {
                "table_name" : "uspto.USCPCCONCORDANCE",
                "extraction_type" : "uscpc",
                "USClass" : us_class.strip(),
                "CPCClass" : line[i].strip(),
                "Position" : position,
                "FileName" : file_name
            }
            position += 1
            # Append item to array to be returned
            class_dict_array.append(class_dictionary)

    #print(class_dict_array)
    # Return the class dictionary
    return class_dict_array

# Process a line of CSV from classification
def process_class_content(args_array):

    # Set the start time of operation
    start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # If csv file insertion is required, then open all the files
    # into args_array
    if "csv" in args_array['command_args'] or ("database" in args_array['command_args'] and args_array['database_insert_mode'] == "bulk"):
        args_array['csv_file_array'] = USPTOCSVHandler.open_csv_files(args_array['document_type'], args_array['file_name'], args_array['csv_directory'])

    # Check the classification filetype code and process accordingly
    if args_array['uspto_xml_format'] == "USCLS":

        # Open file in read mode
        with open(args_array['url_link'], 'r') as read_obj:
            # Iterate over each row in the csv using reader object
            for line in read_obj:
                #print(line)
                # Extract the line into array
                processed_data_array = return_US_class_dict(line)
                processed_data_array['FileName'] = args_array['file_name']
                # Store the array into newly formatted CSV
                class_id = str(processed_data_array['Class']) + " " + str(processed_data_array['SubClass'])
                USPTOStoreClassificationData.store_classification_data(processed_data_array, args_array, class_id)

    # Titles for CPC classifications
    elif args_array['uspto_xml_format'] == "CPCCLS":

        extraction_type = "cpc"
        # Open file in read mode
        with open(args_array['url_link'], 'r') as read_obj:
            # Pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # Iterate over each row in the csv using reader object
            line_cnt = 0
            for line in csv_reader:
                if line_cnt != 0:
                    # Extract the line into array
                    processed_data_array = extract_CPC_class_dict(line)
                    # Store the array into newly formatted CSV
                    processed_data_array['FileName'] = args_array['file_name']
                    class_id = str(processed_data_array['Section']) + str(processed_data_array['Class']) + str(processed_data_array['SubClass']) + " " + str(processed_data_array['MainGroup']) + "/" + str(processed_data_array['SubGroup'])
                    USPTOStoreClassificationData.store_classification_data(processed_data_array, args_array, class_id)
                line_cnt += 1

    # USPC to CPC classification concordance table
    elif args_array['uspto_xml_format'] == "USCPCCLS":

        # Open file in read mode
        with open(args_array['url_link'], 'r') as read_obj:
            # Pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # Iterate over each row in the csv using reader object
            line_cnt = 0
            for line in csv_reader:
                if line_cnt != 0:
                    # Extract the line into array
                    processed_data_array = extract_USCPC_class_dict(line, args_array['file_name'])
                    if len(processed_data_array) != 0:
                        # Store the array into newly formatted CSV
                        class_id = str(processed_data_array[0]['USClass'])
                        USPTOStoreClassificationData.store_classification_data(processed_data_array, args_array, class_id)
                line_cnt += 1

    # Set a flag file_processed to ensure that the bulk insert succeeds
    # This should be true, in case the database insertion method is not bulk
    file_processed = True

    # If data is to be inserted as bulk csv files, then call the sql function
    if "database" in args_array["command_args"] and args_array['database_insert_mode'] == 'bulk':
        # Check for previous attempt to process the file and clean database if required
        args_array['database_connection'].remove_previous_file_records(args_array['document_type'], args_array['file_name'])
        # Loop through each csv file and bulk copy into database
        for key, csv_file in list(args_array['csv_file_array'].items()):
            # Load CSV file into database
            file_processed = args_array['database_connection'].load_csv_bulk_data(args_array, key, csv_file)

    if file_processed:
        # Send the information to USPTOLogger.write_process_log to have log file rewritten to "Processed"
        USPTOLogger.write_process_log(args_array)
        if "csv" not in args_array['command_args']:
            # Delete all the open csv files
            USPTOCSVHandler.delete_csv_files(args_array)

        print('[Loaded {0} data for {1} into database. Time:{2} Finished Time: {3} ]'.format(args_array['document_type'], args_array['url_link'], time.time() - start_time, time.strftime("%c")))
        logger.info('Loaded {0} data for {1} into database. Time:{2} Finished Time: {3}'.format(args_array['document_type'], args_array['url_link'], time.time() - start_time, time.strftime("%c")))
        # Return file_processed as success status
        return file_processed
    else:
        print('[Failed to bulk load {0} data for {1} into database. Time:{2} Finished Time: {3} ]'.format(args_array['document_type'], args_array['url_link'], time.time() - start_time, time.strftime("%c")))
        logger.error('Failed to bulk load {0} data for {1} into database. Time:{2} Finished Time: {3} ]'.format(args_array['document_type'], args_array['url_link'], time.time() - start_time, time.strftime("%c")))
        # Return None as failed status during database insertion
        return None
