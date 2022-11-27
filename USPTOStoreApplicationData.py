# USPTOStoreApplicationData.py
# USPTO Bulk Data Parser - Store Application Data
# Description: Imported to the main USPTOParser.py.  Stores application data in CSV or database.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# Import Python Modules
import time
import traceback
import os
import sys
from pprint import pprint

# Import USPTO Parser Functions
import USPTOLogger
import SQLProcessor

# Funtion to store patent application data to csv and/or database
# TODO: change function to append to csv files until threshhold reached
# then dump CSV to database in batch, and erase CSV file if -csv flag not set.
def store_application_data(processed_data_array, args_array):

    # Set process start time
    start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract critical variables from args_array
    uspto_xml_format = args_array['uspto_xml_format']
    file_name = args_array['file_name']

    # If the argument specified to store data into csv file or csv is needed for bulk database insertion
    if "csv" in args_array["command_args"] or ("database" in args_array['command_args'] and args_array['database_insert_mode'] == "bulk"):

        # Process all the collected application data for one patent record into .csv file
        # Using the already opened csv.DictWriter object stored in args array.
        if "processed_application" in processed_data_array and len(processed_data_array['processed_application']):
            for data_item in processed_data_array["processed_application"]:
                # Print start message to stdout and log
                if args_array['stdout_level'] == 1:
                    print('- Starting to write {0} to .csv file {1} for document: {2}. Start Time: {3}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], time.strftime("%c")))
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['application']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['application']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_agent" in processed_data_array and len(processed_data_array['processed_agent']):
            for data_item in processed_data_array["processed_agent"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['agent']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['agent']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_assignee" in processed_data_array and len(processed_data_array['processed_assignee']):
            for data_item in processed_data_array["processed_assignee"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['assignee']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['assignee']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_applicant" in processed_data_array and len(processed_data_array['processed_applicant']):
            for data_item in processed_data_array["processed_applicant"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['applicant']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['applicant']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_inventor" in processed_data_array and len(processed_data_array['processed_inventor']):
            for data_item in processed_data_array["processed_inventor"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['inventor']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['inventor']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_usclass" in processed_data_array and len(processed_data_array['processed_usclass']):
            for data_item in processed_data_array["processed_usclass"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['usclass']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['usclass']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_intclass" in processed_data_array and len(processed_data_array['processed_intclass']):
            for data_item in processed_data_array["processed_intclass"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['intclass']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['intclass']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_cpcclass" in processed_data_array and len(processed_data_array['processed_cpcclass']):
            for data_item in processed_data_array["processed_cpcclass"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['cpcclass']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['cpcclass']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()
        if "processed_foreignpriority" in processed_data_array and len(processed_data_array['processed_foreignpriority']):
            for data_item in processed_data_array["processed_foreignpriority"]:
                table_name = data_item['table_name']
                del data_item['table_name']
                try:
                    # Write the dictionary of document data to .csv file
                    args_array['csv_file_array']['foreignpriority']['csv_writer'].writerow(data_item)
                    # Append the table onto the array
                    args_array['csv_file_array']['foreignpriority']['table_name'] = table_name
                except Exception as e:
                    print('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    logger.info('- Error writing {0} to .csv file {1} for document: {2} into table {3}. Start Time: {4}'.format(args_array['document_type'], file_name, data_item['ApplicationID'], table_name, time.strftime("%c")))
                    traceback.print_exc()

    elif "database" in args_array["command_args"] and args_array['database_insert_mode'] == "each":

        # Reset the start time
        start_time = time.time()
        if args_array['stdout_level'] == 1:
            print('- Starting to write {0} to database. Start Time: {1}'.format(file_name, time.strftime("%c")))

        # Strip the processed_grant item off the array and process it first
        processed_application = processed_data_array['processed_application']
        del processed_data_array['processed_application']
        for item in processed_application:
            args_array['table_name'] = item['table_name']
            args_array['document_id'] = item['ApplicationID']
            # Build query and pass to database loader
            args_array['database_connection'].load(SQLProcessor.build_sql_insert_query(item, args_array), args_array)

        # Loop throught the processed_data_array and create sql queries and execute them
        for key, value in list(processed_data_array.items()):
            for item in value:
                args_array['table_name'] = item['table_name']
                args_array['document_id'] = item['ApplicationID']
                args_array['database_connection'].load(SQLProcessor.build_sql_insert_query(item, args_array), args_array)
