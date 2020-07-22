# USPTOExtractXML4Application.py
# USPTO Bulk Data Parser - Extract XML4 Applications
# Description: Imported to the main USPTOParser.py.  Extracts XML v4 data for applications.
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

# Function used to extract data from XML4 formatted patent applications
def extract_XML4_application(raw_data, args_array):

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
    processed_applicant = []
    processed_agent = []
    processed_inventor = []
    processed_usclass = []
    processed_intclass = []
    processed_cpcclass = []

    # Pass the raw data into Element tree xml object
    document_root = ET.fromstring(raw_data)

    # Start extract XML data
    for r in document_root.findall('us-bibliographic-data-application'):

        # Get basic document ID information
        pr = r.find('publication-reference')
        pub_doc = pr.find('document-id')
        try: pub_country = pub_doc.findtext('country').strip()
        except:pub_country = None
        try:
            document_id = pub_doc.findtext('doc-number').strip()
            document_id = USPTOSanitizer.fix_patent_number(document_id)
        except:
            document_id = None
            logger.error("No Patent Number was found for: " + url_link)
        try: kind = pub_doc.findtext('kind').strip()[:2]
        except: kind = None
        try: pub_date = USPTOSanitizer.return_formatted_date(pub_doc.findtext('date'), args_array, document_id)
        except: pub_date = None

        # Get application reference data
        ar = r.find('application-reference')
        if ar is not None:
            try: app_type = ar.attrib['appl-type'].strip()[:45]
            except: app_type = None
            app_doc = ar.find('document-id')
            try: app_country = app_doc.findtext('country').strip()
            except: app_country = None
            try: app_no = app_doc.findtext('doc-number').strip()[:20]
            except: app_no = None
            try: app_date = USPTOSanitizer.return_formatted_date(app_doc.findtext('date'), args_array, document_id)
            except: app_date = None
            # Get series code
            try: series_code = r.findtext('us-application-series-code').strip()[:2]
            except: series_code = None

        # Get Priority Claims
        pcs = r.find('priority-claims')
        if pcs is not None:
            for pc in pcs.findall('priority-claim'):
                try: pc_sequence = USPTOSanitizer.strip_leading_zeros(pc.attrib['sequence'])
                except: pc_sequence = None
                try: pc_kind = pc.attrib['kind'].strip()[:100]
                except: pc_kind = None
                try: pc_country = pc.findtext('country').strip()[:100]
                except: pc_country = None
                try: pc_doc_num = pc.findtext('doc-number').strip()[:100]
                except: pc_doc_num = None
                try: pc_date = USPTOSanitizer.return_formatted_date(pc.findtext('date'), args_array, document_id)
                except: pc_date = None

                # Append SQL data into dictionary to be written later
                processed_foreignpriority.append({
                    "table_name" : "uspto.FOREIGNPRIORITY_A",
                    "ApplicationID" : app_no,
                    "Position" : pc_sequence,
                    "Kind" : pc_kind,
                    "Country" : pc_country,
                    "DocumentID" : pc_doc_num,
                    "PriorityDate" : pc_date,
                    "FileName" : args_array['file_name']
                })
                #print(processed_foreignpriority)

        # Find all international classifications
        ic = r.find('classifications-ipcr')
        position = 1
        if ic is not None:
            for icc in ic.findall('classification-ipcr'):
                for x in icc.getchildren():
                    if(USPTOSanitizer.check_tag_exists(x,'section')):
                        try: i_class_sec = x.text.strip()[:15]
                        except: i_class_sec = None
                    if(USPTOSanitizer.check_tag_exists(x,'class')):
                        try: i_class_cls = x.text.strip()[:15]
                        except:  i_class_cls = None
                    if(USPTOSanitizer.check_tag_exists(x,'subclass')):
                        try: i_class_sub = x.text.strip()[:15]
                        except: i_class_sub = None
                    if(USPTOSanitizer.check_tag_exists(x,'main-group')):
                        try: i_class_mgr = x.text.strip()[:15]
                        except: i_class_mgr = None
                    if(USPTOSanitizer.check_tag_exists(x,'subgroup')):
                        try: i_class_sgr = x.text.strip()[:15]
                        except: i_class_sgr = None

                # Append SQL data into dictionary to be written later
                processed_intclass.append({
                    "table_name" : "uspto.INTCLASS_A",
                    "ApplicationID" : app_no,
                    "Position" : position,
                    "Section" : i_class_sec,
                    "Class" : i_class_cls,
                    "SubClass" : i_class_sub,
                    "MainGroup" : i_class_mgr,
                    "SubGroup" : i_class_sgr,
                    "FileName" : args_array['file_name']
                })
                #print(processed_intclass)
                position += 1

        # Get US Classification data
        nc = r.find('classification-national')
        position = 1
        if nc is not None:
            ncm = nc.find('main-classification')
            if ncm is not None:
                #print(ncm.text)
                n_class_main = None
                n_subclass = None
                n_malformed = 1
                try: n_class_info = nc.findtext('main-classification')
                except: n_class_info = None
                try:
                    n_class_main, n_subclass = USPTOSanitizer.return_US_class_XML4_application(n_class_info)
                    n_class_main = n_class_main.strip()[:5]
                    n_subclass = n_subclass.strip()[:15]
                except:
                    n_class_main = None
                    n_subclass = None
                    n_malformed = 1

                # Append SQL data into dictionary to be written later
                processed_usclass.append({
                    "table_name" : "uspto.USCLASS_A",
                    "ApplicationID" : app_no,
                    "Position" : position,
                    "Class" : n_class_main,
                    "SubClass" : n_subclass,
                    "Malformed" : n_malformed,
                    "FileName" : args_array['file_name']
                })
                #print(processed_usclass)
                position += 1

            # TODO: find an instance of futher classification to parse
            ncs = nc.findall('further-classification')
            for ncs_item in ncs:
                #print("Further: " + ncs_item.text)
                n_class_main = None
                n_subclass = None
                n_malformed = 1
                try:
                    n_class_info = ncs_item.text
                    n_class_main, n_subclass = USPTOSanitizer.return_US_class_XML4_application(n_class_info)
                    n_class_main = n_class_main.strip()[:5]
                    n_subclass = n_subclass.strip()[:15]
                except:
                    n_class_main = None
                    n_subclass = None
                    n_malformed = 1

                # Append SQL data into dictionary to be written later
                processed_usclass.append({
                    "table_name" : "uspto.USCLASS_A",
                    "ApplicationID" : app_no,
                    "Position" : position,
                    "Class" : n_class_main,
                    "SubClass" : n_subclass,
                    "Malformed" : n_malformed,
                    "FileName" : args_array['file_name']
                })
                #print(processed_usclass)
                position += 1

        # Get CPC Classification data
        cpc_class_element = r.find('classifications-cpc')
        # Init position
        position = 1
        if cpc_class_element is not None:
            main_cpc_class_element = cpc_class_element.find('main-cpc')
            if main_cpc_class_element is not None:
                for cpc_class_item in main_cpc_class_element.findall('classification-cpc'):
                    try: cpc_section = cpc_class_item.findtext('section').strip()[:15]
                    except: cpc_section = None
                    try: cpc_class = cpc_class_item.findtext('class').strip()[:15]
                    except: cpc_class = None
                    try: cpc_subclass = cpc_class_item.findtext('subclass').strip()[:15]
                    except: cpc_subclass = None
                    try: cpc_mgr = cpc_class_item.findtext('main-group').strip()[:15]
                    except: cpc_mgr = None
                    try: cpc_sgr = cpc_class_item.findtext('subgroup').strip()[:15]
                    except: cpc_sgr = None

                    # Append SQL data into dictionary to be written later
                    processed_cpcclass.append({
                        "table_name" : "uspto.CPCCLASS_A",
                        "ApplicationID" : app_no,
                        "Position" : position,
                        "Section" : cpc_section,
                        "Class" : cpc_class,
                        "SubClass" : cpc_subclass,
                        "MainGroup" : cpc_mgr,
                        "SubGroup" : cpc_sgr,
                        "FileName" : args_array['file_name']
                    })
                    position += 1

            further_cpc_class = cpc_class_element.find('further-cpc')
            if further_cpc_class is not None:
                for cpc_class_item in further_cpc_class.findall('classification-cpc'):
                    try: cpc_section = cpc_class_item.findtext('section').strip()[:15]
                    except: cpc_section = None
                    try: cpc_class = cpc_class_item.findtext('class').strip()[:15]
                    except: cpc_class = None
                    try: cpc_subclass = cpc_class_item.findtext('subclass').strip()[:15]
                    except: cpc_subclass = None
                    try: cpc_mgr = cpc_class_item.findtext('main-group').strip()[:15]
                    except: cpc_mgr = None
                    try: cpc_sgr = cpc_class_item.findtext('subgroup').strip()[:15]
                    except: cpc_sgr = None

                    # Append SQL data into dictionary to be written later
                    processed_cpcclass.append({
                        "table_name" : "uspto.CPCCLASS_A",
                        "ApplicationID" : app_no,
                        "Position" : position,
                        "Section" : cpc_section,
                        "Class" : cpc_class,
                        "SubClass" : cpc_subclass,
                        "MainGroup" : cpc_mgr,
                        "SubGroup" : cpc_sgr,
                        "FileName" : args_array['file_name']
                    })
                    position += 1

        # Get the title of the application
        try: title = USPTOSanitizer.strip_for_csv(r.findtext('invention-title')[:500])
        except:
            title = None
            logger.error("Title not Found for :" + url_link + " Application ID: " + app_no)

        # Get number of figure, drawings
        nof = r.find('figures')
        if nof is not None:
            try: number_of_drawings = nof.findtext('number-of-drawing-sheets').strip()
            except: number_of_drawings = None
            try: number_of_figures = nof.findtext('number-of-figures').strip()
            except: number_of_figures = None
        else:
            number_of_drawings = None
            number_of_figures = None

        # Check if XML format uses 'us-parties' or 'parties'
        if r.find('us-parties') != None: parties_id_string = "us-parties"
        elif r.find('parties') != None: parties_id_string = "parties"
        else: parties_id_string = "parties"
        prt = r.find(parties_id_string)
        if prt is not None:
            # Increment position
            appl_position = 1
            invt_position = 1
            atn_position = 1
            # Check if the XML format uses 'applicants' or 'us-applicants'
            if prt.find('us-applicants') != None : applicants_id_string = 'us-applicants'
            elif prt.find('applicants') != None : applicants_id_string = 'applicants'
            else: applicants_id_string = 'applicants'
            # Get Applicant data
            appl_elem = prt.find(applicants_id_string)
            # Check if the XML format uses 'applicant' or 'us-applicant'
            if appl_elem.find('us-applicant') != None : applicant_id_string = 'us-applicant'
            elif appl_elem.find('applicant') != None : applicant_id_string = 'applicant'
            else: applicant_id_string = 'applicant'
            for appl in appl_elem.findall(applicant_id_string):
                if(appl.find('addressbook') != None):
                    try: appl_orgname = USPTOSanitizer.strip_for_csv(appl.find('addressbook').findtext('orgname'))[:300]
                    except: appl_orgname = None
                    try: appl_role = appl.find('addressbook').findtext('role')
                    except: appl_role = None
                    try: appl_city = appl.find('addressbook').find('address').findtext('city').strip()[:100]
                    except: appl_city = None
                    try: appl_state = appl.find('addressbook').find('address').findtext('state').strip()[:100]
                    except: appl_state = None
                    try: appl_country = appl.find('addressbook').find('address').findtext('country').strip()[:100]
                    except: appl_country = None
                    try: appl_firstname = USPTOSanitizer.strip_for_csv(appl.find('addressbook').findtext('first-name'))[:100]
                    except: appl_firstname = None
                    try: appl_lastname = USPTOSanitizer.strip_for_csv(appl.find('addressbook').findtext('last-name'))[:100]
                    except: appl_lastname = None

                    # Append SQL data into dictionary to be written later
                    processed_applicant.append({
                        "table_name" : "uspto.APPLICANT_A",
                        "ApplicationID" : app_no,
                        "Position" : appl_position,
                        "OrgName" : appl_orgname,
                        "FirstName" : appl_firstname,
                        "LastName" : appl_lastname,
                        "City" : appl_city,
                        "State" : appl_state,
                        "Country" : appl_country,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_applicant)
                    appl_position += 1

            # Get the inventor data element
            invs = prt.find('inventors')
            # Init position
            position = 1
            if invs is not None:
                # Get all inventors
                for inv in invs.findall("inventor"):
                    if(inv.find('addressbook') != None):
                        try: inv_first_name = inv.find('addressbook').findtext('first-name').strip()[:100]
                        except: inv_first_name = None
                        try: inv_last_name = inv.find('addressbook').findtext('last-name').strip()[:100]
                        except: inv_last_name = None
                        try: inv_city = inv.find('addressbook').find('address').findtext('city').strip()[:100]
                        except: inv_city = None
                        try: inv_state = inv.find('addressbook').find('address').findtext('state').strip()[:100]
                        except: inv_state = None
                        try: inv_country = inv.find('addressbook').find('address').findtext('country').strip()[:100]
                        except: inv_country = None
                        try: inv_nationality = inv.find('nationality').findtext('country').strip()[:100]
                        except: inv_nationality = None
                        try: inv_residence = inv.find('residence').findtext('country').strip()[:300]
                        except: inv_residence = None

                        # Append SQL data into dictionary to be written later
                        processed_inventor.append({
                            "table_name" : "uspto.INVENTOR_A",
                            "ApplicationID" : app_no,
                            "Position" : invt_position,
                            "FirstName" : inv_first_name,
                            "LastName" : inv_last_name,
                            "City" : inv_city,
                            "State" : inv_state,
                            "Country" : inv_country,
                            "Nationality" : inv_nationality,
                            "Residence" : inv_residence,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_inventor)
                        invt_position += 1

            # Init position
            position = 1
            # Get agent data
            #TODO Find if available in application ??? Where
            agents_element = prt.find('agents')
            if agents_element is not None:
                for agent_item in agents_element.findall('agent'):
                    try: asn_sequence = agent_item.attrib['sequence']
                    except: asn_sequence = None
                    if(agent_item.find('addressbook') != None):
                        try: atn_orgname = agent_item.find('addressbook').findtext('orgname').strip()[:300]
                        except: atn_orgname = None
                        try: atn_last_name = agent_item.find('addressbook').findtext('last-name').strip()[:100]
                        except: atn_last_name = None
                        try: atn_first_name = agent_item.find('addressbook').findtext('first-name').strip()[:100]
                        except: atn_first_name = None
                        try: atn_country = agent_item.find('addressbook').find('address').findtext('country').strip()[:100]
                        except: atn_country = None
                        atn_address = None

                        # Append SQL data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_A",
                            "ApplicationID" : app_no,
                            "Position" : atn_position,
                            "OrgName" : atn_orgname,
                            "LastName" : atn_last_name,
                            "FirstName" : atn_first_name,
                            "Country" : atn_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        atn_position += 1

        # Get assignee data
        asn_elem = r.find('assignees')
        # Init position
        position = 1
        if asn_elem is not None:
            for asn_item in asn_elem.findall('assignee'):
                if(asn_item.find('addressbook') != None):
                    try: asn_orgname = asn_item.find('addressbook').findtext('orgname').strip()[:300]
                    except: asn_orgname = None
                    try: asn_firstname = asn_item.find('addressbook').findtext('first-name').strip()[:100]
                    except: asn_firstname = None
                    try: asn_lastname = asn_item.find('addressbook').findtext('last-name').strip()[:100]
                    except: asn_lastname = None
                    try: asn_role = asn_item.find('addressbook').findtext('role').strip()[:5]
                    except: asn_role = None
                    try: asn_city = asn_item.find('addressbook').find('address').findtext('city').strip()[:50]
                    except: asn_city = None
                    try: asn_state = asn_item.find('addressbook').find('address').findtext('state').strip()[:10]
                    except: asn_state = None
                    try: asn_country = asn_item.find('addressbook').find('address').findtext('country').strip()[:3]
                    except: asn_country = None

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

    # Find the abstract
    try:
        abstract_element = document_root.find('abstract')
        if abstract_element is not None:
            abstract = USPTOSanitizer.strip_for_csv(USPTOSanitizer.return_element_text(abstract_element))
        else: abstract = None
    except: abstract = None
    #print(abstract)

    # Find the description
    try:
        description = ""
        d_elem = document_root.find('description')
        if d_elem is not None:
            description += USPTOSanitizer.strip_for_csv(' '.join(d_elem.itertext()))
        else: description = None
    except Exception as e:
        description = None
        #traceback.print_exc()
        logger.error("Exception while extracting description from " + str(app_no) + ": " + traceback.print_exc())
    #print(description)

    # Find the claims
    try:
        claims = ""
        c_elem = document_root.find('claims')
        claims += USPTOSanitizer.strip_for_csv(' '.join(c_elem.itertext()))
    except Exception as e:
        claims = None
        traceback.print_exc()
        logger.error("Exception while extracting claim from " + str(app_no) + ": " + traceback.print_exc())
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
        drw_elem = document_root.find('drawings')
        if drw_elem != None:
            for fg in drw_elem.findall('figure'):
                img_type = fg.find('img').attrib['img-content'].strip()
                if img_type == "drawing": number_of_drawings += 1
                elif img_type == "figure": number_of_figures += 1
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
            "table_name": "uspto.APPLICATION",
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
        "processed_foreignpriority": processed_foreignpriority,
        "processed_applicant": processed_applicant,
        "processed_assignee" : processed_assignee,
        "processed_agent" : processed_agent,
        "processed_inventor" : processed_inventor,
        "processed_usclass" : processed_usclass,
        "processed_intclass" : processed_intclass,
        "processed_cpcclass" : processed_cpcclass,
    }
