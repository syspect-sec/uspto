# USPTOProcessPAIRData.py
# USPTO Bulk Data Parser - Processes PAIR Data Files
# Description: Imported to the main USPTOParser.py.  Processes a downloaded PAIR data files to the extracting.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

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
import USPTOStorePAIRData
import USPTOProcessZipFile

# Function opens the zip file for PAIR data files and parses, inserts to database
# and writes log file success
def process_PAIR_content(args_array):

    # Set the start time of operation
    start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # If csv file insertion is required, then open all the files
    # into args_array
    if "csv" in args_array['command_args'] or ("database" in args_array['command_args'] and args_array['database_insert_mode'] == "bulk"):
        args_array['csv_file_array'] = USPTOCSVHandler.open_csv_files(args_array['document_type'], args_array['file_name'], args_array['csv_directory'])

    # Extract the .CSV file from the ZIP file
    csv_file_name = USPTOProcessZipFile.extract_csv_file_from_zip(args_array)

    # If csv_file_contents is None or False, then return immediately
    if csv_file_name == None or csv_file_name == False:
        return False

    # Set a flag based on filename to call the extraction function
    args_array['extraction_type'] = set_extraction_type(csv_file_name)

    # Open file in read mode
    with open(csv_file_name, 'r') as read_obj:
        # Pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        # Iterate over each row in the csv using reader object
        line_cnt = 0
        for line in csv_reader:
            if line_cnt != 0:
                # Extract the line into array
                processed_data_array = extract_csv_line(args_array, line)
                # Store the array into newly formatted CSV
                USPTOStorePAIRData.store_PAIR_data(processed_data_array, args_array)
            line_cnt += 1

    # If not sandbox mode, then delete the .zip file
    if args_array['sandbox'] == False and os.path.exists(args_array['temp_zip_file_name']):
        # Print message to stdout
        print('[Purging .zip file ' + args_array['temp_zip_file_name'] + '...]')
        logger.info('Purging .zip file ' + args_array['temp_zip_file_name'] + '...')
        os.remove(args_array['temp_zip_file_name'])

    # Close all the open .csv files being written to
    USPTOCSVHandler.close_csv_files(args_array)

    # Set a flag file_processed to ensure that the bulk insert succeeds
    # This should be true, in case the database insertion method is not bulk
    file_processed = True

    # If data is to be inserted as bulk csv files, then call the sql function
    if "database" in args_array["command_args"] and args_array['database_insert_mode'] == 'bulk':
        # Check for previous attempt to process the file and clean database if required
        args_array['database_connection'].remove_previous_file_records(args_array['document_type'], args_array['file_name'])
        # Loop through each csv file and bulk copy into database
        for key, csv_file in list(args_array['csv_file_array'].items()):
            # Only load csv file to database if its for this instance
            if key == args_array['extraction_type']:
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


# Returns a code for the extraction type
def set_extraction_type(filename):
    if "transactions" in filename: return "transaction"
    elif "pat_term_adj" in filename: return "adjustment"
    elif "continuity_children" in filename: return "continuitychild"
    elif "continuity_parents" in filename: return "continuityparent"
    elif "correspondence_address" in filename: return "correspondence"
    else: return None

# Converts the extraction type to a SQL table name
def set_table_name_from_type(pair_type):
    if pair_type == "transactions": return "uspto.TRANSACTION_P"
    elif pair_type == "adjustment": return "uspto.ADJUSTMENT_P"
    elif pair_type == "continuitychild": return "uspto.CONTINUITYCHILD_P"
    elif pair_type == "continuityparent": return "uspto.CONTINUITYPARENT_P"
    elif pair_type == "correspondence": return "uspto.CORRESPONDENCE_P"
    else: return None

# Extracts a line list into dictionary with keys
# named for the database columns
def extract_csv_line(args_array, line):

    #print(line)
    # Declare a processed array to append to
    processed_array = {
        "table_name" : set_table_name_from_type(args_array['extraction_type']),
        "FileName" : args_array['file_name'],
        "extraction_type": args_array['extraction_type']
    }

    # Handle a correspondance items
    if args_array['extraction_type'] == "correspondence":
        processed_array['ApplicationID'] = USPTOSanitizer.strip_leading_zeros(USPTOSanitizer.clean_PAIR_csv_item(line[0]))
        processed_array['Name1'] = USPTOSanitizer.clean_PAIR_csv_item(line[1])
        processed_array['Name2'] = USPTOSanitizer.clean_PAIR_csv_item(line[2])
        processed_array['Address'] = USPTOSanitizer.clean_PAIR_csv_item(line[3]) + " " + USPTOSanitizer.clean_PAIR_csv_item(line[4])
        processed_array['City'] = USPTOSanitizer.clean_PAIR_csv_item(line[5])
        processed_array['PostalCode'] = USPTOSanitizer.clean_PAIR_csv_item(line[6])
        processed_array['RegionCode'] = USPTOSanitizer.clean_PAIR_csv_item(line[7])
        processed_array['RegionName'] = USPTOSanitizer.clean_PAIR_csv_item(line[8])
        processed_array['CountryCode'] = USPTOSanitizer.clean_PAIR_csv_item(line[9])
        processed_array['CountryName'] = USPTOSanitizer.clean_PAIR_csv_item(line[10])
        processed_array['CustomerNum'] = USPTOSanitizer.clean_PAIR_csv_item(line[11])

    elif args_array['extraction_type'] == "continuityparent":
        processed_array['ApplicationID'] = USPTOSanitizer.strip_leading_zeros(USPTOSanitizer.clean_PAIR_csv_item(line[0]))
        processed_array['ParentApplicationID'] = USPTOSanitizer.strip_leading_zeros(USPTOSanitizer.clean_PAIR_csv_item(line[1]))
        processed_array['FileDate'] = USPTOSanitizer.clean_PAIR_csv_item(line[2])
        processed_array['ContinuationType'] = USPTOSanitizer.clean_PAIR_csv_item(line[3])

    elif args_array['extraction_type'] == "continuitychild":
        processed_array['ApplicationID'] = USPTOSanitizer.strip_leading_zeros(USPTOSanitizer.clean_PAIR_csv_item(line[0]))
        processed_array['ChildApplicationID'] = USPTOSanitizer.strip_leading_zeros(USPTOSanitizer.clean_PAIR_csv_item(line[1]))
        processed_array['FileDate'] = USPTOSanitizer.clean_PAIR_csv_item(line[2])
        processed_array['ContinuationType'] = USPTOSanitizer.clean_PAIR_csv_item(line[3])

    # Return the array for storage
    return processed_array
