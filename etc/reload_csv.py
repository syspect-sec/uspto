#!/usr/bin/env python
# -*- coding: utf-8 -*-
# USPTOParser: Reload Tables from CSV
#
#

# Import Modules
import os
import ReloadSQLProcessor
import ReloadUSPTOLogger


# Get a list of csv files that match args['base_filename']
def get_csv_file_list(args):

    # Check if list of base_filename
    if isinstance(args['base_filename'], list):
        # Get list of all csv files in args['csv_dir_path']
        print("Checking path: " + args['csv_dir_path'])
        filenames = next(os.walk(args['csv_dir_path']), (None, None, []))[2]
        # Filter list for only startswith base_filename
        filtered = []
        for item in filenames:
            print("-- Checking: " + item)
            for base_file in args['base_filename']:
                if base_file in item:
                    filtered.append(args['csv_dir_path'] + "/" + item)
                    print("** Appending: " + args['csv_dir_path'] + "/" + item)

    # If base_filename is string
    elif isinstance(args['base_filename'], str):
        # Get list of all csv files in args['csv_dir_path']
        print("Checking path: " + args['csv_dir_path'])
        filenames = next(os.walk(args['csv_dir_path']), (None, None, []))[2]
        # filter list for only startswith base_filename
        filtered = []
        for item in filenames:
            print("-- Checking: " + item)
            if args['base_filename'] in item:
                filtered.append(args['csv_dir_path'] + "/" + item)
                print("** Appending: " + args['csv_dir_path'] + "/" + item)
    # Return filtered list of CSV files to reload
    return filtered

#
# Main Function
#
if __name__=="__main__":

    cwd = os.getcwd() + "/"
    # Log levels
    log_level = 3 # Log levels 1 = error, 2 = warning, 3 = info
    stdout_level = 1 # Stdout levels 1 = verbose, 0 = non-verbose
    app_log_file = cwd + "USPTO_rebuild.log"

    # Database args
    database_args = {
        "database_type" : "postgresql", # choose 'mysql' or 'postgresql'
        #"database_type" : "mysql", # choose 'mysql' or 'postgresql'
        "host" : "127.0.0.1",
        "port" : 5432, # PostgreSQL port
        #"port" : 3306, # MySQL port
        "user" : "uspto",
        "passwd" : "Ld58KimTi06v2PnlXTFuLG4", # PostgreSQL password
        #"passwd" : "R5wM9N5qCEU3an#&rku8mxrVBuF@ur", # MySQL password
        "db" : "uspto",
        "charset" : "utf8"
    }

    # Declare args
    args = {
        "base_filename" : "assignee",
        "table" : "ASSIGNEE_G",
        "csv_dir_path" : "../CSV/CSV_G",
        "record_type" : "grant"  # grant, application, (more ??)
    }

    # Setup logger
    USPTOLogger.setup_logger(log_level, app_log_file)
    # Include logger
    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Create a database connection
    database_connection = SQLProcessor.SQLProcess(database_args)

    # Get list of all csv to reload
    csv_list = get_csv_file_list(args)
    # Do each CSV file
    for csv_file in csv_list:
        print("-- Reloading file: " + csv_file)
        logger.info("-- Starting to reload process for file: " + csv_file)
        # Get filename from item
        filename = csv_file.split(".")[-2]
        filename = filename.split("/")[-1]
        filename = filename.split("_", 1)[-1]
        print("-- Extracted filename: " + filename + " from " + csv_file)
        logger.info("-- Extracted filename: " + filename + " from " + csv_file)
        # Clear table from previous files
        database_connection.remove_previous_file_records_of_single_table(args['record_type'], args['table'], filename)
        database_connection.load_csv_bulk_data(args['table'], args['record_type'], csv_file)
        logger.info("-- Finished reload process for file: " + filename)
