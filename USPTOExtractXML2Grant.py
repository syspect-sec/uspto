# USPTOExtractXML2Grant.py
# USPTO Bulk Data Parser - Extract XML 2 Grants
# Description: Imported to the main USPTOParser.py.  Extracts grant data from USPTO XML v2 files.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# Import Python Modules
import xml.etree.ElementTree as ET
import time
import traceback
import os
import sys
import re

# Import USPTO Parser Functions
import USPTOLogger
import USPTOSanitizer

# Function used to extract data from XML2 formatted patent grants
def extract_XML2_grant(raw_data, args_array):

    #
    # Data documentation on the fields in XML2 Grant data can be found
    # in the /documents/data_descriptions/PatentGrantSGMLv19-Documentation.pdf file

    # Start timer
    start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Pass the url_link and format into local variables
    url_link = args_array['url_link']
    uspto_xml_format = args_array['uspto_xml_format']

    # Define all arrays needed to hold the data
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

    # Pass the raw data into Element tree xml object
    try: patent_root = ET.fromstring(raw_data)
    except ET.ParseError as e:
        print_xml = raw_data.split("\n")
        for num, line in enumerate(print_xml, start = 1):
            print(str(num) + ' : ' + line)
        logger.error("Character Entity prevented ET from parsing XML in file: " + url_link )
        traceback.print_exc()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())


    # SDOBI is the bibliographic data
    for r in patent_root.findall('SDOBI'):

        # B100 Document Identification
        for B100 in r.findall('B100'):
            try:
                document_id = USPTOSanitizer.return_element_text(B100.find('B110')).strip()
                document_id = USPTOSanitizer.fix_patent_number(document_id)[:20]
            except:
                document_id = None
                logger.error("No Patent Number was found for: " + url_link)
            try:
                kind = USPTOSanitizer.return_element_text(B100.find('B130')).strip()[:2]
                app_type = USPTOSanitizer.return_xml2_app_type(args_array, kind).strip()
            except: kind = None
            # PATENT ISSUE DATE
            try: pub_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.return_element_text(B100.find('B140')), args_array, document_id)
            except: pub_date = None
            # B190 is Publishing Country or Organization
            # This is always US in Red Book Patent Grant documents and
            # this field is not stored or used.
            try: pub_country = USPTOSanitizer.return_element_text(B100.find('B190')).strip()
            except: pub_country = None

        # B200 is Domestic Filing Data
        for B200 in r.findall('B200'):
            # TODO: find this in XML2 applications
            app_country = None
            # Application number
            try: app_no = USPTOSanitizer.return_element_text(B200.find('B210')).strip()[:20]
            except: app_no = None
            # Application Date
            try: app_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.return_element_text(B200.find('B220')), args_array, document_id)
            except: app_date = None
            # Series Code
            try: series_code = USPTOSanitizer.return_element_text(B200.find('B211US')).strip()[:2]
            except: series_code = None

        # Collect the Grant Length
        try: grant_length = USPTOSanitizer.return_element_text(r.find("B400").find("B472").find("B474")).strip()
        except: grant_length = None

        # Collect Technical information
        # such as classification and references
        for B500 in r.findall('B500'):
            # US Classification
            for B520 in B500.findall('B520'):
                position = 1
                # USCLASS
                for B521 in B520.findall('B521'):
                    # Reset the class vars
                    n_class = None
                    n_section = None
                    n_subclass = None
                    # Collect class vars
                    n_class_info = USPTOSanitizer.return_element_text(B521)
                    n_class_main, n_subclass = USPTOSanitizer.return_class(n_class_info)
                    n_class_main = n_class_main.strip()[:5]
                    n_subclass = n_subclass.strip()[:15]

                    # Append SQL data into dictionary to be written later
                    processed_usclass.append({
                        "table_name" : "uspto.USCLASS_G",
                        "GrantID" : document_id,
                        "Position" : position,
                        "Class" : n_class_main,
                        "SubClass" : n_subclass,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_usclass)
                    position += 1

                # B522 USCLASS FURTHER
                for B522 in B520.findall('B522'):
                    n_class_info = USPTOSanitizer.return_element_text(B522)
                    n_class_main, n_subclass = USPTOSanitizer.return_class(n_class_info)
                    n_class_main = n_class_main.strip()[:5]
                    n_subclass = n_subclass.strip()[:15]

                    # Append SQL data into dictionary to be written later
                    processed_usclass.append({
                        "table_name" : "uspto.USCLASS_G",
                        "GrantID" : document_id,
                        "Position" : position,
                        "Class" : n_class_main,
                        "SubClass" : n_subclass,
                        "FileName" : args_array['file_name']
                    })
                    position += 1

            # B510 International Class data
            # TODO: check if I need to set all variables to empty or can just leave as null
            # TODO: check if classification is parsed correctly
            for B510 in B500.findall('B510'):
                #logger.warning("International Classifcation found in XML2: " + args_array['url_link'] + " document: " + str(document_id))
                # Reset position
                position = 1
                # B511 Main Class
                for B511 in B510.findall('B511'):
                    i_section = None
                    i_class = None
                    i_subclass = None
                    i_class_mgr = None
                    i_class_sgr = None
                    i_malformed = None
                    int_class = USPTOSanitizer.return_element_text(B511)
                    # Int Class is:
                    if(len(int_class.split()) > 1):
                        sec_1, sec_2 = int_class.split()
                        sec_1 = sec_1.strip()[:15]
                        # Remove the Section from first character
                        i_section = sec_1[0]
                        i_class = sec_1[1:3]
                        i_subclass = sec_1[-1]
                        i_class_mgr = sec_2.strip()[:-2]
                        i_class_sgr = sec_2.strip()[-2:]
                    else:
                        int_class = int_class.strip()[:15]
                        i_section = int_class[0]
                        i_class = int_class[1:]
                        i_subclass = int_class[-1]
                        i_malformed = 1

                    # Append SQL data into dictionary to be written later
                    processed_intclass.append({
                        "table_name" : "uspto.INTCLASS_G",
                        "GrantID" : document_id,
                        "Position" : position,
                        "Section" : i_section,
                        "Class" : i_class,
                        "SubClass" : i_subclass,
                        "MainGroup" : i_class_mgr,
                        "SubGroup" : i_class_sgr,
                        "Malformed" : i_malformed,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_intclass)
                    position += 1

                # B512 Further International Class
                for B512 in B510.findall('B512'):
                    i_section = None
                    i_class = None
                    i_subclass = None
                    i_class_mgr = None
                    i_class_sgr = None
                    i_malformed = None
                    int_class = USPTOSanitizer.return_element_text(B512)
                    # Split class in to class and group
                    if(len(int_class.split()) > 1):
                        sec_1, sec_2 = int_class.split()
                        sec_1 = sec_1.strip()[:15]
                        # Remove the Section from first character
                        i_section = sec_1[0]
                        i_class = sec_1[1:3]
                        i_subclass = sec_1[-1]
                        i_class_mgr = sec_2.strip()[:-2]
                        i_class_sgr = sec_2.strip()[-2:]
                    else:
                        # TODO: Is this correct??
                        int_class = int_class.strip()[:15]
                        i_section = int_class[0]
                        i_class = int_class[1:]
                        i_subclass = int_class[-1]
                        i_malformed = 1

                    # Append SQL data into dictionary to be written later
                    processed_intclass.append({
                        "table_name" : "uspto.INTCLASS_G",
                        "GrantID" : document_id,
                        "Position" : position,
                        "Section" : i_section,
                        "Class" : i_class,
                        "SubClass" : i_subclass,
                        "MainGroup" : i_class_mgr,
                        "SubGroup" : i_class_sgr,
                        "Malformed" : i_malformed,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_intclass)
                    position += 1

            # B540 Collect Title
            for B540 in B500.findall('B540'):
                try: title = USPTOSanitizer.strip_for_csv(USPTOSanitizer.return_element_text(B540)[:500])
                except: title = None

            # Collect Citations
            for B560 in B500.findall('B560'):
                # Reset position counter for all citations loop
                position = 1
                # B561 is PATCIT
                for B561 in B560.findall('B561'):

                    # TODO: find out how to do PCIT, DOC without loop.  Only B561 needs loop
                    pcit = B561.find('PCIT')
                    # Determien if the patent is US or not
                    #TODO: needs to check better, what does non US patent look like
                    # If all patents have PARTY-US then perhaps a databse call to check the country of origin
                    # would still allow to separate into GRACIT and FORPATCIT_G
                    #if PCIT.find("PARTY-US") == True:
                        #print "CITATION COUNTRY US"
                        #citation_country = "US"
                    #else:
                        #citation_country = "NON-US"
                        #logger.warning("NON US patent found")

                    #citation_country = "US"

                    # Declare items in case they are not found
                    citation_name = None
                    citation_city = None
                    citation_state = None
                    citation_country = None

                    doc = pcit.find('DOC')
                    if doc is not None:
                        try: citation_document_number = USPTOSanitizer.return_element_text(doc.find('DNUM')).strip()[:15]
                        except: citation_document_number = None
                        try: pct_kind = USPTOSanitizer.return_element_text(doc.find('KIND')).strip()[:10]
                        except: pct_kind = None
                        try: citation_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.return_element_text(doc.find('DATE')), args_array, document_id)
                        except: citation_date = None
                        p_elem = pcit.find('PARTY-US')
                        if p_elem is not None:
                            try: citation_name = USPTOSanitizer.return_element_text(p_elem.find("NAM").find("SNM")).strip()[:100]
                            except: citation_name = None
                            # Citation Address info
                            try: citation_city = USPTOSanitizer.return_element_text(p_elem.find('ADR').find('CITY')).strip()[:100]
                            except: citation_city = None
                            try: citation_state = USPTOSanitizer.return_element_text(p_elem.find('ADR').find('STATE')).strip()[:3]
                            except: citation_state = None
                            # Citation country
                            try: citation_country = USPTOSanitizer.return_element_text(p_elem.find("ADR").find('CTRY')).strip()[:3]
                            except:
                                try:
                                    # If state is a US state, set country to US
                                    if USPTOSanitizer.is_US_state(citation_state):
                                        citation_country = "US"
                                    else:
                                        citation_country = None
                                except: citation_country = None

                        # Parse citation category
                        if(len(B561.getchildren()) > 1):
                            try: citation_category = B561.getchildren()[1].tag.replace("\n", "").replace("\r", "").upper()
                            except: citation_category = None
                        else: citation_category = None

                        #TODO: be aware that there may be something crazy in the
                        # citation document number
                        if pct_kind != None:

                            # Append SQL data into dictionary to be written later
                            processed_gracit.append({
                                "table_name" : "uspto.GRACIT_G",
                                "GrantID" : document_id,
                                "Position" : position,
                                "CitedID" : citation_document_number,
                                "Kind" : pct_kind,
                                "Name" : citation_name,
                                "Date" : citation_date,
                                "Country" : citation_country,
                                "Category" : citation_category,
                                "FileName" : args_array['file_name']
                            })
                            #print(processed_gracit)
                            position += 1

                        else:

                            # Append SQL data into dictionary to be written later
                            processed_forpatcit.append({
                                "table_name" : "uspto.FORPATCIT_G",
                                "GrantID" : document_id,
                                "Position" : position,
                                "CitedID" : citation_document_number,
                                "Kind" : pct_kind,
                                "Name" : citation_name,
                                "Date" : citation_date,
                                "Country" : citation_country,
                                "Category" : citation_category,
                                "FileName" : args_array['file_name']
                            })
                            #print(processed_forpatcit)
                            position += 1

                # Reset position counter for non-patent citations loop
                position = 1
                # NON-PATENT LITERATURE
                for B562 in B560.findall('B562'):
                    NCIT = B562.find('NCIT')
                    if NCIT is not None:
                        # Sometimes, there will be '<i> or <sup>, etc.' in the reference string; we need to remove it
                        non_patent_citation_text = USPTOSanitizer.return_element_text(NCIT)
                        non_patent_citation_text = re.sub('<[^>]+>','',non_patent_citation_text)
                    else:
                        non_patent_citation_text = None

                    # Parse citation category into code
                    if(len(B562.getchildren())>1):
                        try: ncitation_category = B562.getchildren()[1].tag.replace("\n", "").replace("\r", "").upper()
                        except: ncitation_category = None
                    else: ncitation_category = None

                    # Append SQL data into dictionary to be written later
                    processed_nonpatcit.append({
                        "table_name" : "uspto.NONPATCIT_G",
                        "GrantID" : document_id,
                        "Position" : position,
                        "Citation" : non_patent_citation_text,
                        "Category" : ncitation_category,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_nonpatcit)
                    position += 1

            # Collect number of claims
            for B570 in B500.findall('B570'):
                try: claims_num = USPTOSanitizer.return_element_text(B570.find('B577')).strip()
                except: claims_num = None

            # Collect number of drawings and figures
            for B590 in B500.findall('B590'):
                for B595 in B590.findall('B595'):
                    try:
                        number_of_drawings = USPTOSanitizer.return_element_text(B595).strip()
                        number_of_drawings = number_of_drawings.split("/")[0]
                    except: number_of_drawings = None
                for B596 in B590.findall('B596'):
                    try: number_of_figures = USPTOSanitizer.return_element_text(B596).strip()
                    except: number_of_figures = None

            # TODO: B582 find out what it is.  Looks like patent classifications but it's all alone in the XML

        # B700 is Parties
        # TODO: find the applicant data and append to array
        for B700 in r.findall('B700'):

            # B720 Inventor
            for B720 in B700.findall('B720'):
                # Reset position for inventors
                position = 1
                # Collect inventor information
                for B721 in B720.findall('B721'):
                    for i in B721.findall('PARTY-US'):
                        # Inventor Name
                        try: inventor_first_name = USPTOSanitizer.return_element_text(i.find('NAM').find('FNM')).strip()[:100]
                        except: inventor_first_name = None
                        try: inventor_last_name = USPTOSanitizer.return_element_text(i.find('NAM').find('SNM')).strip()[:100]
                        except: inventor_last_name = None
                        # Inventor Address info
                        try: inventor_city = USPTOSanitizer.return_element_text(i.find('ADR').find('CITY')).strip()[:100]
                        except: inventor_city = None
                        try: inventor_state = USPTOSanitizer.return_element_text(i.find('ADR').find('STATE')).strip()[:3]
                        except: inventor_state = None
                        # Inventor country
                        try: inventor_country = USPTOSanitizer.return_element_text(i.find("ADR").find('CTRY')).strip()[:3]
                        except:
                            try:
                                # If state is a US state, set country to US
                                if USPTOSanitizer.is_US_state(inventor_state):
                                    inventor_country = "US"
                                else:
                                    inventor_country = None
                            except: inventor_country = None
                        inventor_nationality = None
                        inventor_residence = None

                    # Append SQL data into dictionary to be written later
                    processed_inventor.append({
                        "table_name" : "uspto.INVENTOR_G",
                        "GrantID" : document_id,
                        "Position" : position,
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
                    position += 1

            # B730 Assignee
            # TODO: check if finding child of child is working
            # Reset position for assignees
            position = 1
            for B730 in B700.findall('B730'):
                for B731 in B730.findall('B731'):
                    for x in B731.findall('PARTY-US'):
                        try: asn_orgname = USPTOSanitizer.return_element_text(x.find('NAM').find("ONM")).strip()[:500]
                        except: asn_orgname = None
                        asn_role = None
                        try: asn_city = USPTOSanitizer.return_element_text(x.find("ADR").find('CITY')).strip()[:100]
                        except: asn_city = None
                        try: asn_state = USPTOSanitizer.return_element_text(x.find("ADR").find('STATE')).strip()[:30]
                        except: asn_state = None
                        # Assignee country
                        try: asn_country = USPTOSanitizer.return_element_text(x.find("ADR").find('CTRY')).strip()[:3]
                        except:
                            try:
                                # Fix country if country missing
                                if USPTOSanitizer.is_US_state(asn_state): asn_country = "US"
                                else:asn_country = None
                            except: asn_country = None

                    # Append SQL data into dictionary to be written later
                    processed_assignee.append({
                        "table_name" : "uspto.ASSIGNEE_G",
                        "GrantID" : document_id,
                        "Position" : position,
                        "OrgName" : asn_orgname,
                        "Role" : asn_role,
                        "City" : asn_city,
                        "State" :  asn_state,
                        "Country" : asn_country,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_assignee)
                    position += 1

            # B740 is Legal Agent / Attorney
            for B740 in B700.findall('B740'):
                # Reset position for agents
                position = 1
                for B741 in B740.findall('B741'):
                    for x in B741.findall('PARTY-US'):
                        # Attorney Organization
                        try: agent_orgname = USPTOSanitizer.return_element_text(x.find('NAM').find("ONM")).strip()[:300]
                        except: agent_orgname = None
                        # Attorney Name
                        try: agent_last_name = USPTOSanitizer.return_element_text(x.find('NAM').find('FNM')).strip()[:100]
                        except: agent_last_name = None
                        try: agent_first_name = USPTOSanitizer.return_element_text(x.find('NAM').find('SNM')).strip()[:100]
                        except: agent_first_name = None
                        # Attorney Address information
                        try: agent_city = USPTOSanitizer.return_element_text(x.find("ADR").find('CITY')).strip()[:100]
                        except: agent_city = None
                        try: agent_state = USPTOSanitizer.return_element_text(x.find("ADR").find('STATE')).strip()[:30]
                        except: agent_state = None
                        # Agent country
                        try:
                            agent_country = USPTOSanitizer.return_element_text(x.find("ADR").find('CTRY')).strip()[:3]
                        except:
                            try:
                                # Fix country if missing
                                if USPTOSanitizer.is_US_state(agent_state): agent_country = "US"
                                else: agent_country = None
                            except: agent_country = None

                        # Append SQL data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_G",
                            "GrantID" : document_id,
                            "Position" : position,
                            "OrgName" : agent_orgname,
                            "LastName" : agent_last_name,
                            "FirstName" : agent_first_name,
                            "Country" : agent_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        position += 1

            # B745 Examiner
            for B745 in B700.findall('B745'):
                position = 1
                # Primary Examiner
                for B746 in B745.findall('B746'):
                    for x in B746.findall('PARTY-US'):
                        try: examiner_last_name = USPTOSanitizer.return_element_text(x.find('NAM').find('SNM')).strip()[:50]
                        except: examiner_last_name = None
                        try: examiner_fist_name = USPTOSanitizer.return_element_text(x.find('NAM').find('FNM')).strip()[:50]
                        except:  examiner_fist_name = None
                        try: examiner_department = USPTOSanitizer.return_element_text(B745.find('B748US')).strip()[:50]
                        except: examiner_department = None

                        # Append SQL data into dictionary to be written later
                        processed_examiner.append({
                            "table_name" : "uspto.EXAMINER_G",
                            "GrantID" : document_id,
                            "Position" : position,
                            "LastName" :  examiner_last_name,
                            "FirstName" : examiner_fist_name,
                            "Department" : examiner_department,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_examiner)
                        position += 1

                # Assistant Examiner
                for B747 in B745.findall('B747'):
                    for x in B747.findall('PARTY-US'):
                        try: examiner_last_name = USPTOSanitizer.return_element_text(x.find('NAM').find('SNM')).strip()[:50]
                        except: examiner_last_name = None
                        try: examiner_fist_name = USPTOSanitizer.return_element_text(x.find('NAM').find('FNM')).strip()[:50]
                        except: examiner_fist_name = None
                        try: examiner_department = USPTOSanitizer.return_element_text(B745.find('B748US')).strip()[:50]
                        except: examiner_department = None

                        # Append SQL data into dictionary to be written later
                        processed_examiner.append({
                            "table_name" : "uspto.EXAMINER_G",
                            "GrantID" : document_id,
                            "Position" : position,
                            "LastName" :  examiner_last_name,
                            "FirstName" : examiner_fist_name,
                            "Department" : examiner_department,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_examiner)
                        position += 1

        # Collect foreign priotiry data
        position = 1
        for B300 in r.findall('B300'):
            # Country
            try: pc_country = USPTOSanitizer.return_element_text(B300.find('B330').find('CTRY')).strip()[:5]
            except: pc_country = None
            # Prority filing date
            try: pc_date = USPTOSanitizer.return_formatted_date(USPTOSanitizer.return_element_text(B300.find('B320').find('DATE')).strip()[:45])
            except: pc_date = None
            # Prority document number
            try: pc_doc_num = USPTOSanitizer.return_element_text(B300.find('B310').find('DNUM')).strip()[:45]
            except: pc_doc_dum = None

            # Set the fields that are not in gXML2
            pc_kind = None

            # Append SQL data into dictionary to be written later
            processed_foreignpriority.append({
                "table_name" : "uspto.FOREIGNPRIORITY_G",
                "GrantID" : document_id,
                "Position" : position,
                "Kind" : pc_kind,
                "Country" : pc_country,
                "DocumentID" : pc_doc_num,
                "PriorityDate" : pc_date,
                "FileName" : args_array['file_name']
            })
            #print(processed_foreignpriority)
            position += 1

        # Collect Abstract from data
        try:
            a_elem = patent_root.find('SDOAB')
            if a_elem is not None:
                abstract = USPTOSanitizer.strip_for_csv(USPTOSanitizer.return_element_text(a_elem))
            else: abstract = None
        except Exception as e:
            abstract = None
            traceback.print_exc()
            logger.error("Exception while extracting description from " + str(document_id) + ": " + traceback.print_exc())
        #print(abstract)

        # Collect detailed description from DETDESC
        try:
            d_elem = patent_root.find('SDODE').find('DETDESC')
            if d_elem is not None:
                description = USPTOSanitizer.strip_for_csv(' '.join(d_elem.itertext()))
            else:
                description = None
        except Exception as e:
            description = None
            traceback.print_exc()
            logger.error("Exception while extracting claim from " + str(document_id) + ": " + traceback.print_exc())
        #print(description)

        # Collect claims from data
        try:
            c_elem = patent_root.find('SDOCL')
            if c_elem is not None:
                claims = USPTOSanitizer.strip_for_csv(' '.join(c_elem.itertext()))
                #claims = USPTOSanitizer.strip_for_csv(USPTOSanitizer.return_element_text(c_elem))
            else: claims = None
        except Exception as e:
            claims = None
            traceback.print_exc()
            logger.error("Exception while extracting claim from " + str(document_id) + ": " + traceback.print_exc())
        #print(claims)

        # Append SQL data into dictionary to be written later
        processed_grant.append({
            "table_name" : "uspto.GRANT",
            "GrantID" : document_id,
            "Title" : title,
            "Claims" : claims,
            "Description" : description,
            "IssueDate" : pub_date,
            "Kind" : kind,
            "GrantLength" : grant_length,
            "USSeriesCode" : series_code,
            "Abstract" : abstract,
            "ClaimsNum" : claims_num,
            "DrawingsNum" : number_of_drawings,
            "FiguresNum" : number_of_figures,
            "ApplicationID" : app_no,
            "FileDate" : app_date,
            "AppType" : app_type,
            "FileName" : args_array['file_name']
        })
        #print(processed_grant)


    # Return a dictionary of the processed_ data arrays
    return {
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
