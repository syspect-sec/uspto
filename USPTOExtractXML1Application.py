# USPTOExtractXML1Application.py
# USPTO Bulk Data Parser - Extract XML1 Applications
# Description: Imported to the main USPTOParser.py.  Extracts XML v1 data for applications.
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

# Import USPTO Parser Functions
import USPTOLogger
import USPTOSanitizer

# Function used to extract data from XML1 formatted patent applications
def extract_XML1_application(raw_data, args_array):

    # Set process start time
    start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Pass the url_link and format into local variables
    url_link = args_array['url_link']
    uspto_xml_format = args_array['uspto_xml_format']

    # Define required arrays
    processed_application = []
    processed_foreignpriority = []
    processed_assignee = []
    processed_agent = []
    processed_inventor = []
    processed_usclass = []
    processed_intclass = []
    processed_cpcclass = []

    # Pass the xml into Element tree object
    document_root = ET.fromstring(raw_data)
    r = document_root.find('subdoc-bibliographic-information')

    # Get and fix the document_id data
    di = r.find('document-id')
    if di is not None:
        try:
            # This document ID is NOT application number
            document_id = di.findtext('doc-number').strip()
        except:
            document_id = None
            logger.error("No Patent Number was found for: " + url_link)
        try:
            kind = di.findtext('kind-code').strip()[:2]
            app_type = USPTOSanitizer.return_xml2_app_type(args_array, kind).strip()
        except:
            kind = None
            app_type = None
        try: pub_date = USPTOSanitizer.return_formatted_date(di.findtext('document-date'), args_array, document_id)
        except: pub_date = None

    # Get application filing data
    ar = r.find('domestic-filing-data')
    if ar is not None:
        try:
            app_no = ar.find('application-number').findtext('doc-number').strip()[:20]
        except: app_no = None
        try: app_date = USPTOSanitizer.return_formatted_date(ar.findtext('filing-date'), args_array, document_id)
        except: app_date = None
        try: series_code = ar.findtext('application-number-series-code').strip()[:2]
        except: series_code = None

    # Get technical information
    ti_elem = r.find('technical-information')
    if ti_elem is not None:

        # Get invention title
        try: title = USPTOSanitizer.strip_for_csv(ti_elem.findtext('title-of-invention')[:500])
        except: title = None

        # Get international classification data
        ic = ti_elem.find('classification-ipc')
        if ic is not None:
            # Init position
            position = 1
            # Process the primary international class
            icm = ic.find('classification-ipc-primary')
            if icm is not None:
                #print(icm.findtext('ipc'))
                # Clear variable values
                i_class_sec = None
                i_class = None
                i_subclass = None
                i_class_mgr = None
                i_class_sgr = None
                i_malformed = None
                try:
                    i_class_sec, i_class, i_subclass, i_class_mgr, i_class_sgr = USPTOSanitizer.return_international_class_XML1_application(icm.findtext('ipc'))
                    i_class_sec = i_class_sec.strip()[:15]
                    i_class = i_class.strip()[:15]
                    i_subclass = i_subclass.strip()[:15]
                    i_class_mgr = i_class_mgr.strip()[:15]
                    i_class_sgr = i_class_sgr.strip()[:15]
                except Exception as e:
                    traceback.print_exc()
                    i_class_sec = None
                    i_class = None
                    i_subclass = None
                    i_class_mgr = None
                    i_class_sgr = None
                    i_malformed = 1
                    logger.warning("Malformed international class found in application ID: " + document_id +  " in file: " + url_link)

                # Append SQL data into dictionary to be written later
                processed_intclass.append({
                    "table_name" : "uspto.INTCLASS_A",
                    "ApplicationID" : app_no,
                    "Position" : position,
                    "Section" : i_class_sec,
                    "Class" : i_class,
                    "SubClass" : i_subclass,
                    "MainGroup" : i_class_mgr,
                    "SubGroup" : i_class_sgr,
                    "Malformed" : i_malformed,
                    "FileName" : args_array['file_name']
                })
                #print(processed_intclass)
                position += 1

            # Process any secondary international classes
            ics = ic.findall('classification-ipc-secondary')
            if ics is not None:
                for ics_item in ics:
                    # Clear variable values
                    i_class_sec = None
                    i_class = None
                    i_subclass = None
                    i_class_mgr = None
                    i_class_sgr = None
                    i_malformed = None
                    try:
                        i_class_sec, i_class, i_subclass, i_class_mgr, i_class_sgr = USPTOSanitizer.return_international_class_XML1_application(ics_item.findtext('ipc'))
                        i_class_sec = i_class_sec.strip()[:15]
                        i_class = i_class.strip()[:15]
                        i_subclass = i_subclass.strip()[:15]
                        i_class_mgr = i_class_mgr.strip()[:15]
                        i_class_sgr = i_class_sgr.strip()[:15]
                    except Exception as e:
                        traceback.print_exc()
                        i_class_sec = None
                        i_class = None
                        i_subclass = None
                        i_class_mgr = None
                        i_class_sgr = None
                        i_malformed = 1
                        logger.warning("Malformed international class found in application ID: " + document_id +  " in file: " + url_link)

                    # Append SQL data into dictionary to be written later
                    processed_intclass.append({
                        "table_name" : "uspto.INTCLASS_A",
                        "ApplicationID" : app_no,
                        "Position" : position,
                        "Section" : i_class_sec,
                        "Class" : i_class,
                        "SubClass" : i_subclass,
                        "MainGroup" : i_class_mgr,
                        "SubGroup" : i_class_sgr,
                        "Malformed" : i_malformed,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_intclass)
                    position += 1

        # Get US classification data
        nc = ti_elem.find('classification-us')
        position = 1
        if nc is not None:
            uspc = nc.find('classification-us-primary').find('uspc')
            if uspc is not None:
                n_class_main = None
                n_subclass = None
                try: n_class_main = uspc.findtext('class').strip()[:5]
                except: n_class_main = None
                try: n_subclass = uspc.findtext('subclass').strip()[:15]
                except: n_subclass = None

                # Append SQL data into dictionary to be written later
                processed_usclass.append({
                    "table_name" : "uspto.USCLASS_A",
                    "ApplicationID" : app_no,
                    "Position" : position,
                    "Class" : n_class_main,
                    "SubClass" : n_subclass,
                    "FileName" : args_array['file_name']
                })
                #print(processed_usclass)
                position += 1

            # Collect all Secondary US class
            ncs = nc.findall('classification-us-secondary')
            for ncs_item in ncs:
                n_class_main = None
                n_subclass = None
                uspc = ncs_item.find('uspc')
                if uspc is not None:
                    try: n_class_main = uspc.findtext('class').strip()[:5]
                    except: n_class_main = None
                    try: n_subclass = uspc.findtext('subclass').strip()[:5]
                    except: n_subclass = None

                    # Append SQL data into dictionary to be written later
                    processed_usclass.append({
                        "table_name" : "uspto.USCLASS_A",
                        "ApplicationID" : app_no,
                        "Position" : position,
                        "Class" : n_class_main,
                        "SubClass" : n_subclass,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_usclass)
                    position += 1

    # Get priority claims
    position = 1
    pc_kind = None
    for pc in r.findall('foreign-priority-data'):
        try: pc_country = pc.findtext('country-code').strip()[:100]
        except: pc_country = None
        try: pc_doc_num = pc.find('priority-application-number').findtext('doc-number').strip()[:100]
        except: pc_doc_num = None
        try: pc_date = USPTOSanitizer.return_formatted_date(pc.findtext('filing-date'), args_array, document_id)
        except:pc_date = None

        # Append SQL data into dictionary to be written later
        processed_foreignpriority.append({
            "table_name" : "uspto.FOREIGNPRIORITY_A",
            "ApplicationID" : app_no,
            "Position" : position,
            "Kind" : pc_kind,
            "Country" : pc_country,
            "DocumentID" : pc_doc_num,
            "PriorityDate" : pc_date,
            "FileName" : args_array['file_name']
        })
        #print(processed_foreignpriority)
        position += 1

    # Get inventor data
    iv = r.find('inventors')
    if iv is not None:

        # Init position
        position = 1
        for inventor in iv.findall('first-named-inventor'):
            n = inventor.find('name')
            try: inventor_first_name = n.findtext('given-name').strip()[:100]
            except: inventor_first_name = None
            try: inventor_last_name = n.findtext('family-name').strip()[:100]
            except: inventor_last_name = None
            # Get the residence tag
            res = inventor.find('residence')
            if res is not None:
                residence_us = res.find('residence-us')
                if residence_us is not None:
                    try: inventor_city = residence_us.findtext('city').strip()[:100]
                    except: inventor_city = None
                    try: inventor_state = residence_us.findtext('state').strip()[:100]
                    except: inventor_state = None
                    try: inventor_country = residence_us.findtext('country-code').strip()[:100]
                    except: inventor_country = None
                residence_non_us = res.find('residence-non-us')
                if residence_non_us is not None:
                    try: inventor_city = residence_non_us.findtext('city').strip()[:100]
                    except: inventor_city = None
                    try: inventor_state = residence_non_us.findtext('state').strip()[:100]
                    except: inventor_state = None
                    try: inventor_country = residence_non_us.findtext('country-code').strip()[:100]
                    except: inventor_country = None

            # Append SQL data into dictionary to be written later
            processed_inventor.append({
                "table_name" : "uspto.INVENTOR_A",
                "ApplicationID" : app_no,
                "Position" : position,
                "FirstName" : inventor_first_name,
                "LastName" : inventor_last_name,
                "City" : inventor_city,
                "State" : inventor_state,
                "Country" : inventor_country,
                "FileName" : args_array['file_name']
            })
            #print(processed_inventor)
            position += 1

        # For all secordary inventors
        for inventor in iv.findall('inventor'):
            if inventor is not None:
                n = inventor.find('name')
                if n is not None:
                    try: inventor_first_name = n.findtext('given-name').strip()[:100]
                    except: inventor_first_name = None
                    try: inventor_last_name = n.findtext('family-name').strip()[:100]
                    except: inventor_last_name = None

                res = inventor.find('residence')
                if res is not None:
                    residence_us = res.find('residence-us')
                    if residence_us is not None:
                        try: inventor_city = residence_us.findtext('city').strip()[:100]
                        except: inventor_city = None
                        try: inventor_state = residence_us.findtext('state').strip()[:100]
                        except: inventor_state = None
                        try: inventor_country = residence_us.findtext('country-code').strip()[:100]
                        except: inventor_country = None
                    residence_non_us = res.find('residence-non-us')
                    if residence_non_us is not None:
                        try: inventor_city = residence_non_us.findtext('city').strip()[:100]
                        except: inventor_city = None
                        try: inventor_state = residence_non_us.findtext('state').strip()[:100]
                        except: inventor_state = None
                        try: inventor_country = residence_non_us.findtext('country-code').strip()[:100]
                        except: inventor_country = None

                    # Append SQL data into dictionary to be written later
                    processed_inventor.append({
                        "table_name" : "uspto.INVENTOR_A",
                        "ApplicationID" : app_no,
                        "Position" : position,
                        "FirstName" : inventor_first_name,
                        "LastName" : inventor_last_name,
                        "City" : inventor_city,
                        "State" : inventor_state,
                        "Country" : inventor_country,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_inventor)
                    position += 1

    # Get assignee data
    asn_elem = r.find('assignee')
    if asn_elem is not None:
        # Init position
        position = 1
        try: asn_role = asn_elem.findtext('assignee-type').strip()[:100]
        except: asn_role = None
        try: asn_orgname = asn_elem.findtext('organization-name').strip()[:300]
        except: asn_orgname = None
        adr_elem = asn_elem.find('address')
        try: asn_city = adr_elem.findtext('city').strip()[:100]
        except: asn_city = None
        try: asn_state = adr_elem.findtext('state').strip()[:100]
        except: asn_state = None
        try: asn_country = adr_elem.find('country').findtext('country-code').strip()[:100]
        except: asn_country = None
        if asn_country == None:
            if USPTOSanitizer.is_US_state(asn_state):
                asn_country = "US"
        # These have not been found in XML1,
        # but a full XML parse should be done
        asn_firstname = None
        asn_lastname = None

        # Append SQL data into dictionary to be written later
        processed_assignee.append({
            "table_name" : "uspto.ASSIGNEE_A",
            "ApplicationID" : app_no,
            "Position" : position,
            "OrgName" : asn_orgname,
            "FirstName" : asn_firstname,
            "LastName" : asn_lastname,
            "Role" : asn_role,
            "City" : asn_city,
            "State" : asn_state,
            "Country" : asn_country,
            "FileName" : args_array['file_name']
        })
        #print(processed_assignee)
        position += 1

    # Find the agent element
    ag_elem = r.find('correspondence-address')
    # Init position
    position = 1
    if ag_elem is not None:
        try: agent_orgname = ag_elem.findtext('name-1').strip()
        except: agent_orgname = None
        try: agent_orgname_2 = ag_elem.findtext('name-2').strip()
        except: agent_orgname_2 = None
        # Combine Orgname 1 and 2 and shorten if needed
        if agent_orgname != None and agent_orgname_2 != None:
            agent_orgname = USPTOSanitizer.strip_for_csv(agent_orgname + " " + agent_orgname_2)[:300]
        # Get the address element
        addr_elem = ag_elem.find('address')
        if addr_elem is not None:
            try:
                try: agent_addr_1 = addr_elem.findtext('address-1').strip()[:100]
                except: agent_addr_1 = ""
                try: agent_addr_2 = addr_elem.findtext('address-2').strip()[:100]
                except: agent_addr_2 = ""
                agent_address = USPTOSanitizer.strip_for_csv(agent_addr_1 + agent_addr_2)
            except: agent_address = None
            try:agent_city = addr_elem.findtext('city').strip()[:50]
            except: agent_city = None
            try: agent_state = addr_elem.findtext('state').strip()[:3]
            except: agent_state = None
            try:
                agent_country = addr_elem.find('country').findtext('country-code').strip()[:3]
            except:
                if USPTOSanitizer.is_US_state(agent_state):
                    agent_country = "US"
                else:
                    agent_country = None

        # Append SQL data into dictionary to be written later
        processed_agent.append({
            "table_name" : "uspto.AGENT_A",
            "ApplicationID" : app_no,
            "Position" : position,
            "OrgName" : agent_orgname,
            "Address" : agent_address,
            "City" : agent_city,
            "State" : agent_state,
            "Country" : agent_country,
            "FileName" : args_array['file_name']
        })
        #print(processed_agent)
        position += 1

    # Find the abstract of the application
    try: abstract = USPTOSanitizer.strip_for_csv(USPTOSanitizer.return_element_text(document_root.find('subdoc-abstract')))
    except: abstract = None

    # Find the description
    try:
        description = ""
        d_elem = document_root.find('subdoc-description')
        if d_elem is not None:
            description += USPTOSanitizer.strip_for_csv(' '.join(d_elem.itertext()))
        else: description = None
    except Exception as e:
        description = None
        traceback.print_exc()
        logger.error("Exception while extracting description from " + str(app_no))
    #print(description)

    # Find the claims
    try:
        claims = ""
        c_elem = document_root.find('subdoc-claims')
        if c_elem is not None:
            claims += USPTOSanitizer.strip_for_csv(' '.join(c_elem.itertext()))
        else: claims = None
    except Exception as e:
        claims = None
        traceback.print_exc()
        logger.error("Exception while extracting claim from " + str(app_no))
    #print(claims)

    # Find the number of claims
    try:
        number_of_claims = 0
        for clms in c_elem.findall('claim'):
            number_of_claims += 1
    except Exception as e:
        number_of_claims = None
        traceback.print_exc()
        logger.error("Exception while extracting claim from " + str(app_no))
    #print(number_of_claims)

    # Find the number of drawings and figures
    try:
        number_of_figures = 0
        number_of_drawings = 0
        drw_elem = document_root.find('subdoc-drawings')
        if drw_elem != None:
            for fg in drw_elem.findall('figure'):
                img_type = fg.find('image').attrib['ti'].strip()
                if img_type == "DR": number_of_drawings += 1
                elif img_type == "FG": number_of_figures += 1
        else:
            number_of_figures = None
            number_of_drawings = None
    except Exception as e:
        number_of_figures = None
        number_of_drawings = None
        traceback.print_exc()
        logger.error("Exception while extracting figures and drawings num " + str(app_no))
    #print(number_of_figures)
    #print(number_of_drawings)

    # Append SQL data into dictionary to be written later
    processed_application.append({
            "table_name" : "uspto.APPLICATION",
            "ApplicationID" : app_no,
            "PublicationID" : document_id,
            "AppType" : app_type,
            "Title" :  title,
            "FileDate" : app_date,
            "PublishDate" : pub_date,
            "Kind" : kind,
            "USSeriesCode" : series_code,
            "Abstract" : abstract,
            "ClaimsNum" : number_of_claims,
            "DrawingsNum" : number_of_drawings,
            "FiguresNum" : number_of_figures,
            "Description" : description,
            "Claims" : claims,
            "FileName" : args_array['file_name']
        })
    #print(processed_application)

    # Return a dictionary of the processed_ data arrays
    return {
        "processed_application" : processed_application,
        "processed_foreignpriority" : processed_foreignpriority,
        "processed_assignee" : processed_assignee,
        "processed_agent" : processed_agent,
        "processed_inventor" : processed_inventor,
        "processed_usclass" : processed_usclass,
        "processed_intclass" : processed_intclass,
        "processed_cpcclass" : processed_cpcclass
    }
