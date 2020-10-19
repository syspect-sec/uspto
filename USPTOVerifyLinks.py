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
import xml.etree.ElementTree as ET

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
        print("Verification tag count extraction failed for document type: " + args_array['uspto_xml_format'] + " filename: " + args_array['file_name'])
        logger.error("Verification tag count extraction for document type: " + args_array['uspto_xml_format'] + " filename: " + args_array['file_name'])
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
    # Store the exptected tag counts in database
    if counts_dict:
        file_processed_success = args_array['database_connection'].storeVerificationExtraction(counts_dict, args_array)
        # Log the file as verified
        if file_processed_success == True: USPTOLogger.write_verified_log(args_array)
        else:
            # Print to stdout and log
            print("The contents of: " + args_array['file_name'] + " could not be stored into the database! Time Finished: " + time.strftime("%c"))
            logger.error("The contents of: " + args_array['file_name'] + " could not be stored into the database! Time Finished: " + time.strftime("%c"))
    else:
        # Print to stdout and log
        print("The contents of: " + args_array['file_name'] + " could not be verified. Time Finished: " + time.strftime("%c"))
        logger.error("The contents of: " + args_array['file_name'] + " could not be verified. Time Finished: " + time.strftime("%c"))

    # Print to stdout and log
    print("- Finished the verificaction process for contents of: " + args_array['file_name'] + " Time Finished: " + time.strftime("%c"))
    logger.info("Finished the verification process for contents of: " + args_array['file_name'] + " Time Finished: " + time.strftime("%c"))

