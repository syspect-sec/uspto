# USPTOStoreClassificationData.py
# USPTO Bulk Data Parser - Store Classification Data
# Description: Imported to the main USPTOParser.py.  Stores classification data in CSV or database.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# Import Python Modules
import time
import traceback
import os
import sys

# Import USPTO Parser Functions
import USPTOLogger
import SQLProcessor

# Function used to store PAIR data in CSV and/or database
def store_classification_data(processed_data_array, args_array, class_id):

    # Set process start time
    start_time = time.time()
    # Extract some variables from args_array
    file_name = args_array['file_name']

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # If the argument specified to store data into csv file or csv is needed for bulk database insertion
    if "csv" in args_array["command_args"] or ("database" in args_array['command_args'] and args_array['database_insert_mode'] == "bulk"):

        # Process a single classification csv record into a new formatted csv file
        # Using the already opened csv.csv.DictWriter object stored in args array.
        # Table name must be appended to the dictionary for later processing
        if args_array['stdout_level'] == 1:
            # Print start message to stdout and log
            print('- Starting to write {0} to .csv file {1} for document: {2}. Start Time: {3}'.format(args_array['document_type'], file_name, class_id, time.strftime("%c")))
        # Try catch is to avoid failing the whole file when
        # htmlentity characters found or other error occurs
        try:
            if type(processed_data_array) == list:
                for item in processed_data_array:
                    # Move the table name to temp variable and remove from table
                    table_name = item['table_name']
                    extraction_type = item['extraction_type']
                    del item['table_name']
                    del item['extraction_type']
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array'][extraction_type]['csv_writer'].writerow(item)
            else:
                # Move the table name to temp variable and remove from table
                table_name = processed_data_array['table_name']
                extraction_type = processed_data_array['extraction_type']
                del processed_data_array['table_name']
                del processed_data_array['extraction_type']
                # Write the dictionary of document data to .csv file
                args_array['csv_file_array'][extraction_type]['csv_writer'].writerow(processed_data_array)
            # Append the table onto the array
            args_array['csv_file_array'][extraction_type]['table_name'] = table_name
        except Exception as e:
            print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, class_id, table_name, time.strftime("%c")))
            logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, class_id, table_name, time.strftime("%c")))
            traceback.print_exc()

    # If command arg is set to put data into database
    elif "database" in args_array["command_args"] and args_array['database_insert_mode'] == "each":

        # Reset the start time
        start_time = time.time()

        print('- Starting to write {0} to database. Start Time: {1}'.format(file_name, time.strftime("%c")))

        # Strip the metadata item off the array and process it first
        # Store table name for stdout
        args_array['table_name'] = processed_data_array['table_name']
        del processed_data_array['table_name']
        # Build query and pass to database loader
        args_array['database_connection'].load(SQLProcessor.build_sql_insert_query(processed_data_array, args_array), args_array)
