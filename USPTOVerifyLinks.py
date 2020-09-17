# USPTOVerifyLinks.py
# USPTO Bulk Data Parser - Vefify the database contents
# Description: Verifies the database contents against the exptected
# values based on XML tags found in source bulk-data file.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# Import Python Modules
import time
import re
import os
import sys
import shutil
import traceback
from pprint import pprint

# Import USPTO Parser Functions
import USPTOLogger
import USPTOProcessLinks
import USPTOProcessZipFile
import USPTOSanitizer


# Function to accept raw xml data and route to the appropriate function to parse
# either grant, application or PAIR data.
def verification_extract_data_router(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    try:
        # Process the contents of file based on type
        if args_array['uspto_xml_format'] == "gAPS":
            counts_dict = extract_APS_grant_tag_counts(args_array)
        elif args_array['uspto_xml_format'] == "aXML1":
            counts_dict = extract_XML1_application_tag_counts(args_array)
        elif args_array['uspto_xml_format'] == "aXML4":
            counts_dict = extract_XML4_application_tag_counts(args_array)
        elif args_array['uspto_xml_format'] == "gXML2":
            counts_dict = extract_XML2_grant_tag_counts(args_array)
        elif args_array['uspto_xml_format'] == "gXML4":
            counts_dict = extract_XML4_grant_tag_counts(args_array)
        elif args_array['uspto_xml_format'] == "PAIR":
            counts_dict = extract_PAIR_counts(args_array)
        elif args_array['uspto_xml_format'] == "LEGAL":
            counts_dict = extract_legal_counts(args_array)
        elif args_array['uspto_xml_format'] == "CPCCLS":
            counts_dict = extract_CPC_class_counts(args_array)
        elif args_array['uspto_xml_format'] == "USCLS":
            counts_dict = extract_US_class_counts(args_array)
        elif args_array['uspto_xml_format'] == "USCPCCLS":
            counts_dict = extract_USCPC_class_counts(args_array)

        # Return the dictionary of table, filenames and counts
        return counts_dict

    except Exception as e:
        # Print and log general fail comment
        print("Verification tag count extraction failed for document type: " + args_array['uspto_xml_format'] + " link: " + args_array['url_link'])
        logger.error("Verification tag count extraction for document type: " + args_array['uspto_xml_format'] + " link: " + args_array['url_link'])
        traceback.print_exc()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

# Function to route the extraction of expected XML tags
def verify_link_file(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Download the file and append temp location to args array
    args_array['temp_zip_file_name'] = USPTOProcessLinks.download_zip_file(args_array)
    # Route to the correct extraction function
    counts_dict = verification_extract_data_router(args_array)
    if counts_dict:
        # Store the exptected tag counts in database
        args_array['database_connection'].storeVerificationExtraction(counts_dict, args_array)
    else:
        # Print to stdout and log
        print("The contents of: " + args_array['file_name'] + " were empty. Finished at: " + time.strftime("%c"))
        logger.error("The contents of: " + args_array['file_name'] + "were empty. Finished at: " + time.strftime("%c"))

    # Print to stdout and log
    print("Finished the verificaction process for contents of: " + args_array['file_name'] + " Finished at: " + time.strftime("%c"))
    logger.info("Finished the verification process for contents of: " + args_array['file_name'] + " Finished at: " + time.strftime("%c"))

# Extract the tag count for APS grant files
def extract_APS_grant_tag_counts(args_array):
    pass

# Extract the tag count for XML2 grant files
def extract_XML2_grant_tag_counts(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Print to stdout and log
    print("Starting the XML tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))
    logger.info("Starting the XML tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))

    # Extract the XML file from the ZIP file
    xml_file_contents = USPTOProcessZipFile.extract_xml_file_from_zip(args_array)

    # Declare a dictionary to use in counting tags
    # NOTE: CPCClASS_G, APPLICANT_G, are not available in XML2 Grant files
    tags_dict = {
        "GRANT" : ["<PATDOC"],
        "INTCLASS_G" : ["<B510"],
        "USCLASS_G" : ["<B520"],
        "INVENTOR_G" : ["<B720"],
        "AGENT_G" : ["<B740]"],
        "ASSIGNEE_G" : ["<B730"],
        "NONPATCIT_G" : ["<B562"],
        "EXAMINER_G" : ["<B745"],
        # TODO: GRACIT and FORPATCIT are not countable by single line
        # they require extracting tags in another way
        #"GRACIT_G" : "<B561",
        #"FORPATCIT_G" : "",
        "FOREIGNPRIORITY_G" : ["<B310"]
    }

    # Declare a dictionary to hold counts by table
    counts_dict = {
        "file_name" : args_array['file_name'],
        "GRANT" : 0,
        "INTCLASS_G" : 0,
        "CPCCLASS_G" : 0,
        "USCLASS_G" : 0,
        "INVENTOR_G" : 0,
        "AGENT_G" : 0,
        "ASSIGNEE_G" : 0,
        "APPLICANT_G" : 0,
        "NONPATCIT_G" : 0,
        "EXAMINER_G" : 0,
        "GRACIT_G" : 0,
        "FORPATCIT_G" : 0,
        "FOREIGNPRIORITY_G" : 0
    }

    # Print to stdout and log
    print("Starting the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))
    logger.info("Starting the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        # Increment the count for appropriate table
                        counts_dict[table] += 1

    # Print to stdout and log
    print("Finished the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))
    logger.info("Finished the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))

    # Return the dictionary of counts for found tags
    if args_array['stdout_level'] == 1: pprint(counts_dict)
    return counts_dict

# Extract the tag count for XML4 grant files
def extract_XML4_grant_tag_counts(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the XML file from the ZIP file
    xml_file_contents = USPTOProcessZipFile.extract_xml_file_from_zip(args_array)

    # If xml_file_contents is None or False, then return immediately
    if xml_file_contents == None or xml_file_contents == False:
        return False

    # Declare a dictionary to use in counting tags
    tags_dict = {
        "GRANT" : ["<us-patent-grant"],
        "INTCLASS_G" : ["<classification-ipcr"],
        "CPCCLASS_G" : ["<classification-cpc"],
        "USCLASS_G" : ["<main-classification", "<further-classification"],
        "INVENTOR_G" : ["<us-applicant>", "<applicant>"],
        "AGENT_G" : ["<agent>"],
        "ASSIGNEE_G" : ["<assignee>"],
        "APPLICANT_G" : ["<us-applicant>", "<applicant>"],
        "NONPATCIT_G" : ["<nplcit"],
        "EXAMINER_G" : ["<primary-examiner", "<assistant-examiner"],
        # Grant and foreign citations cannot be counted using only tags
        #"GRACIT_G" : "<patcit",
        #"FORPATCIT_G" : "",
        "FOREIGNPRIORITY_G" : ["<priority-claim"]
    }

    # Declare a dictionary to hold counts by table
    counts_dict = {
        "file_name" : args_array['file_name'],
        "GRANT" : 0,
        "INTCLASS_G" : 0,
        "CPCCLASS_G" : 0,
        "USCLASS_G" : 0,
        "INVENTOR_G" : 0,
        "AGENT_G" : 0,
        "ASSIGNEE_G" : 0,
        "APPLICANT_G" : 0,
        "NONPATCIT_G" : 0,
        "EXAMINER_G" : 0,
        "GRACIT_G" : 0,
        "FORPATCIT_G" : 0,
        "FOREIGNPRIORITY_G" : 0
    }

    # Print to stdout and log
    print("Starting the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))
    logger.info("Starting the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        # Increment the count for appropriate table
                        counts_dict[table] += 1

    # Print to stdout and log
    print("Finished the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))
    logger.info("Finished the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))

    # Return the dictionary of counts for found tags
    if args_array['stdout_level'] == 1: pprint(counts_dict)

    # Return the dictionary of counts for found tags
    return counts_dict

# Extract the tag count for XML1 application files
def extract_XML1_application_tag_counts(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the XML file from the ZIP file
    xml_file_contents = USPTOProcessZipFile.extract_xml_file_from_zip(args_array)

    # If xml_file_contents is None or False, then return immediately
    if xml_file_contents == None or xml_file_contents == False:
        return False

    # Declare a dictionary to use in counting tags
    #CPCCLASS_A are not included in XML1 applications
    tags_dict = {
        "APPLICATION" : ["<patent-application-publication"],
        "INTCLASS_A" : ["<classification-ipc"],
        "USCLASS_A" : ["<classification-us"],
        "FOREIGNPRIORITY_A" : ["<priority-application-number"],
        # AGENT_A cannot be counted by a single tag
        "AGENT_A" : [],
        # ASSIGNEE_A cannot be counted by a single tag
        #"ASSIGNEE_A" : [],
        "INVENTOR_A" : ["first-named-inventor", "inventor"],
        # APPLICANT_A cannot be counted by single tag
        "APPLICANT_A" : []
    }

    # Declare a dictionary to hold counts by table
    counts_dict = {
        "file_name" : args_array['file_name'],
        "APPLICATION" : 0,
        "INTCLASS_A" : 0,
        "USCLASS_A" : 0,
        "CPCCLASS_A" : 0,
        "FOREIGNPRIORITY_A" : 0,
        "AGENT_A" : 0,
        "ASSIGNEE_A" : 0,
        "INVENTOR_A" : 0,
        "APPLICANT_A" : 0
    }

    # Print to stdout and log
    print("Starting the XML1 application tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))
    logger.info("Starting the XML1 application tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        # Increment the count for appropriate table
                        counts_dict[table] += 1

    # Print to stdout and log
    print("Finished the XML1 appication tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))
    logger.info("Finished the XML1 application tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))
    # Return the dictionary of counts for found tags
    if args_array['stdout_level'] == 1: pprint(counts_dict)

    # Return the dictionary of counts for found tags
    return counts_dict

# Extract the tag count for XML4 application files
def extract_XML4_application_tag_counts(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the XML file from the ZIP file
    xml_file_contents = USPTOProcessZipFile.extract_xml_file_from_zip(args_array)

    # If xml_file_contents is None or False, then return immediately
    if xml_file_contents == None or xml_file_contents == False:
        return False

    # Declare a dictionary to use in counting tags
    tags_dict = {
        "APPLICATION" : ["<us-patent-application"],
        "INTCLASS_A" : ["<classification-ipcr"],
        "USCLASS_A" : ["<main-classification", "<further-classification"],
        "CPCCLASS_A" : ["<classification-cpc"],
        "FOREIGNPRIORITY_A" : ["<priority-claim>"],
        "AGENT_A" : ["<agent>"],
        "ASSIGNEE_A" : ["<assignee>"],
        "INVENTOR_A" : ["<inventor>"],
        "APPLICANT_A" : ["<us-applicant>", "<applicant>"]
    }

    # Declare a dictionary to hold counts by table
    counts_dict = {
        "file_name" : args_array['file_name'],
        "APPLICATION" : 0,
        "INTCLASS_A" : 0,
        "USCLASS_A" : 0,
        "CPCCLASS_A" : 0,
        "FOREIGNPRIORITY_A" : 0,
        "AGENT_A" : 0,
        "ASSIGNEE_A" : 0,
        "INVENTOR_A" : 0,
        "APPLICANT_A" : 0
    }

    # Print to stdout and log
    print("Starting the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))
    logger.info("Starting the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Started at: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        # Increment the count for appropriate table
                        counts_dict[table] += 1

    # Print to stdout and log
    print("Finished the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))
    logger.info("Finished the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Finished at: " + time.strftime("%c"))
    # Return the dictionary of counts for found tags
    if args_array['stdout_level'] == 1: pprint(counts_dict)

    # Return the dictionary of counts for found tags
    return counts_dict

# Extract the tag count for legal data files
def extract_legal_counts(args_array):
    pass

# Extract the tag count for PAIR data files
def extract_PAIR_counts(args_array):
    pass

# Extract the tag count for CPC classification data files
def extract_CPC_class_counts(args_array):
    pass

# Extract the tag count for US classification data files
def extract_US_class_counts(args_array):
    pass

# Extract the tag count for CPC / US class concordance data files
def extract_USCPC_class_counts(args_array):
    pass
