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
import USPTOStoreLegalData
import USPTOProcessZipFile

# Function opens the zip file for PAIR data files and parses, inserts to database
# and writes log file success
def process_legal_content(args_array):

    # Set the start time of operation
    start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the .CSV file from the ZIP file
    csv_file_name = USPTOProcessZipFile.extract_csv_file_from_zip(args_array)

    # If csv_file_contents is None or False, then return immediately
    if csv_file_name == None or csv_file_name == False:
        return False

    # Set a flag based on filename to call the extraction function
    args_array['extraction_type'] = set_extraction_type(csv_file_name)
    csv_output_filename = set_csv_output_filename(csv_file_name)

    # If csv file insertion is required, then open all the files
    # into args_array
    if "csv" in args_array['command_args'] or ("database" in args_array['command_args'] and args_array['database_insert_mode'] == "bulk"):
        args_array['csv_file_array'] = USPTOCSVHandler.open_csv_files(args_array['document_type'], csv_output_filename, args_array['csv_directory'], args_array['extraction_type'])

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
                USPTOStoreLegalData.store_legal_data(processed_data_array, args_array)
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
    if "cases" in filename: return "cases"
    elif "pacer_cases" in filename: return "pacercases"
    elif "names" in filename: return "names"
    elif "attorneys" in filename: return "attorneys"
    elif "patents" in filename: return "patents"
    else: return None

# Returns a filename for output csv file
def set_csv_output_filename(filename):
    if "cases" in filename: return "case"
    elif "pacer_cases" in filename: return "pacercase"
    elif "names" in filename: return "name"
    elif "attorneys" in filename: return "attorney"
    elif "patents" in filename: return "patent"
    else: return None

# Converts the extraction type to a SQL table name
def set_table_name_from_type(extraction_type):
    if extraction_type == "cases": return "uspto.CASE_L"
    elif extraction_type == "pacercases": return "uspto.PACERCASES_L"
    elif extraction_type == "names": return "uspto.PARTY_L"
    elif extraction_type == "attorneys": return "uspto.ATTORNEY_L"
    elif extraction_type == "patents": return "uspto.PATENT_L"
    else: return None

# Converts the line to array with fields that match
# the database column names
def extract_csv_line(args_array, line):

    #print(line)
    # Declare a processed array to append to
    processed_array = {
        "table_name" : set_table_name_from_type(args_array['extraction_type']),
        "FileName" : args_array['file_name'],
        "extraction_type": args_array['extraction_type']
    }

    # Handle a correspondance items
    if args_array['extraction_type'] == "cases":
        processed_array['CaseID'] = USPTOSanitizer.clean_PAIR_csv_item(line[1])
        processed_array['PacerID'] = USPTOSanitizer.clean_PAIR_csv_item(line[2])
        processed_array['CourtTitle'] = USPTOSanitizer.clean_PAIR_csv_item(line[3])
        processed_array['DistrictID'] = USPTOSanitizer.clean_PAIR_csv_item(line[4])
        processed_array['CaseTitle'] = USPTOSanitizer.clean_PAIR_csv_item(line[5])
        processed_array['AssignedTo'] = USPTOSanitizer.clean_PAIR_csv_item(line[6])
        processed_array['ReferredTo'] = USPTOSanitizer.clean_PAIR_csv_item(line[7])
        processed_array['Cause'] = USPTOSanitizer.clean_PAIR_csv_item(line[8])
        processed_array['JurisdictionBasis'] = USPTOSanitizer.clean_PAIR_csv_item(line[9])
        processed_array['FileDate'] = USPTOSanitizer.clean_PAIR_csv_item(line[10])
        processed_array['CloseDate'] = USPTOSanitizer.clean_PAIR_csv_item(line[11])
        processed_array['LastFileDate'] = USPTOSanitizer.clean_PAIR_csv_item(line[12])
        processed_array['JuryDemand'] = USPTOSanitizer.clean_PAIR_csv_item(line[13])
        processed_array['Demand'] = USPTOSanitizer.clean_PAIR_csv_item(line[14])
        processed_array['LeadCase'] = USPTOSanitizer.clean_PAIR_csv_item(line[15])
        processed_array['RelatedCase'] = USPTOSanitizer.clean_PAIR_csv_item(line[16])
        processed_array['Settlement'] = USPTOSanitizer.clean_PAIR_csv_item(line[17])
        processed_array['CaseIDRaw'] = USPTOSanitizer.clean_PAIR_csv_item(line[18])
        processed_array['CaseType1'] = USPTOSanitizer.clean_PAIR_csv_item(line[19])
        processed_array['CaseType2'] = USPTOSanitizer.clean_PAIR_csv_item(line[20])
        processed_array['CaseType3'] = USPTOSanitizer.clean_PAIR_csv_item(line[21])
        processed_array['CaseTypeNote'] = USPTOSanitizer.clean_PAIR_csv_item(line[22])

    elif args_array['extraction_type'] == "pacercases":
        processed_array['ApplicationID'] = USPTOSanitizer.clean_PAIR_csv_item(line[0])
        processed_array['ParentApplicationID'] = USPTOSanitizer.clean_PAIR_csv_item(line[1])
        processed_array['FileDate'] = USPTOSanitizer.clean_PAIR_csv_item(line[2])
        processed_array['ContinuationType'] = USPTOSanitizer.clean_PAIR_csv_item(line[3])

    elif args_array['extraction_type'] == "names":
        processed_array['CaseID'] = USPTOSanitizer.clean_PAIR_csv_item(line[1])
        processed_array['PartyType'] = USPTOSanitizer.clean_PAIR_csv_item(line[3])
        processed_array['Name'] = USPTOSanitizer.clean_PAIR_csv_item(line[5])

    elif args_array['extraction_type'] == "attorneys":
        processed_array['CaseID'] = USPTOSanitizer.clean_PAIR_csv_item(line[1])
        processed_array['CaseIDRaw'] = USPTOSanitizer.clean_PAIR_csv_item(line[2])
        processed_array['PartyType'] = USPTOSanitizer.clean_PAIR_csv_item(line[4])
        processed_array['Name'] = USPTOSanitizer.clean_PAIR_csv_item(line[6])
        processed_array['ContactInfo'] = USPTOSanitizer.clean_PAIR_csv_item(line[7])
        processed_array['Position'] = USPTOSanitizer.clean_PAIR_csv_item(line[8])

    elif args_array['extraction_type'] == "patents":
        processed_array['CaseID'] = USPTOSanitizer.clean_PAIR_csv_item(line[2])
        processed_array['PacerID'] = USPTOSanitizer.clean_PAIR_csv_item(line[1])
        processed_array['NOS'] = USPTOSanitizer.clean_PAIR_csv_item(line[4])
        processed_array['PatentID'] = USPTOSanitizer.strip_leading_zeros(USPTOSanitizer.clean_PAIR_csv_item(line[11]))
        processed_array['PatentDocType'] = USPTOSanitizer.clean_PAIR_csv_item(line[12])

    # Return the array for storage
    return processed_array