# Extract the tag count for APS grant files
def extract_APS_grant_tag_counts(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the .dat file from the .zip file
    data_file_contents = USPTOProcessZipFile.extract_dat_file_from_zip(args_array, True)

    # If xml_file_contents is None or False, then return False immediately
    if data_file_contents == None or data_file_contents == False:
        return False

    # Declare a dictionary to use in counting tags
    # NOTE: CPCClASS_G, APPLICANT_G, are not available in APS Grant files
    tags_dict = {
        "GRANT" : ["PATN"],
        "INTCLASS_G" : ["ICL"],
        "USCLASS_G" : ["UREF"],
        "INVENTOR_G" : ["INVT"],
        "AGENT_G" : ["FRM", "FR2", "ATT", "AGT", "ATT"],
        "ASSIGNEE_G" : ["ASSG"],
        "GRACIT_G" : ["UREF"],
        "NONPATCIT_G" : ["OREF"],
        "FORPATCIT_G" : ["FREF"],
        "EXAMINER_G" : ["EXP", "EXA"],
        "FOREIGNPRIORITY_G" : ["PRIR"]
    }
    sub_tags_dict = {
        "NONPATCIT_G" : ["PAL"]
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
    print("- Starting the APS grant tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))
    logger.info("Starting the APS grant tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for index, line in enumerate(data_file_contents, start=0):
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            item_found = False
            # Go through each table
            for item in tag:
                # Look for field tag
                if line.strip().startswith(item):
                    #print(table)
                    item_found = True
                    if table in sub_tags_dict:
                        #print("sub-tag-required")
                        sub_tag_exit = False
                        sub_tag_count = 0
                        # Create a subindex to iterate through
                        # next lines ahead in file content
                        sub_index = index + 1
                        #print(str(sub_index))
                        while sub_tag_exit == False:
                            sub_line = data_file_contents[sub_index]
                            #print(sub_line)
                            sub_index += 1
                            if sub_line[:4].strip() in sub_tags_dict[table]:
                                #print("add one")
                                sub_tag_count += 1
                            elif sub_line[:4].strip() != "":
                                sub_tag_exit = True
            if item_found == True:
                if table in sub_tags_dict:
                    # Increment the count calculated in sub_tag_required
                    counts_dict[table] += sub_tag_count
                # Increment the count for appropriate table
                else: counts_dict[table] += 1

    # Print to stdout and log
    print("- Finished the APS grant tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))
    logger.info("Finished the APS grant tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))

    # Return the dictionary of counts for found tags
    if args_array['stdout_level'] == 1: pprint(counts_dict)
    return counts_dict

# Extract the tag count for XML2 grant files
def extract_XML2_grant_tag_counts(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the XML file from the ZIP file
    xml_file_contents = USPTOProcessZipFile.extract_xml_file_from_zip(args_array)

    # If xml_file_contents is None or False, then return immediately
    if xml_file_contents == None or xml_file_contents == False:
        return False

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
    print("- Starting the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))
    logger.info("Starting the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            item_found = False
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        item_found = True
            if item_found == True:
                # Increment the count for appropriate table
                counts_dict[table] += 1

    # Count the items that cannot be counted by only tags
    # Parse the tags that need to be XML parsed
    # Create variables needed to parse the file
    xml_string = ''
    patent_xml_started = False
    # Loop through all lines in the xml file
    for line in xml_file_contents:

        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)

        # This identifies the start of well formed XML segment for patent
        # grant bibliographic information
        if "<PATDOC" in line:
            patent_xml_started = True
            xml_string += "<PATDOC>"

        # This identifies end of well-formed XML segement for single patent
        # grant bibliographic information
        elif "</PATDOC" in line:
            patent_xml_started = False
            xml_string += "</PATDOC>"
            #print(xml_string)
            # Pass the raw_data data into Element Tree
            try:
                document_root = ET.fromstring(xml_string)
                # SDOBI is the bibliographic data
                r = document_root.find('SDOBI')
                # Patent Citations
                B500 = r.find('B500')
                if B500 is not None:
                    for B560 in B500.findall('B560'):
                        # B561 is Patent Citation
                        for B561 in B560.findall('B561'):
                            try: pcit = B561.find('PCIT').find('DOC')
                            except: pcit = None
                            if pcit is not None:
                                prt = pcit.find('PARTY-US')
                                try: citation_state = USPTOSanitizer.return_element_text(prt.find('ADR').find('STATE')).strip()[:3]
                                except: citation_state = None
                                try: citation_country = USPTOSanitizer.return_element_text(prt.find("ADR").find('CTRY')).strip()[:3]
                                except:
                                    try:
                                        # If state is a US state, set country to US
                                        if USPTOSanitizer.is_US_state(citation_state):
                                            citation_country = "US"
                                        else: citation_country = None
                                    except: citation_country = None
                                if citation_country == "US" or citation_country == None: counts_dict['GRACIT_G'] += 1
                                elif citation_country is not None: counts_dict['FORPATCIT_G'] += 1
                # Reset the xml string
                xml_string = ''

            except ET.ParseError as e:
                print_xml = xml_string.split("\n")
                for num, line in enumerate(print_xml, start = 1):
                    #print(str(num) + ' : ' + line)
                    logger.error(str(num) + ' : ' + line)
                logger.error("Character Entity prevented ET from parsing XML in file: " + args_array['file_name'] )
                traceback.print_exc()
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())


        # This is used to append lines of file when inside single patent grant
        elif patent_xml_started == True:
            # Check which type of encoding should be used to fix the line string
            xml_string += USPTOSanitizer.replace_old_html_characters(line)

    # Print to stdout and log
    print("- Finished the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))
    logger.info("Finished the XML2 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))

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
        "AGENT_G" : ["<agent>", "<agent "],
        "ASSIGNEE_G" : ["<assignee>", "<assignee "],
        "APPLICANT_G" : ["<us-applicant>", "<us-applicant ", "<applicant", "<applicant>"],
        "INVENTOR_G" : ["<inventor>", "<inventor "],
        "NONPATCIT_G" : ["<nplcit"],
        "EXAMINER_G" : ["<primary-examiner", "<assistant-examiner"],
        "FOREIGNPRIORITY_G" : ["<priority-claim>", "<priority-claim "]
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
    print("- Starting the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))
    logger.info("Starting the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            item_found = False
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        item_found = True
            if item_found == True:
                # Increment the count for appropriate table
                counts_dict[table] += 1

    # Parse the tags that need to be XML parsed
    # Create variables needed to parse the file
    xml_string = ''
    patent_xml_started = False
    # Loop through all lines in the xml file
    for line in xml_file_contents:

        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)

        # This identifies the start of well formed XML segment for patent
        # grant bibliographic information
        if "<us-patent-grant" in line:
            patent_xml_started = True
            xml_string += "<us-patent-grant>"

        # This identifies end of well-formed XML segement for single patent
        # grant bibliographic information
        elif "</us-patent-grant" in line:
            patent_xml_started = False
            xml_string += "</us-patent-grant>"
            #print(xml_string)
            # Pass the raw_data data into Element Tree
            document_root = ET.fromstring(xml_string)
            #print(document_root)
            # Extract the root tag
            r = document_root.find('us-bibliographic-data-grant')
            # Get the patent CPC class count
            foc = r.find('us-field-of-classification-search')
            if foc is not None:
                counts_dict["CPCCLASS_G"] += len(foc.findall('classification-cpc-text'))
                counts_dict["USCLASS_G"] += len(foc.findall('classification-national'))
            # Count the citation / reference tags
            if r.find('us-references-cited') != None: ref_cited_id_string = "us-references-cited"
            elif r.find('references-cited') != None: ref_cited_id_string = "references-cited"
            else: ref_cited_id_string = "references"
            rf = r.find(ref_cited_id_string)
            if rf != None:
                # Check if the XML format is using 'citation' or 'us-citation'
                if rf.find('citation') != None: citation_id_string = "citation"
                elif rf.find('us-citation') != None: citation_id_string = "us-citation"
                else: citation_id_string = "us-citation"
                all_rfc = rf.findall(citation_id_string)
                for rfc in all_rfc:
                    # If the patent citation child is found must be a patent citation
                    if rfc.find('patcit') != None:
                        x = rfc.find('patcit')
                        try: citation_country = x.find('document-id').findtext('country').strip()
                        except: citation_country = None
                        # Check if US or foreign patent citation
                        if(citation_country == 'US'): counts_dict["GRACIT_G"] += 1
                        else: counts_dict["FORPATCIT_G"] += 1
            # Count the foreign patent citiation tags
            # Reset the xml string
            xml_string = ''

        # This is used to append lines of file when inside single patent grant
        elif patent_xml_started == True:
            # Check which type of encoding should be used to fix the line string
            xml_string += line


    # Print to stdout and log
    print("- Finished the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))
    logger.info("Finished the XML4 grant tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))

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
    #CPCCLASS_A and APPLICANT_A are not included in XML1 applications
    # APPLICANT_A are not include in XML1 applications
    tags_dict = {
        "APPLICATION" : ["<patent-application-publication"],
        "INTCLASS_A" : ["<classification-ipc-primary>", "<classification-ipc-secondary>"],
        "USCLASS_A" : ["<classification-us-primary>", "<classification-us-secondary>"],
        "FOREIGNPRIORITY_A" : ["<priority-application-number"],
        "AGENT_A" : ["<correspondence-address>"],
        "INVENTOR_A" : ["<first-named-inventor", "<inventor>"],
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
    print("- Starting the XML1 application tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))
    logger.info("Starting the XML1 application tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            item_found = False
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        item_found = True
            if item_found == True:
                # Increment the count for appropriate table
                counts_dict[table] += 1

    # Parse the tags that need to be XML parsed
    # Create variables needed to parse the file
    xml_string = ''
    patent_xml_started = False
    # Loop through all lines in the xml file
    for line in xml_file_contents:

        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)

        # This identifies the start of well formed XML segment for patent
        # grant bibliographic information
        if "<patent-application-publication" in line:
            patent_xml_started = True
            xml_string += "<patent-application-publication>"

        # This identifies end of well-formed XML segement for single patent
        # grant bibliographic information
        elif "</patent-application-publication" in line:
            patent_xml_started = False
            xml_string += "</patent-application-publication>"
            #print(xml_string)
            # Pass the raw_data data into Element Tree
            document_root = ET.fromstring(xml_string)
            #print(document_root)
            # Extract the root tag
            r = document_root.find('subdoc-bibliographic-information')
            # Count the number of assignee tags
            counts_dict['ASSIGNEE_A'] += len(r.findall('assignee'))
            # Count the number of inventor tags
            counts_dict['INVENTOR_A'] += len(r.findall('inventor'))
            # Reset the xml string
            xml_string = ''

        # This is used to append lines of file when inside single patent grant
        elif patent_xml_started == True:
            # Check which type of encoding should be used to fix the line string
            xml_string += USPTOSanitizer.replace_old_html_characters(line)

    # Print to stdout and log
    print("- Finished the XML1 appication tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))
    logger.info("Finished the XML1 application tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))
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
        "FOREIGNPRIORITY_A" : ["<priority-claim>", "<priority-claim "],
        "AGENT_A" : ["<agent>", "<agent "],
        "ASSIGNEE_A" : ["<assignee>", "<assignee "],
        "INVENTOR_A" : ["<inventor>", "<inventor "],
        "APPLICANT_A" : ["<us-applicant>", "<applicant>", "<us-applicant ", "<applicant "]
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
    print("- Starting the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))
    logger.info("Starting the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Time Started: " + time.strftime("%c"))

    # Loop through the file contents line by line
    for line in xml_file_contents:
        # Decode the line from byte-object
        line = USPTOSanitizer.decode_line(line)
        # Loop through tags_dict items and look for XML tag
        for table, tag in tags_dict.items():
            item_found = False
            # If list is provided
            if isinstance(tag, list):
                for item in tag:
                    # Look for field tag
                    if item in line:
                        item_found = True
            if item_found == True:
                # Increment the count for appropriate table
                counts_dict[table] += 1

    # Print to stdout and log
    print("- Finished the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))
    logger.info("Finished the XML4 application tag counting process for contents of: " + args_array['file_name'] + ". Time Finished: " + time.strftime("%c"))
    # Return the dictionary of counts for found tags
    if args_array['stdout_level'] == 1: pprint(counts_dict)

    # Return the dictionary of counts for found tags
    return counts_dict

# Extract the tag count for legal data files
def extract_legal_counts(args_array):
    # Get the expected count of records from file
    expected_count = get_file_length(file_name, args_array)

# Extract the tag count for PAIR data files
def extract_PAIR_counts(args_array):
    # Get the expected count of records from file
    expected_count = get_file_length(file_name, args_array)

# Extract the tag count for CPC classification data files
def extract_CPC_class_counts(args_array):
    # Get the expected count of records from file
    expected_count = get_file_length(file_name, args_array)

# Extract the tag count for US classification data files
def extract_US_class_counts(args_array):
    # Get the expected count of records from file
    expected_count = get_file_length(file_name, args_array)

# Extract the tag count for CPC / US class concordance data files
def extract_USCPC_class_counts(args_array):
    # Get the expected count of records from file
    expected_count = get_file_length(file_name, args_array)

# Gets the number of lines of CSV content in file
def get_file_length(file_name, args_array):
    pass
