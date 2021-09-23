# USPTOProcessAPSGrant.py
# USPTO Bulk Data Parser - Process APS Grants
# Description: Imported to the main USPTOParser.py.  Processes APS Grant data for database and CSV.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# Import python Modules
import time
import traceback
import os
import sys

# Import USPTO Parser Functions
import USPTOLogger
import USPTOCSVHandler
import USPTOSanitizer
import USPTOProcessZipFile
import USPTOStoreGrantData

# Used to parse xml files of the type APS
def process_APS_grant_content(args_array):

    #
    # Documentation about the APS format can be found in the
    # /documents/data_descriptions/PatentFullTextAPSGreenBook-Documentation.pdf file

    # Set the start time of the process
    start_time = time.time()
    # Import logger
    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # If csv file insertion is required, then open all the files
    if "csv" in args_array['command_args'] or ("database" in args_array['command_args'] and args_array['database_insert_mode'] == "bulk"):
        args_array['csv_file_array'] = USPTOCSVHandler.open_csv_files(args_array['document_type'], args_array['file_name'], args_array['csv_directory'])

    # Colect arguments from args array
    url_link = args_array['url_link']
    uspto_xml_format = args_array['uspto_xml_format']

    # Define all arrays to hold the data
    processed_grant = []
    processed_applicant = []
    processed_examiner = []
    processed_assignee = []
    processed_agent = []
    processed_inventor = []
    processed_usclass = []
    processed_intclass = []
    processed_gracit = []
    processed_forpatcit = []
    processed_nonpatcit = []
    processed_foreignpriority = []

    # Extract the .dat file from the .zip file
    data_file_contents = USPTOProcessZipFile.extract_dat_file_from_zip(args_array)

    # If xml_file_contents is None or False, then return False immediately
    if data_file_contents == None or data_file_contents == False:
        return False

    # Define variables required to parse the file
    is_first_patent_tag = True
    next_line_loaded_already = False
    end_of_file = False
    insert_final = False
    total_patents_found = 0

    # Start to read the file in lines
    while end_of_file == False:

        # Read a single line if there is no line content then load another line
        if next_line_loaded_already == False:
            # Load the next line
            try:
                line = data_file_contents.readline()
                # If not line, set flag to insert last item
                if not line: insert_final = True;
            except Exception as e:
                line = data_file_contents.readline()
                if not line: insert_final = True;
                traceback.print_exc()
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

        # Initialize next line is not loaded
        next_line_loaded_already = False

        # If EOF then append last patent grant
        if insert_final:

            # Set flag to end the while loop
            end_of_file = True
            # Store the final patent file for the data

            # Check if variable exists for abstract, claims and
            # description and create if not set already
            if 'abstract' not in locals(): abstract = None
            if 'claims' not in locals(): claims = None
            if 'description' not in locals(): description = None
            if 'grant_length' not in locals(): grant_length = None
            if 'app_type' not in locals(): app_type = None
            if 'kind' not in locals(): kind = None

            # Append to the patent grand data
            processed_grant.append({
                "table_name" : "uspto.GRANT",
                "GrantID" : document_id,
                "Title" :  title,
                "IssueDate" : pub_date,
                "FileDate" : app_date,
                "Kind" : kind,
                "AppType": app_type,
                "USSeriesCode" : series_code,
                "Abstract" : abstract,
                "ClaimsNum" : claims_num,
                "DrawingsNum" : number_of_drawings,
                "FiguresNum" : number_of_figures,
                "ApplicationID" : app_no,
                "Description" : description,
                "Claims" : claims,
                "GrantLength" : grant_length,
                "FileName" : args_array['file_name']
            })

            # Append to the processed data array
            processed_data_array = {
                "processed_grant" : processed_grant,
                "processed_applicant" : processed_applicant,
                "processed_examiner" : processed_examiner,
                "processed_assignee" : processed_assignee,
                "processed_agent" : processed_agent,
                "processed_inventor" : processed_inventor,
                "processed_usclass" : processed_usclass,
                "processed_intclass" : processed_intclass,
                "processed_gracit" : processed_gracit,
                "processed_forpatcit" : processed_forpatcit,
                "processed_nonpatcit" : processed_nonpatcit,
                "processed_foreignpriority" : processed_foreignpriority
            }

            # Call function to write data to csv or database
            USPTOStoreGrantData.store_grant_data(processed_data_array, args_array)

        # IF not EOF then strip the line
        else:
            line = line.strip()

        # If the line is start of a patent document
        if line == "PATN":

            total_patents_found += 1
            # Initialize the position variables required for classification
            # NOTE: this is because there seems to be a rare anomoly of Records
            # having more than one CLAS tag, otherwise it could be set after the
            # CLAS tag was found.  Else, it's because a patent had 2 separate Records
            # one after the other.
            position_usclass = 1
            position_intclass = 1
            position_uref = 1
            position_oref = 1
            position_forpat = 1
            position_inventor = 1
            position_assignee = 1
            position_agent = 1
            position_prior = 1

            # If it is not the first patent, then store the previous patent
            if is_first_patent_tag == False:

                # Check if variable exists for abstract, claims and
                # description and create if not set already
                if 'abstract' not in locals(): abstract = None
                if 'claims' not in locals(): claims = None
                if 'description' not in locals(): description = None
                if 'grant_length' not in locals(): grant_length = None
                if 'app_type' not in locals(): app_type = None
                if 'kind' not in locals(): kind = None

                # Append to the patent grand data
                processed_grant.append({
                    "table_name" : "uspto.GRANT",
                    "GrantID" : document_id,
                    "Title" :  title,
                    "IssueDate" : pub_date,
                    "FileDate" : app_date,
                    "Kind" : kind,
                    "AppType": app_type,
                    "USSeriesCode" : series_code,
                    "Abstract" : abstract,
                    "ClaimsNum" : claims_num,
                    "DrawingsNum" : number_of_drawings,
                    "FiguresNum" : number_of_figures,
                    "ApplicationID" : app_no,
                    "Description" : description,
                    "Claims" : claims,
                    "GrantLength" : grant_length,
                    "FileName" : args_array['file_name']
                })
                #print(processed_grant)

                # Reset all variables required to store data to avoid overlap
                document_id = None
                title = None
                pub_date = None
                app_date = None
                kind = None
                app_type = None
                series_code = None
                abstract = None
                claims = None
                description = None
                claims_num = None
                number_of_drawings = None
                number_of_figures = None
                app_no = None
                grant_length = None

                # Append to the processed data array
                processed_data_array = {
                    "processed_grant" : processed_grant,
                    "processed_applicant" : processed_applicant,
                    "processed_examiner" : processed_examiner,
                    "processed_assignee" : processed_assignee,
                    "processed_agent" : processed_agent,
                    "processed_inventor" : processed_inventor,
                    "processed_usclass" : processed_usclass,
                    "processed_intclass" : processed_intclass,
                    "processed_gracit" : processed_gracit,
                    "processed_forpatcit" : processed_forpatcit,
                    "processed_nonpatcit" : processed_nonpatcit,
                    "processed_foreignpriority" : processed_foreignpriority
                }
                #print(processed_data_array)

                # Call function to write data to csv or database
                USPTOStoreGrantData.store_grant_data(processed_data_array, args_array)

                # Reset all arrays to hold the item data
                processed_grant = []
                processed_applicant = []
                processed_examiner = []
                processed_assignee = []
                processed_agent = []
                processed_inventor = []
                processed_usclass = []
                processed_intclass = []
                processed_gracit = []
                processed_forpatcit = []
                processed_nonpatcit = []
                processed_foreignpriority = []

            # If first line found that starts a patent set flag to true
            else:
                is_first_patent_tag = False

        # If new patent line was not found, expect other data elements to be found.
        # Check for a data-field header.  If found, then collect the data for
        # that field and if required load new lines until field section parsed.

        # WKU is Patent Number
        elif line[0:3].strip() == "WKU":
            document_id = None
            try: document_id = USPTOSanitizer.fix_APS_patent_number(args_array, USPTOSanitizer.fix_patent_number(USPTOSanitizer.replace_old_html_characters(line[3:].strip())))
            except:
                document_id = None
                logger.error("No patent number found for patent from this url: " + args_array["url_link"])
        # SRC is Series Code
        elif line[0:3].strip() == "SRC":
            try: series_code = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:2]
            except: series_code = None
        # APT is Application type
        elif line[0:3].strip() == "APT":
            try: app_type = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:2]
            except: app_type = None
        # NCL is Number of Claims
        elif line[0:3].strip() == "NCL":
            try: claims_num = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(",")[0]
            except: claims_num = None
        # ISD is Publication Date
        elif line[0:3].strip() == "ISD":
            try: pub_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.replace_old_html_characters(line[3:].strip()), args_array, document_id)
            except: pub_date = None
        # APN is Application Number
        elif line[0:3].strip() == "APN":
            try: app_no = USPTOSanitizer.fix_patent_number(USPTOSanitizer.replace_old_html_characters(line[3:].strip()))[:20]
            except: app_no = None
        # APD is Application date
        elif line[0:3].strip() == "APD":
            try: app_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.replace_old_html_characters(line[3:].strip()), args_array, document_id)
            except: app_date = None
        # TTL is title
        elif line[0:4].strip() == "TTL":
            try: title = USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:500])
            except: title = None

            # TTL can be multi-line, so load next line and
            # check if should be appended or not
            line = data_file_contents.readline()
            if not line: insert_final = True;
            else:
                # Check if line has empty header
                if not line[0:3]:
                    # Append the TTL to the title variable above if empty header
                    title += USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:500]) + " "
                # Check if the loaded next line is the next expected header
                elif line[0:4].strip() == "ISD":
                    # Set that the next line has been loaded already
                    # so it won't be skipped
                    next_line_loaded_already = True
        # NDR is Number of Drawings
        elif line[0:3].strip() == "NDR":
            try:
                number_of_drawings = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(",")[0].replace(" ", "").strip()
                number_of_drawings = number_of_drawings.split("/")[0]
            except: number_of_drawings = None
        # NFG Number of Figures
        elif line[0:4].strip() == "NFG":
            try: number_of_figures = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(",")[0].replace(" ", "").strip()
            except: number_of_drawings = None
        # TRM is Term length of patent
        elif line[0:4].strip() == "TRM":
            try: grant_length = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(",")[0].replace(" ", "").strip()
            except: grant_length = None
            # NOTE: (could name database column decimal) If grant length is decimal value, then
            if "." in grant_length:
                grant_length = grant_length.split(".")[0].strip()

        # EXA is Assistant Examiner
        elif line[0:4].strip() == "EXA":
            try:
                assistant_examiner = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(";")
                examiner_last_name = assistant_examiner[0][:50].strip()
                examiner_first_name = assistant_examiner[1][:50].strip()
            except:
                examiner_first_name = None
                examiner_last_name = None

            # Append data into dictionary to be written later
            processed_examiner.append({
                "table_name" : "uspto.EXAMINER_G",
                "GrantID" : document_id,
                "Position" : 2,
                "LastName" : examiner_last_name,
                "FirstName" : examiner_first_name,
                "Department" : None,
                "FileName" : args_array['file_name']
            })
            #print(processed_examiner)
            # Reset all the variables to avoid overlap
            examiner_last_name = None
            examiner_first_name = None

        # EXP is Primary Examiner
        elif line[0:4].strip() == "EXP":

            examiner_fist_name = None
            examiner_last_name = None
            try:
                primary_examiner = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(";")
                examiner_last_name = primary_examiner[0][:50].strip()
                examiner_first_name = primary_examiner[1][:50].strip()
            except:
                examiner_last_name = None
                examiner_first_name = None

            # Append data into dictionary to be written later
            processed_examiner.append({
                "table_name" : "uspto.EXAMINER_G",
                "GrantID" : document_id,
                "Position" : 1,
                "LastName" : examiner_last_name,
                "FirstName" : examiner_first_name,
                "Department" : None,
                "FileName" : args_array['file_name']
            })
            #print(processed_examiner)
            # Reset all variables to avoid overlap
            examiner_first_name = None
            examiner_last_name = None

        # UREF is USPTO Reference
        elif line[0:4] == "UREF":
            # This header type  has no data on same line but will include further
            # readlines so read another line in a while loop until you finish with foreign references
            # and when non-foreign nonreference is found set a flag that prevents another line from being
            # read next iteration through main loop

            # Set accepted DAT headers
            accepted_headers_array = ["UREF", "OCL", "PNO", "ISD", "NAM", "OCL", "XCL", "UCL"]
            # Set a flag that the UREF tag has not finished
            data_parse_completed = False
            item_ready_to_insert = False

            while data_parse_completed == False:

                # Read next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # If line is represents another foreign reference, store the last one into array
                    if line[0:4] == "UREF":

                        # The data collection is complete and should be appended
                        if item_ready_to_insert == True:

                            # Try to append the item.  If items are missinng it will not append
                            # and error will be written to log
                            try:
                                # Append data into dictionary to be written later
                                processed_gracit.append({
                                    "table_name" : "uspto.GRACIT_G",
                                    "GrantID" : document_id,
                                    "Position" : position_uref,
                                    "CitedID" : citation_document_number,
                                    "Name" : citation_name,
                                    "Date" : citation_date,
                                    "Country" : "US",
                                    "FileName" : args_array['file_name']
                                })
                                #print(processed_gracit)
                                position_uref += 1
                                # Reset all variables to avoid overlap
                                citation_document_number = None
                                citation_name = None
                                citation_date = None
                                # Reset the item ready to insert
                                item_ready_to_insert = False

                            except Exception as e:
                                # Reset the item ready to insert
                                item_ready_to_insert = False
                                print("Data missing from patent references for grant id : " + document_id + " in url: " + args_array['url_links'])
                                logger.error("Some data was missing from the patent reference data for grant id: " + document_id + " in url: " + args_array['url_link'])

                    # CitedID
                    elif line[0:3] == "PNO":
                        try: citation_document_number = USPTOSanitizer.fix_patent_number(USPTOSanitizer.replace_old_html_characters(line[3:].strip().replace("*", "").replace(" ", "")))[:20].strip()
                        except: citation_document_number = None
                    # Issue Date of cited patent
                    elif line[0:3] == "ISD":
                        try: citation_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.replace_old_html_characters(line[3:].strip()), args_array, document_id)
                        except: citation_date = None
                    # Name of patentee
                    elif line[0:3] == "NAM":
                        try:
                            citation_name = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:100].strip()
                            item_ready_to_insert = True
                        except:
                            citation_name = None
                            item_ready_to_insert = True

                    # Catch the tag of next header but not empty line
                    elif line[0:4].strip() not in accepted_headers_array:

                        # Append final UREF to gracit items array
                        processed_gracit.append({
                            "table_name" : "uspto.GRACIT_G",
                            "GrantID" : document_id,
                            "Position" : position_uref,
                            "CitedID" : citation_document_number,
                            "Name" : citation_name,
                            "Date" : citation_date,
                            "Country" : "US",
                            "FileName" : args_array['file_name']
                        })
                        # Reset all variables to avoid overlap
                        citation_document_number = None
                        citation_name = None
                        citation_date = None
                        # Reset the item ready to insert
                        item_ready_to_insert = False
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True

        # OREF is Other References
        elif line[0:4] == "OREF":
            # Define the accepted headers in this section
            accepted_headers_array = ["PAL"]
            # Initialize empty string to to hold multi-line entries
            temp_data_string = ''
            # End while loop
            data_parse_completed = False

            # Loop through all OREF until finished
            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # If line is represents another foreign reference, store the last one into array
                    if line[0:3] == "PAL":

                        # If the temp_data_string is not empty then append that record
                        if temp_data_string:

                            # Append data into dictionary to be written later
                            processed_nonpatcit.append({
                                "table_name" : "uspto.NONPATCIT_G",
                                "GrantID" : document_id,
                                "Position" : position_oref,
                                "Citation" : USPTOSanitizer.strip_for_csv(temp_data_string),
                                "Category" : None,
                                "FileName" : args_array['file_name']
                            })
                            #print(processed_nonpatcit)
                            position_oref += 1
                            # Reset variable to avoid overlap
                            temp_data_string = None
                            # Set the temp_data_string back to empty
                            temp_data_string = ''

                        # The PAL header was found and temp_data_string is empty.
                        # Try to collect the PAL data
                        else:

                            # Get the citation text from the PAL line
                            try: temp_data_string += USPTOSanitizer.replace_old_html_characters(line[3:].strip())
                            except:
                                logger.error("A non patent reference could not be found for grant_id: " + document_id + " in link: " + args_array['url_link'])
                                temp_data_string = ''

                    # Catch the tag of next header but not empty line
                    elif not line[0].strip():
                        # Append the continued reference text to temp string
                        try: temp_data_string += USPTOSanitizer.replace_old_html_characters(line[3:].strip())
                        except Exception as e:
                            logger.error("A non patent reference could not be appended for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # If the next element in the document is found
                    elif line[0:4].strip() not in accepted_headers_array:

                        # Complete a final append to the other referenes array
                        # Append data into dictionary to be written later
                        processed_nonpatcit.append({
                            "table_name" : "uspto.NONPATCIT_G",
                            "GrantID" : document_id,
                            "Position" : position_oref,
                            "Citation" : temp_data_string,
                            "Category" : None,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_nonpatcit)
                        position_oref += 1
                        # Reset variable to avoid overlap
                        temp_data_string = None
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # End while loop
                        data_parse_completed = True

        # FREF is Foreign Reference
        elif line[0:4] == "FREF":
            # This header type  has no data on same line but will include further
            # readlines so read another line in a while loop until you finish with foreign references
            # and when non-foreign nonreference is found set a flag that prevents another line from being
            # read next iteration through main loop
            accepted_headers_array = ["FREF", "PNO", "ISD", "CNT", "ICL", "OCL"]

            # Init while loop break
            data_parse_completed = False

            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # If line is represents another foreign reference, store the last one into array
                    if line[0:4] == "FREF":

                        # The data collection is complete and should be appended
                        if item_ready_to_insert == True:

                            # Try to append the item.  If items are missingn it will not append
                            # and error will be written to log
                            try:
                                # Append data into dictionary to be written later
                                processed_forpatcit.append({
                                    "table_name" : "uspto.FORPATCIT_G",
                                    "GrantID" : document_id,
                                    "Position" : position_forpat,
                                    "CitedID" : citation_document_number,
                                    "Date" : citation_date,
                                    "Country" : citation_country,
                                    "FileName" : args_array['file_name']
                                })
                                #print(processed_forpatcit)
                                position_forpat += 1
                                # Reset variable to avoid overlap
                                citation_document_number = None
                                citation_date = None
                                citation_country = None
                                # Reset the item ready to insert
                                item_ready_to_insert = False

                            except Exception as e:
                                print("Data missing from foreign references for grant id : " + document_id + " in url: " + args_array['url_links'])
                                logger.error("Some data was missing from the Foreign reference data for grant id: " + document_id + " in url: " + args_array['url_link'])
                                # Reset the item ready to insert
                                item_ready_to_insert = False

                    elif line[0:3] == "PNO":
                        citation_document_number = None
                        try: citation_document_number = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:25]
                        except: citation_document_number = None
                    elif line[0:3] == "ISD":
                        citation_date = None
                        try: citation_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.replace_old_html_characters(line[3:].strip()), args_array, document_id)
                        except: citation_date = None
                    elif line[0:3] == "CNT":
                        citation_country = None
                        # Country is the last item included in APS so item is ready to be inserted after this is found
                        try:
                            citation_country = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:100]
                            item_ready_to_insert = True
                        except:
                            citation_country = None
                            item_ready_to_insert = True

                    # If the tag found is not for FREF data, new data set found.
                    elif line[0:4].strip() not in accepted_headers_array:

                        # Append data into dictionary to be written later
                        processed_forpatcit.append({
                            "table_name" : "uspto.FORPATCIT_G",
                            "GrantID" : document_id,
                            "Position" : position_forpat,
                            "CitedID" : citation_document_number,
                            "Date" : citation_date,
                            "Country" : citation_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_forpatcit)
                        position_forpat += 1
                        # Reset variable to avoid overlap
                        citation_document_number = None
                        citation_date = None
                        citation_country = None
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True

        # CLAS is Classification Data
        elif line[0:4] == "CLAS":
            # Define accepted array headers for this section
            accepted_headers_array = ["OCL", "XCL", "UCL", "DCL", "EDF", "ICL", "FSC", "FSS"]
            # Set the variable that will certainly not be found
            i_class_mgr = None
            i_class_sgr = None
            # Initialize empty string to to hold multi-line entries
            temp_data_string = ''
            # Set flag for while loop
            data_parse_completed = False
            # Set the malformmed_class variable used to find erroneos classes
            malformed_class = 0

            # Loop through all OREF until finished
            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # Collect the main class
                    if line[0:3] == "OCL":

                        # Get the citation text from the line
                        try:
                            class_string = USPTOSanitizer.replace_old_html_characters(line[3:].strip().replace("  ", " ")).split(" ")
                            #print "Original class_string array: "
                            #print class_string
                            #print "Class string found in patent: " + document_id + " class:" + str(class_string[0]) + " substring: " + str(class_string[1])
                            #logger.warning("Class string found in patent: " + document_id + " class:" + str(class_string[0]) + " substring: " + str(class_string[1]))
                            # If the class string's length is 6, then assumed that needs to be parsed further.
                            if len(class_string) == 1:
                                if len(str(class_string[0])) >= 4 and len(str(class_string[0])) <= 12 :
                                    class_string = USPTOSanitizer.fix_old_APS_class(str(class_string[0]))

                                    # Set the returned array to insert data vaiables
                                    n_class_main = class_string[0][:5]
                                    n_subclass = class_string[1][:15]

                                    # If the class is malformed than set variable to = 1
                                    if "MAL" in class_string:
                                        malformed_class = 1

                            elif len(class_string) == 2:
                                if len(class_string[0]) > 3:
                                    n_class_main = class_string[0][:3]
                                    n_subclass = class_string[0][3:len(class_string)] + class_string[1]
                                    n_subclass = n_subclass[:15]
                                else:
                                    n_class_main = class_string[0][:5]
                                    n_subclass = class_string[1][:15]

                            elif len(class_string) == 3:
                                n_class_main = class_string[0][:5]
                                n_subclass = class_string[1] + " " + class_string[2]
                                n_subclass = n_subclass[:15]
                                malformed_class = 1
                            else:
                                logger.warning("A mal-formed US OCL class was found with more than one space: " + document_id + " in link: " + args_array['url_link'])

                        except Exception as e:
                            # Print exception information to file
                            traceback.print_exc()
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                            n_class_main = None
                            n_subclass = None
                            logger.error("An OCL classification error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                        # Append data into dictionary to be written later
                        processed_usclass.append({
                            "table_name" : "uspto.USCLASS_G",
                            "GrantID" : document_id,
                            "Position" : position_usclass,
                            "Class" : n_class_main,
                            "SubClass" : n_subclass,
                            "Malformed" : malformed_class,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_usclass)
                        position_usclass += 1
                        # Reset the class and subclass
                        class_string = None
                        n_class_main = None
                        n_subclass = None
                        malformed_class = 0

                    # Collect the extra class believed to be in INT class format space separated on a single lineself.
                    # if processed needs to be separated on space character and joined in groups of two.
                    '''if line[0:3] == "XCL":

                        # Get the US class text from the line
                        try:
                            class_string = USPTOSanitizer.replace_old_html_characters(line[3:].strip().replace("  ", " ")).split(" ")
                            #print "Class string found in patent: " + document_id + " class:" + str(class_string[0]) + " substring: " + str(class_string[1])
                            #logger.warning("Class string found in patent: " + document_id + " class:" + str(class_string[0]) + " substring: " + str(class_string[1]))
                            # If the class string's length is 6, then assumed that needs to be parsed further.

                            if len(class_string) == 1:
                                if len(str(class_string[0])) >= 4 and len(str(class_string[0])) <= 12 :
                                    class_string = USPTOSanitizer.fix_old_APS_class(str(class_string[0]))

                                    # Set the returned array to insert data vaiables
                                    n_class_main = class_string[0][:5]
                                    n_subclass = class_string[1][:15]

                                    # if the class is malformed than set variable to = 1
                                    if "MAL" in class_string:
                                        malformed_class = 1

                            elif len(class_string) == 2:
                                if len(class_string[0]) > 3:
                                    n_class_main = class_string[0][:3]
                                    n_subclass = class_string[0][3:len(class_string)] + class_string[1]
                                    n_subclass = n_subclass[:15]
                                else:
                                    n_class_main = class_string[0][:5]
                                    n_subclass = class_string[1]
                            elif len(class_string) == 3:
                                n_class_main = class_string[0]
                                n_subclass = class_string[1] + " " + class_string[2]
                                n_subclass = n_subclass[:15]
                                malformed_class = 1
                            else:

                                logger.warning("A mal-formed US XCL class was found with more than two spaces: " + document_id + " in link: " + args_array['url_link'])

                            # if the class is malformed than set variable to = 1
                            if "MAL" in class_string:
                                malformed_class = 1

                        except:
                            # Print exception information to file
                            traceback.print_exc()
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                            n_class_main = None
                            n_subclass = None
                            logger.error("An XCL classification error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                        # Append data into dictionary to be written later
                        processed_usclass.append({
                            "table_name" : "uspto.USCLASS_G",
                            "GrantID" : document_id,
                            "Position" : position_usclass,
                            "Class" : n_class_main,
                            "SubClass" : n_subclass,
                            "Malformed" : malformed_class,
                            "FileName" : args_array['file_name']
                        })

                        # Reset the class and subclass
                        class_string = None
                        n_class_main = None
                        n_subclass = None
                        malformed_class = 0

                        #print processed_usclass

                        # Increment position for US class
                        position_usclass += 1 '''

                    # Collect the Main International Class
                    if line[0:3] == "ICL":

                        # Get the international class text from the line
                        # Documentation found in PatentFullTextAPSGreenBook.pdf page 90.
                        # TODO: find out how to parse the int class code.
                        try:
                            #i_class_string = USPTOSanitizer.replace_old_html_characters(line[3:].strip().replace("  ", " ")).split(" ")
                            i_class_string = USPTOSanitizer.replace_old_html_characters(line[3:].strip())
                            #i_class_sring = i_class_string.replace(" ", "")
                        except:
                            # Print exception information to file
                            traceback.print_exc()
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                            logger.error("An International classification error occurred that could not be extracted for grant_id: " + document_id + " in link: " + args_array['url_link'])
                            i_section = None
                            i_class_main = None
                            i_subclass = None
                            i_class_mgr = None
                            i_class_sgr = None
                            malformed_class = 1

                        try:
                            # If there length for a maingroup or subgroup
                            if len(i_class_string) >= 6:
                                i_section = i_class_string[0]
                                i_class_main = i_class_string[1:3]
                                i_subclass = i_class_string[3]
                                # The group string is
                                group_string = i_class_string[4:]
                                # If there is a space separating group and subgroup
                                if len(group_string) >= 4:
                                    i_class_mgr = group_string[:3].strip()
                                    i_class_sgr = group_string[3:].strip()
                                # If no space in
                                else:
                                    i_class_mgr = group_string.strip()
                                    i_class_sgr = None
                                    malformed_class = 1
                                    logger.warning("A mal-formed international class with no subgroup was found (" + ' '.join(i_class_string) + ") with more than two spaces: " + document_id + " in link: " + args_array['url_link'])
                            # The class is malformed
                            else:
                                i_section = None
                                i_class_main = None
                                i_subclass = None
                                i_class_mgr = None
                                i_class_sgr = None
                                malformed_class = 1
                                #logger.warning("A mal-formed international class was found (" + ' '.join(i_class_string) + ") with more than two spaces: " + document_id + " in link: " + args_array['url_link'])
                        except:
                            # Print exception information to file
                            traceback.print_exc()
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                            logger.error("An International classification error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])
                            i_section = None
                            i_class_main = None
                            i_subclass = None
                            i_class_mgr = None
                            i_class_sgr = None
                            malformed_class = 1


                        # TODO: find out if field of search is same as Main Group, etc.
                        # Append data into dictionary to be written later
                        processed_intclass.append({
                            "table_name" : "uspto.INTCLASS_G",
                            "GrantID" : document_id,
                            "Position" : position_intclass,
                            "Section" : i_section,
                            "Class" : i_class_main,
                            "SubClass" : i_subclass,
                            "MainGroup" : i_class_mgr,
                            "SubGroup" : i_class_sgr,
                            "Malformed" : malformed_class,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_intclass)
                        position_intclass += 1
                        # Reset the class and subclass
                        i_class_string = None
                        i_section = None
                        i_class_main = None
                        i_subclass = None
                        i_class_mgr = None
                        i_class_sgr = None
                        malformed_class = 0

                    # Looking for next line in reference, id'd by not empty temp_data_string and not empty line
                    elif line.strip() and temp_data_string != '':
                        # Append the continued reference text to temp string
                        try: temp_data_string += USPTOSanitizer.replace_old_html_characters(line[3:].strip())
                        except Exception as e:
                            logger.error("A international class reference could not be appended for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # If the next element in the document is found
                    elif line[0:4].strip() not in accepted_headers_array:

                        # End while loop
                        data_parse_completed = True
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop


        # PRIR is Foreign Priority
        elif line[0:4] == "PRIR":
            # This header type  has no data on same line but will include further
            # readlines so read another line in a while loop until you finish with foreign references
            # and when non-foreign nonreference is found set a flag that prevents another line from being
            # read next iteration through main loop

            # Set accepted DAT headers
            accepted_headers_array = ["PRIR", "CNT", "APD", "APN"]
            # Set a flag that the UREF tag has not finished
            data_parse_completed = False
            item_ready_to_insert = False

            # Set pc_kind = None because it's not included in APS
            pc_kind = None

            while data_parse_completed == False:
                # Read next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # If line is represents another foreign priority document, store the last one into array
                    if line[0:4] == "PRIR":

                        # The data collection is complete and should be appended
                        if item_ready_to_insert == True:

                            # Try to append the item.  If items are missinng it will not append
                            # and error will be written to log
                            try:
                                # Append data into dictionary to be written later
                                processed_foreignpriority.append({
                                    "table_name" : "uspto.FOREIGNPRIORITY_G",
                                    "GrantID" : document_id,
                                    "Position" : position_prior,
                                    "Kind" : pc_kind,
                                    "Country" : pc_country,
                                    "DocumentID" : pc_doc_num,
                                    "PriorityDate" : pc_date,
                                    "FileName" : args_array['file_name']
                                })
                                #print(processed_foreignpriority)
                                position_prior += 1
                                # Reset all variables to avoid overlap
                                pc_country = None
                                pc_doc_num = None
                                pc_date = None
                                # Reset the item ready to insert
                                item_ready_to_insert = False

                            except Exception as e:
                                # Reset the item ready to insert
                                item_ready_to_insert = False
                                print("Data missing from APS foreign priority for grant id : " + document_id + " in url: " + args_array['url_links'])
                                logger.error("Some data was missing from the APS foreign priority data for grant id: " + document_id + " in url: " + args_array['url_link'])

                    # Priority Country
                    elif line[0:3] == "CNT":
                        try: pc_country = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:5].strip()
                        except: pc_country = None
                    # Priotity Application Date
                    elif line[0:3] == "APD":
                        try: pc_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.replace_old_html_characters(line[3:].strip()), args_array, document_id)
                        except: pc_date = None
                    # Priority Application Number
                    elif line[0:3] == "APN":
                        try:
                            pc_doc_num = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:100].strip()
                            item_ready_to_insert = True
                        except:
                            pc_doc_num = None
                            item_ready_to_insert = True

                    # Catch the tag of next header but not empty line
                    elif line[0:4].strip() not in accepted_headers_array:

                        try:
                            # Append data into dictionary to be written later
                            processed_foreignpriority.append({
                                "table_name" : "uspto.FOREIGNPRIORITY_G",
                                "GrantID" : document_id,
                                "Position" : position_prior,
                                "Kind" : pc_kind,
                                "Country" : pc_country,
                                "DocumentID" : pc_doc_num,
                                "PriorityDate" : pc_date,
                                "FileName" : args_array['file_name']
                            })
                            #print(processed_foreignpriority)
                            position_prior += 1
                            # Reset all variables to avoid overlap
                            pc_country = None
                            pc_doc_num = None
                            pc_date = None

                        except Exception as e:
                            # Reset the item ready to insert
                            item_ready_to_insert = False
                            print("Data missing from APS foreign priority for grant id : " + document_id + " in url: " + args_array['url_links'])
                            logger.error("Some data was missing from the APS foreign priority data for grant id: " + document_id + " in url: " + args_array['url_link'])

                        # Reset the item ready to insert
                        item_ready_to_insert = False
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True

        # INVT is Inventor
        elif line[0:4] == "INVT":

            # Set the multi_line_flag to empty
            multi_line_flag = ""
            # Array of expected header strings
            accepted_headers_array = ["INVT", "NAM","STR", "CTY", "STA", "CNT", "ZIP", "R47", "ITX"]
            # Init ready to insert to false to first flag is not caught
            item_ready_to_insert = False
            # Set loop flag for finished reading inventors to false
            data_parse_completed = False
            # Ensure that all variables that are optionally included will be set.
            inventory_first_name = None
            inventor_last_name = None
            inventor_city = None
            inventor_state = None
            inventor_country = None
            inventor_residence = None
            inventor_nationality = None

            # loop through all inventors
            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # If the inventor tag is found then append last set of data
                    if line[0:4] == "INVT":

                        # The data collection is complete and should be appended
                        if item_ready_to_insert == True:

                            # US countries were not assigned a CNT value
                            if inventor_country == None and inventor_state != None:
                                if USPTOSanitizer.is_US_state(inventor_state):
                                    inventor_country = "US"
                                else: inventor_country = None

                            # Append data into dictionary to be written later
                            try:
                                processed_inventor.append({
                                    "table_name" : "uspto.INVENTOR_G",
                                    "GrantID" : document_id,
                                    "Position" : position_inventor,
                                    "FirstName" : inventor_first_name,
                                    "LastName" : inventor_last_name,
                                    "City" : inventor_city,
                                    "State" : inventor_state,
                                    "Country" : inventor_country,
                                    "Nationality" : inventor_nationality,
                                    "Residence" : inventor_residence,
                                    "FileName" : args_array['file_name']
                                })
                                #print(processed_inventor)
                                position_inventor += 1
                                # Reset all the variables associated so they don't get reused
                                inventor_first_name = None
                                inventor_last_name = None
                                inventor_city = None
                                inventor_nationality = None
                                inventor_country = None
                                inventor_residence = None
                                inventor_state = None
                                # Reset the item ready to insert
                                item_ready_to_insert = False

                            except Exception as e:
                                print("Data missing from inventors for grant id : " + document_id + " in url: " + args_array['url_links'])
                                logger.error("Some data was missing from inventors reference data for grant id: " + document_id + " in url: " + args_array['url_link'])
                                # Reset the item ready to insert
                                item_ready_to_insert = False


                    # Get and parse the name of the inventor
                    elif line[0:3] == "NAM":
                        # Get the citation text from the line
                        try:
                            name_array = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(";")
                            if len(name_array) == 1:
                                inventor_last_name = USPTOSanitizer.strip_for_csv(name_array[0])[:100]
                                inventor_first_name = None
                            elif len(name_array) == 2:
                                inventor_first_name = USPTOSanitizer.strip_for_csv(name_array[0])[:100]
                                inventor_last_name = USPTOSanitizer.strip_for_csv(name_array[1])[:100]
                            else:
                                inventor_first_name = USPTOSanitizer.strip_for_csv(name_array[0])[:100]
                                inventor_last_name = USPTOSanitizer.strip_for_csv(name_array[1])[:100]

                        except:
                            traceback.print_exc()
                            # Print exception information to file
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                            inventor_first_name = None
                            inventor_last_name = None
                            logger.error("A inventor name data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Get the street of inventor
                    elif line[0:3] == "STR":
                        multi_line_flag = 'STR'
                        # Get the citation text from the line
                        try: inventor_residence = USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip()))[:100]
                        except:
                            inventor_residence = None
                            logger.error("A inventor street data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Get the city of inventor
                    elif line[0:3] == "CTY":
                        # Get the citation text from the line
                        try: inventor_city = USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip()))[:100]
                        except:
                            inventor_city = None
                            logger.error("A inventor city data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Get the state of inventor
                    elif line[0:3] == "STA":
                        # Get the citation text from the line
                        try: inventor_state = USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip()))[:100]
                        except:
                            inventor_state = None
                            logger.error("A inventor state data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Get the country of inventor
                    elif line[0:3] == "CNT":
                        # Get the citation text from the line
                        try:
                            inventor_country = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:100]
                            #inventor_country = USPTOSanitizer.fix_old_country_code(inventor_country)
                            # Reset the item ready to insert
                            item_ready_to_insert = True
                        except:
                            inventor_country = None
                            item_ready_to_insert = True
                            logger.error("A inventor country data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # If next line does not have a header but more text, it is the continuince of NAM
                    elif not line[0:3].strip():
                        # Get the extended text from the line
                        try:
                            if multi_line_flag == "STR":
                                inventor_residence += " " + USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip()))[:300]
                        except: logger.error("An inventor data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # If next header is found then store data and end loop
                    elif line[0:4].strip() not in accepted_headers_array:

                        # US countries were not assigned a CNT value
                        if inventor_country == None and inventor_state != None:
                            if USPTOSanitizer.is_US_state(inventor_state):
                                inventor_country = "US"
                            else: inventor_country = None

                        # Append data into dictionary to be written later
                        processed_inventor.append({
                            "table_name" : "uspto.INVENTOR_G",
                            "GrantID" : document_id,
                            "Position" : position_inventor,
                            "FirstName" : inventor_first_name,
                            "LastName" : inventor_last_name,
                            "City" : inventor_city,
                            "State" : inventor_state,
                            "Country" : inventor_country,
                            "Nationality" : inventor_nationality,
                            "Residence" : inventor_residence,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_inventor)
                        position_inventor += 1
                        # Reset all the variables associated so they don't get reused
                        inventor_first_name = None
                        inventor_last_name = None
                        inventor_city = None
                        inventor_nationality = None
                        inventor_country = None
                        inventor_residence = None
                        inventor_state = None
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True

        # ASSG Assignee
        elif line[0:4] == "ASSG":

            multi_line_flag = ''
            # Array of expected header strings
            accepted_headers_array = ["ASSG", "NAM", "STR", "CTY", "STA", "CNT", "ZIP", "COD", "ITX"]
            # Init ready to insert to false to first flag is not caught
            item_ready_to_insert = False
            # Set loop flag for finished reading inventors to false
            data_parse_completed = False
            # Ensure that all variables that are optionally included will be set.
            asn_orgname = None
            asn_city = None
            asn_state = None
            asn_country = None
            asn_role = None

            # loop through all inventors
            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # If the inventor tag is found then append last set of data
                    if line[0:4] == "ASSG":

                        # The data collection is complete and should be appended
                        if item_ready_to_insert == True:
                            # Append data into dictionary to be written later
                            try:
                                # Append data into dictionary to be written later
                                processed_assignee.append({
                                    "table_name" : "uspto.ASSIGNEE_G",
                                    "GrantID" : document_id,
                                    "Position" : position_assignee,
                                    "OrgName" : asn_orgname,
                                    "Role" : asn_role,
                                    "City" : asn_city,
                                    "State" : asn_state,
                                    "Country" : asn_country,
                                    "FileName" : args_array['file_name']
                                })
                                #print(processed_assignee)
                                position_assignee += 1
                                # Reset all variables so they don't get reused.
                                asn_orgname = None
                                asn_city = None
                                asn_state = None
                                asn_country = None
                                asn_role = None
                                # Reset the item ready to insert
                                item_ready_to_insert = False

                            except Exception as e:
                                print("Data missing from assignee for grant id : " + document_id + " in url: " + args_array['url_links'])
                                logger.error("Some data was missing from assignee reference data for grant id: " + document_id + " in url: " + args_array['url_link'])
                                # Reset the item ready to insert
                                item_ready_to_insert = False

                    # Get and pase the name of the inventor
                    elif line[0:3] == "NAM":
                        # Get the citation text from the line
                        try:
                            asn_orgname = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:500]
                            multi_line_flag = "NAM"
                        except:
                            asn_orgname = None
                            logger.error("An assignee data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Get the street of inventor
                    elif line[0:3] == "CTY":
                        # Get the assignee city text from the line
                        try: asn_city = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:100]
                        except:
                            asn_city = None
                            logger.error("A assignee data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Get the state of inventor
                    elif line[0:3] == "STA":
                        # Get the assignee state from the line
                        try: asn_state = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:100]
                        except:
                            asn_state = None
                            logger.error("A assignee data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Get the state of inventor
                    elif line[0:3] == "COD":
                        # Get the citation text from the line
                        try: asn_role = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:45]
                        except:
                            asn_role = None
                            logger.error("A assignee data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # get the country of inventor
                    elif line[0:3] == "CNT":
                        # Get the citation text from the line
                        try:
                            asn_country = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:100]
                            # Reset the item ready to insert
                            item_ready_to_insert = True
                        except:
                            asn_country = None
                            item_ready_to_insert = True
                            logger.error("A inventor data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # If next line does not have a header but more text, it is the continuince of NAM
                    elif not line[0:3].strip():
                        # Get the citation text from the line
                        try:
                            if multi_line_flag == "NAM":
                                asn_orgname += " " +  USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:500]
                        except: logger.error("An assignee data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # if next header is found store and end loop
                    elif line[0:4].strip() not in accepted_headers_array:

                        # Append data into dictionary to be written later
                        processed_assignee.append({
                            "table_name" : "uspto.ASSIGNEE_G",
                            "GrantID" : document_id,
                            "Position" : position_assignee,
                            "OrgName" : asn_orgname,
                            "Role" : asn_role,
                            "City" : asn_city,
                            "State" : asn_state,
                            "Country" : asn_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_assignee)
                        position_assignee += 1
                        # Ensure that all variables that are optionally included will be set.
                        asn_orgname = None
                        asn_city = None
                        asn_state = None
                        asn_country = None
                        asn_role = None
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True

        # LREP is Legal Representation / Agent
        elif line[0:4] == "LREP":

            # Set the accepted expected headers allowed in agent dataset
            accepted_headers_array = ["LREP", "FRM", "FR2", "AAT", "AGT", "ATT", "REG", "NAM", "STR", "CTY", "STA", "CNT", "ZIP"]
            # Set loop flag for finished reading inventors to false
            data_parse_completed = False
            # Ensure that all required database variables that are set
            agent_first_name = None
            agent_last_name = None
            agent_country = None
            agent_orgname = None

            # loop through all inventors
            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line: insert_final = True;
                else:
                    # Get the firm name from line
                    if line[0:3] == "FRM":
                        # Get the firm name from the line
                        try:
                            agent_orgname = USPTOSanitizer.replace_old_html_characters(line[3:].strip())[:300]
                        except:
                            agent_orgname = None
                            logger.error("An agent data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                        # Append data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_G",
                            "GrantID" : document_id,
                            "Position" : position_agent,
                            "OrgName" : agent_orgname,
                            "LastName" : agent_last_name,
                            "FirstName" : agent_first_name,
                            "Country" : agent_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        position_agent += 1
                        # Reset all variables so they don't get reused.
                        agent_first_name = None
                        agent_last_name = None
                        agent_country = None

                    # Get the principle attorney name and append to array
                    elif line[0:3] == "FR2":
                        # Get the citation text from the line
                        try:
                            agent_name = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(";")
                            agent_first_name = agent_name[1].strip()[:100]
                            agent_last_name = agent_name[0].strip()[:100]
                        except:
                            agent_first_name = None
                            agent_last_name = None
                            logger.error("A agent data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                        # Append data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_G",
                            "GrantID" : document_id,
                            "Position" : position_agent,
                            "OrgName" : agent_orgname,
                            "LastName" : agent_last_name,
                            "FirstName" : agent_first_name,
                            "Country" : agent_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        position_agent += 1
                        # Reset all variables so they don't get reused.
                        agent_first_name = None
                        agent_last_name = None
                        agent_country = None

                    # Get associate attorney name and append to dataset
                    elif line[0:3] == "AAT":
                        # Get the citation text from the line
                        try:
                            agent_name = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(";")
                            agent_first_name = agent_name[1].strip()[:100]
                            agent_last_name = agent_name[0].strip()[:100]
                        except:
                            agent_first_name = None
                            agent_last_name = None
                            logger.error("A agent data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                        # Append data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_G",
                            "GrantID" : document_id,
                            "Position" : position_agent,
                            "OrgName" : agent_orgname,
                            "LastName" : agent_last_name,
                            "FirstName" : agent_first_name,
                            "Country" : agent_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        position_agent += 1
                        # Reset all variables so they don't get reused.
                        agent_first_name = None
                        agent_last_name = None
                        agent_country = None

                    # Get Agent's name and append to dataset
                    elif line[0:3] == "AGT":
                        # Get the citation text from the line
                        try:
                            agent_name = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(";")
                            agent_first_name = agent_name[1].strip()[:100]
                            agent_last_name = agent_name[0].strip()[:100]
                        except:
                            agent_first_name = None
                            agent_last_name = None
                            logger.error("A agent data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                        # Append data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_G",
                            "GrantID" : document_id,
                            "Position" : position_agent,
                            "OrgName" : agent_orgname,
                            "LastName" : agent_last_name,
                            "FirstName" : agent_first_name,
                            "Country" : agent_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        position_agent += 1
                        # Reset all variables so they don't get reused.
                        agent_first_name = None
                        agent_last_name = None
                        agent_country = None

                    # Get Agent's name and append to dataset
                    elif line[0:3] == "ATT":
                        # Get the citation text from the line
                        try:
                            agent_name = USPTOSanitizer.replace_old_html_characters(line[3:].strip()).split(";")
                            agent_first_name = agent_name[1].strip()[:100]
                            agent_last_name = agent_name[0].strip()[:100]
                        except:
                            agent_first_name = None
                            agent_last_name = None
                            logger.error("A agent data error occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                        # Append data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_G",
                            "GrantID" : document_id,
                            "Position" : position_agent,
                            "OrgName" : agent_orgname,
                            "LastName" : agent_last_name,
                            "FirstName" : agent_first_name,
                            "Country" : agent_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        position_agent += 1
                        # Reset all variables so they don't get reused.
                        agent_first_name = None
                        agent_last_name = None
                        agent_country = None

                    # Else check if the header is from the next datatype
                    elif line[0:4].strip() not in accepted_headers_array:
                        # End the while loop for agent data
                        data_parse_completed = True
                        next_line_loaded_already = True

        # ABST is Abstract
        elif line[0:4] == "ABST":

            # Define accepted headers
            accepted_headers_array = ["PAL", "PAR", "GOVT"]
            # Initialize empty string to to hold multi-line entries
            abstract = ''
            # Set the flag for while loop
            data_parse_completed = False

            # Loop through all ABST until finished
            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line:
                    data_parse_completed = True
                    insert_final = True;
                else:

                    # If line is the first line of the abstract append to string
                    if line[0:3] == "PAL" or line[0:3] == "PAR":
                        # Get the abstract text from the line
                        try: abstract +=  USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())) + " "
                        except: logger.error("Abstract line could not be appended for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # If line has blank space at first character
                    elif not line[0].strip():
                        # Append the continued reference
                        try: abstract += USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())) + " "
                        except:
                            traceback.print_exc()
                            logger.error("Abstract line could not be appended for grant_id: " + document_id + " in link: " + args_array['url_link'])
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

                    # If the next element in the document is found
                    elif line[0:4].strip() not in accepted_headers_array:
                        # Set abstract to None if it's still an empty string
                        if not abstract: abstract = None
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True

            # Clear the leading and trailing whitespace
            try: abstract = abstract.strip()
            except: abstract = None

        # DCLM is Design Claims and CLMS is Claims
        elif line[0:4] == "DCLM" or line[0:4] == "CLMS":

            #if line[0:4] == "DCLM":
                #logger.warning("A DCLM header tag found in grant_id: " + document_id + " in link: " + args_array['url_link'])

            accepted_headers_array = ["PAL", "STM", "NUM", "PAR", "PA1", "PA2"]
            # Initialize empty string to to hold multi-line entries
            claims = ''
            data_parse_completed = False

            # Loop through all CLAIMS until finished
            while data_parse_completed == False:

                # Load the next line
                line = data_file_contents.readline()
                if not line:
                    data_parse_completed = True
                    insert_final = True;
                else:
                    # If line is in accepted headers array,
                    # append the line onto the string
                    if line[0:3] in accepted_headers_array:
                        # Get the citation text from the line
                        try: claims += USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())) + " "
                        except: logger.error("An error appending line to claim occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # Else if line has empty chracter as first char
                    elif not line[0].strip():
                        # Append to claims string
                        try: claims += USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())) + " "
                        except Exception as e:
                            traceback.print_exc()
                            logger.error("An error appending line to claim occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

                    # If the next element in the document is found
                    elif line[0:4].strip() not in accepted_headers_array:
                        # Set claims to None if still empty string
                        if not claims: claims = None
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True

            # Clear the leading and trailing whitespace
            try: claims = claims.strip()
            except: claims = None

        # DETD is Detailed Description
        elif line[0:4] == "DETD":
            # This header type has no data on same line but will include further
            # readlines so read another line in a while loop until you finish with foreign references
            # and when non-description tag is found set a flag that prevents another line from being
            # read next iteration through main loop

            # Set accepted DAT headers
            accepted_headers_array = ["PAC", "PAR", "PA0", "PA1", "PA2", "NUM"]
            # Set a flag that the DETD tag has not finished
            data_parse_completed = False
            item_ready_to_insert = False
            description = ""

            while data_parse_completed == False:

                # Read next line
                line = data_file_contents.readline()
                if not line:
                    data_parse_completed = True
                    insert_final = True;
                else:
                    # If the header is expected as part of DETD
                    if line[0:4].strip() in accepted_headers_array:
                        # Get the citation text from the line
                        try: description += USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())) + " "
                        except: logger.error("An error appending line to description occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])

                    # If the line is a blank line
                    elif not line[0].strip():
                        # Append to claims string
                        try: description += USPTOSanitizer.strip_for_csv(USPTOSanitizer.replace_old_html_characters(line[3:].strip())) + " "
                        except Exception as e:
                            traceback.print_exc()
                            logger.error("An error appending line to description occurred for grant_id: " + document_id + " in link: " + args_array['url_link'])
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

                    # Catch the tag of next header but not empty line
                    elif line[0:4].strip() not in accepted_headers_array:
                        # Reset the item ready to insert
                        item_ready_to_insert = False
                        # Set the next_line_loaded_already flag to True
                        next_line_loaded_already = True
                        # Break the foreign patent citation loop
                        data_parse_completed = True
            # Clear the leading and trailing whitespace
            try: description = description.strip()
            except: description = None

    # Close all the open .csv files
    USPTOCSVHandler.close_csv_files(args_array)
    #print("Patents found: " + str(total_patents_found))
    # Set a flag file_processed to ensure that the bulk insert succeeds
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
            # Close all the open csv files
            USPTOCSVHandler.delete_csv_files(args_array)

        # Print message to stdout and log
        print('[Processed .bat or .txt File. Total time:{0}  Time: {1}]'.format(time.time()-start_time, time.strftime('%c')))
        # Return the file processed status
        return file_processed
    else:
        # Print message to stdout and log
        print('[Failed to bulk load {0} data for {1} into database. Time:{2} Finished Time: {3} ]'.format(args_array['document_type'], args_array['url_link'], time.time() - start_time, time.strftime("%c")))
        logger.error('Failed to bulk load {0} data for {1} into database. Time:{2} Finished Time: {3} ]'.format(args_array['document_type'], args_array['url_link'], time.time() - start_time, time.strftime("%c")))
        # Return None to show database insertion failed
        return None
