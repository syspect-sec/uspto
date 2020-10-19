# USPTOExtractXML4Grant.py
# USPTO Bulk Data Parser - Extract XML 4 Grants
# Description: Imported to the main USPTOParser.py.  Extracts grant data from USPTO XML v4 files.
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

# Function used to extract data from XML4 formatted patent grants
def extract_XML4_grant(raw_data, args_array):

    # Stat process timer
    start_time = time.time()

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Pass the url_link and format into local variables
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
    processed_cpcclass = []
    processed_gracit = []
    processed_forpatcit = []
    processed_nonpatcit = []
    processed_foreignpriority = []

    # Pass the raw_data data into Element Tree
    document_root = ET.fromstring(raw_data)

    # Start the extraction of XML data
    r = document_root.find('us-bibliographic-data-grant')
    if r is not None:
        # Find the main patent grant data
        for pr in r.findall('publication-reference'):
            for di in pr.findall('document-id'):
                try: pub_country = di.findtext('country').strip()
                except: pub_country = None
                try:
                    document_id = di.findtext('doc-number').strip()
                    document_id = USPTOSanitizer.fix_patent_number(document_id)[:20]
                except:
                    document_id = None
                    logger.error("No Patent Number was found for: " + url_link)
                try: kind = di.findtext('kind').strip()[:2]
                except: kind = None
                try: pub_date = USPTOSanitizer.return_formatted_date(di.findtext('date'), args_array, document_id)
                except: pub_date = None

        # Find the main application data
        for ar in r.findall('application-reference'):
            try: app_type = ar.attrib['appl-type'][:45].strip()
            except: app_type = None
            for di in ar.findall('document-id'):
                try: app_country = di.findtext('country').strip()
                except: app_country = None
                try: app_no = di.findtext('doc-number')[:20].strip()
                except: app_no = None
                try: app_date = USPTOSanitizer.return_formatted_date(di.findtext('date'), args_array, document_id)
                except: app_date = None

        # Get the series code
        try: series_code = r.findtext('us-application-series-code')[:2].strip()
        except: series_code = None
        # Get the length of grant
        try: grant_length = r.find("us-term-of-grant").findtext("length-of-grant").strip()
        except: grant_length = None

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
                    "table_name" : "uspto.INTCLASS_G",
                    "GrantID" : document_id,
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

        # Init positions for CPC and US classifications
        cpc_position = 1
        nc_position = 1
        # TODO: So much more fields available in the XML4 grant cpc-classifications
        # Find CPC Classifications in main root
        # This section is not required since the 'classification-cpc-text' provides same data
        #
        """
        cpcs = r.find('classifications-cpc')
        if cpcs is not None:
            cpc_main = cpcs.find('main-cpc').find('classification-cpc')
            if cpc_main is not None:
                cpc_section = None
                cpc_class = None
                cpc_subclass = None
                cpc_class_mgr = None
                cpc_class_sgr = None
                try: cpc_section = cpc_item.findtext('section')
                except: cpc_section = None
                try: cpc_class = cpc_item.findtext('class')
                except: cpc_class = None
                try: cpc_subclass = cpc_item.findtext('subclass')
                except: cpc_subclass = None
                try: cpc_class_mgr = cpc_item.findtext('main-group')
                except: cpc_class_mgr = None
                try: cpc_class_sgr = cpc_item.findtext('subgroup')
                except: cpc_class_sgr = None

                # Append SQL data into dictionary to be written later
                processed_cpcclass.append({
                    "table_name" : "uspto.CPCCLASS_G",
                    "GrantID" : document_id,
                    "Position" : cpc_position,
                    "Section" : cpc_section,
                    "Class" : cpc_class,
                    "SubClass" : cpc_subclass,
                    "MainGroup" : cpc_class_mgr,
                    "SubGroup" : cpc_class_sgr,
                    "FileName" : args_array['file_name']
                })
                #print(processed_cpcclass)
                cpc_position += 1

            # Collect further CPC classifications
            cpcf = cpcs.find('further-cpc')
            if cpcf is not None:
                for cpc_item in cpcf.findall('classification-cpc'):
                    cpc_section = None
                    cpc_class = None
                    cpc_subclass = None
                    cpc_class_mgr = None
                    cpc_class_sgr = None
                    try: cpc_section = cpc_item.findtext('section')
                    except: cpc_section = None
                    try: cpc_class = cpc_item.findtext('class')
                    except: cpc_class = None
                    try: cpc_subclass = cpc_item.findtext('subclass')
                    except: cpc_subclass = None
                    try: cpc_class_mgr = cpc_item.findtext('main-group')
                    except: cpc_class_mgr = None
                    try: cpc_class_sgr = cpc_item.findtext('subgroup')
                    except: cpc_class_sgr = None

                    # Append SQL data into dictionary to be written later
                    processed_cpcclass.append({
                        "table_name" : "uspto.CPCCLASS_G",
                        "GrantID" : document_id,
                        "Position" : cpc_position,
                        "Section" : cpc_section,
                        "Class" : cpc_class,
                        "SubClass" : cpc_subclass,
                        "MainGroup" : cpc_class_mgr,
                        "SubGroup" : cpc_class_sgr,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_cpcclass)
                    cpc_position += 1
        """

        # Find all CPC classifications
        foc = r.find('us-field-of-classification-search')
        if foc is not None:
            for cpc in foc.findall('classification-cpc-text'):
                cpc_section = None
                cpc_class = None
                cpc_subclass = None
                cpc_class_mgr = None
                cpc_class_sgr = None
                try:
                    #print(cpc.text)
                    cpc_text = cpc.text
                    cpc_class_string, cpc_group_string = cpc_text.split(" ")
                    #print(cpc_class_string + " " + cpc_group_string)
                    cpc_section = cpc_text.strip()[0]
                    cpc_class = cpc_class_string.strip()[1:3]
                    cpc_subclass = cpc_class_string.strip()[3]
                    cpc_class_mgr, cpc_class_sgr = cpc_group_string.rsplit("/", 1)
                    cpc_class_mgr = cpc_class_mgr.strip()[:15]
                    cpc_class_sgr = cpc_class_sgr.strip()[:15]
                    #print(cpc_class_sec + " " + cpc_class + " " + cpc_subclass + " " + cpc_class_mgr + " " + cpc_class_sgr)
                except:
                    cpc_section = None
                    cpc_class = None
                    cpc_subclass = None
                    cpc_class_mgr = None
                    cpc_class_sgr = None
                    logger.warning("There was an error parsing the cpc class for Grant ID: " + document_id + " in file: " + url_link)
                    logger.warning("Traceback: " + traceback.format_exc())

                # Append SQL data into dictionary to be written later
                processed_cpcclass.append({
                    "table_name" : "uspto.CPCCLASS_G",
                    "GrantID" : document_id,
                    "Position" : cpc_position,
                    "Section" : cpc_section,
                    "Class" : cpc_class,
                    "SubClass" : cpc_subclass,
                    "MainGroup" : cpc_class_mgr,
                    "SubGroup" : cpc_class_sgr,
                    "FileName" : args_array['file_name']
                })
                #print(processed_cpcclass)
                cpc_position += 1

            # Find all US classifications
            nc_position = 1
            ncs = foc.findall('classification-national')
            for nc in ncs:
                ncm = nc.find('main-classification')
                if ncm is not None:
                    #print(ncm.text)
                    n_class_main = None
                    n_subclass = None
                    n_malformed = None
                    try:
                        n_class_main, n_subclass = USPTOSanitizer.return_class_XML4_grant(ncm.text)
                    except Exception as e:
                        traceback.print_exc()
                        exit()
                        n_class_main = None
                        n_subclass = None
                        n_malformed = 1

                    # Some are labelled as "None"
                    if n_class_main != None or n_subclass != None:
                        # Append SQL data into dictionary to be written later
                        processed_usclass.append({
                            "table_name" : "uspto.USCLASS_G",
                            "GrantID" : document_id,
                            "Position" : nc_position,
                            "Class" : n_class_main,
                            "SubClass" : n_subclass,
                            "Malformed" : n_malformed,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_usclass)
                        nc_position += 1

                # Collect further US classes
                ncf = nc.find('further-classification')
                if ncf is not None:
                    #print("Further " + ncf.text)
                    n_class_main = None
                    n_subclass = None
                    n_malformed = None
                    try: n_class_main, n_subclass = USPTOSanitizer.return_class_XML4_grant(ncf.text)
                    except Exception as e:
                        traceback.print_exc()
                        exit()
                        n_class_main = None
                        n_subclass = None
                        n_malformed = 1

                    # Some are labelled as "None"
                    if n_class_main != None or n_subclass != None:
                        # Append SQL data into dictionary to be written later
                        processed_usclass.append({
                            "table_name" : "uspto.USCLASS_G",
                            "GrantID" : document_id,
                            "Position" : position,
                            "Class" : n_class_main,
                            "SubClass" : n_subclass,
                            "Malformed" : n_malformed,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_usclass)
                        position += 1

        # Find the title of the patent
        try: title = USPTOSanitizer.strip_for_csv(r.findtext('invention-title')[:500])
        except: title = None

        # Find all references cited in the grant
        # Check if the XML format is using 'us-references-cited' or 'references-cited'
        if r.find('us-references-cited') != None: ref_cited_id_string = "us-references-cited"
        elif r.find('references-cited') != None: ref_cited_id_string = "references-cited"
        else: ref_cited_id_string = "references"
        rf = r.find(ref_cited_id_string)
        if rf != None:
            # Check if the XML format is using 'citation' or 'us-citation'
            if rf.find('citation') != None: citation_id_string = "citation"
            elif rf.find('us-citation') != None: citation_id_string = "us-citation"
            else: citation_id_string = "us-citation"
            uspatcit_position = 1
            forpatcit_position = 1
            nptc_position = 1
            all_rfc = rf.findall(citation_id_string)
            for rfc in all_rfc:
                # If the patent citation child is found must be a patent citation
                if rfc.find('patcit') != None:
                    x = rfc.find('patcit')
                    try: citation_country = x.find('document-id').findtext('country').strip()[:5]
                    except: citation_country = None
                    try: citation_grant_id = x.find('document-id').findtext('doc-number').strip()[:20]
                    except: citation_grant_id = None
                    try: citation_kind = x.find('document-id').findtext('kind').strip()[:10]
                    except: citation_kind = None
                    try: citation_name = x.find('document-id').findtext('name').strip()[:100]
                    except: citation_name = None
                    try: citation_date = USPTOSanitizer.return_formatted_date(x.find('document-id').findtext('date'), args_array, document_id)
                    except: citation_date = None
                    try: citation_category = rfc.findtext('category').strip().upper()[:20]
                    except Exception as e: citation_category = None
                    # US patent citations
                    if(citation_country.strip().upper() == 'US'):

                        # Append SQL data into dictionary to be written later
                        processed_gracit.append({
                            "table_name" : "uspto.GRACIT_G",
                            "GrantID" : document_id,
                            "Position" : uspatcit_position,
                            "CitedID" : citation_grant_id,
                            "Kind" : citation_kind,
                            "Name" : citation_name,
                            "Date" : citation_date,
                            "Country" : citation_country,
                            "Category" : citation_category,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_usclass)
                        uspatcit_position += 1

                    elif citation_country.strip().upper() != 'US':

                        # Append SQL data into dictionary to be written later
                        processed_forpatcit.append({
                            "table_name" : "uspto.FORPATCIT_G",
                            "GrantID" : document_id,
                            "Position" : forpatcit_position,
                            "CitedID" : citation_grant_id,
                            "Kind" : citation_kind,
                            "Name" : citation_name,
                            "Date" : citation_date,
                            "Country" : citation_country,
                            "Category" : citation_category,
                            "FileName" : args_array['file_name']
                        })
                        forpatcit_position += 1
                        #print(processed_forpatcit)

                # If the non-patent citations are found
                elif rfc.find('nplcit') != None:
                    x = rfc.find('nplcit')
                    # Sometimes, there will be '<i> or <sup>, etc.' in the reference string; we need to remove it
                    try:
                        npatcit_text = USPTOSanitizer.strip_for_csv(x.findtext('othercit'))
                        #npatcit_text.replace("<", "").replace(">","")
                    except: npatcit_text = None
                    try: citation_category = rfc.findtext('category').strip().upper()[:20]
                    except: citation_category = None

                    # Append SQL data into dictionary to be written later
                    processed_nonpatcit.append({
                        "table_name" : "uspto.NONPATCIT_G",
                        "GrantID" : document_id,
                        "Position" : nptc_position,
                        "Citation" : npatcit_text,
                        "Category" : citation_category,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_nonpatcit)
                    nptc_position += 1

        # Find number of claims
        try: claims_num = r.findtext('number-of-claims').strip()
        except: claims_num = None

        # Find the number of figures and number of drawings
        nof = r.find('figures')
        try:
            number_of_drawings = nof.findtext('number-of-drawing-sheets').strip()
            number_of_drawings = number_of_drawings.split("/")[0].strip()
        except: number_of_drawings = None
        try: number_of_figures = nof.findtext('number-of-figures').strip()
        except: number_of_figures = None

        # Find the parties
        # Check if XML format uses 'us-parties' or 'parties'
        if r.find('us-parties') != None: parties_id_string = "us-parties"
        elif r.find('parties') != None: parties_id_string = "parties"
        else: parties_id_string = "parties"
        # Get the main parties XML tag
        prt = r.find(parties_id_string)
        if prt != None:
            appl_position = 1
            invt_position = 1
            # Find all applicant data
            # Check if the XML format uses 'applicants' or 'us-applicants'
            if prt.find('us-applicants') != None : applicants_id_string = 'us-applicants'
            elif prt.find('applicants') != None : applicants_id_string = 'applicants'
            else: applicants_id_string = 'applicants'
            # Grab the layered applicants tag
            apts = prt.find(applicants_id_string)
            if apts != None:
                # Check if the XML format uses 'applicant' or 'us-applicant'
                if apts.find('us-applicant') != None : applicant_id_string = 'us-applicant'
                elif apts.find('applicant') != None : applicant_id_string = 'applicant'
                else: applicant_id_string = 'applicant'
                for apt in apts.findall(applicant_id_string):
                    # Get the inventor status of the applicant
                    try: inventor_status = apt.attrib['app-type']
                    except: inventor_status = None
                    if(apt.find('addressbook') != None):
                        try: applicant_orgname = apt.find('addressbook').findtext('orgname')[:300].strip()
                        except: applicant_orgname = None
                        try: applicant_first_name = apt.find('addressbook').findtext('first-name')[:100].strip()
                        except: applicant_first_name = None
                        try: applicant_last_name = apt.find('addressbook').findtext('last-name')[:100].strip()
                        except: applicant_last_name = None
                        try: applicant_city = apt.find('addressbook').find('address').findtext('city')[:100].strip()
                        except: applicant_city = None
                        try: applicant_state = apt.find('addressbook').find('address').findtext('state')[:25].strip()
                        except: applicant_state = None
                        try: applicant_country = apt.find('addressbook').find('address').findtext('country')[:5].strip()
                        except: applicant_country = None
                        try: inventor_residence = apt.findtext('residence')[:100].strip()
                        except: inventor_residence = None

                        # Append SQL data into dictionary to be written later
                        processed_applicant.append({
                            "table_name" : "uspto.APPLICANT_G",
                            "GrantID" : document_id,
                            "OrgName" : applicant_orgname,
                            "Position" : appl_position,
                            "FirstName" : applicant_first_name,
                            "LastName" : applicant_last_name,
                            "City" : applicant_city,
                            "State" : applicant_state,
                            "Country" : applicant_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_applicant)
                        appl_position += 1

                        # Check if the applicant is inventor
                        if "inventor" in inventor_status:
                            # Append SQL data into dictionary to be written later
                            processed_inventor.append({
                                "table_name" : "uspto.INVENTOR_G",
                                "GrantID" : document_id,
                                "Position" : invt_position,
                                "FirstName" : applicant_first_name,
                                "LastName" : applicant_last_name,
                                "City" : applicant_city,
                                "State" : applicant_state,
                                "Country" : applicant_country,
                                "Residence" : inventor_residence,
                                "FileName" : args_array['file_name']
                            })
                            #print(processed_inventor)
                            invt_position += 1

            # Find all inventor data
            for invts in prt.findall('inventors'):
                for inv in invts.findall('inventor'):
                    try: inventor_sequence = USPTOSanitizer.strip_leading_zeros(inv.attrib['sequence'])
                    except: inventor_sequence = position
                    if inv.find('addressbook') != None:
                        try: inventor_first_name = inv.find('addressbook').findtext('first-name')[:100].strip()
                        except: inventor_first_name = None
                        try: inventor_last_name = inv.find('addressbook').findtext('last-name')[:100].strip()
                        except: inventor_last_name = None
                        try: inventor_city = inv.find('addressbook').find('address').findtext('city')[:100].strip()
                        except: inventor_city = None
                        try: inventor_state = inv.find('addressbook').find('address').findtext('state')[:100].strip()
                        except: inventor_state = None
                        try:
                            inventor_country = inv.find('addressbook').find('address').findtext('country')[:5].strip()
                        except: inventor_country = None
                        try: inventor_residence = inv.find('addressbook').find('address').findtext('country')[:5].strip()
                        except: inventor_residence = None

                        # Append SQL data into dictionary to be written later
                        processed_inventor.append({
                            "table_name" : "uspto.INVENTOR_G",
                            "GrantID" : document_id,
                            "Position" : invt_position,
                            "FirstName" : inventor_first_name,
                            "LastName" : inventor_last_name,
                            "City" : inventor_city,
                            "State" : inventor_state,
                            "Country" : inventor_country,
                            "Residence" : inventor_residence,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_inventor)
                        invt_position += 1

            # Find all agent data
            for agns in prt.findall('agents'):
                position = 1
                for agn in agns.findall('agent'):
                    try: agent_sequence = USPTOSanitizer.strip_leading_zeros(agn.attrib['sequence'])
                    except: agent_sequence = position
                    if(agn.find('addressbook') != None):
                        try: agent_orgname = agn.find('addressbook').findtext('orgname')[:300].strip()
                        except: agent_orgname = None
                        try: agent_last_name = agn.find('addressbook').findtext('last-name')[:100].strip()
                        except: agent_last_name = None
                        try: agent_first_name = agn.find('addressbook').findtext('first-name')[:100].strip()
                        except: agent_first_name = None
                        try: agent_country = agn.find('addressbook').find('address').findtext('country')[:3].strip()
                        except: agent_country = None

                        # Append SQL data into dictionary to be written later
                        processed_agent.append({
                            "table_name" : "uspto.AGENT_G",
                            "GrantID" : document_id,
                            "Position" : agent_sequence,
                            "OrgName" : agent_orgname,
                            "LastName" : agent_last_name,
                            "FirstName" : agent_first_name,
                            "Country" : agent_country,
                            "FileName" : args_array['file_name']
                        })
                        #print(processed_agent)
                        position += 1

        # Find all assignee data
        for asn in r.findall('assignees'):
            position = 1
            for x in asn.findall('assignee'):
                if(x.find('addressbook') != None):
                    try: asn_orgname = x.find('addressbook').findtext('orgname')[:500].strip()
                    except: asn_orgname = None
                    try: asn_role = x.find('addressbook').findtext('role')[:45].strip()
                    except: asn_role = None
                    try: asn_city = x.find('addressbook').find('address').findtext('city')[:100].strip()
                    except: asn_city = None
                    try: asn_state = x.find('addressbook').find('address').findtext('state')[:100].strip()
                    except: asn_state = None
                    try: asn_country = x.find('addressbook').find('address').findtext('country')[:5].strip()
                    except: asn_country = None

                    # Append SQL data into dictionary to be written later
                    processed_assignee.append({
                        "table_name" : "uspto.ASSIGNEE_G",
                        "GrantID" : document_id,
                        "Position" : position,
                        "OrgName" : asn_orgname,
                        "Role" : asn_role,
                        "City" : asn_city,
                        "State" : asn_state,
                        "Country" : asn_country,
                        "FileName" : args_array['file_name']
                    })
                    #print(processed_assignee)
                    position += 1

        # Find all examiner data
        for exm in r.findall('examiners'):
            position = 1
            for x in exm.findall('primary-examiner'):
                try: exm_last_name = x.findtext('last-name')[:50].strip()
                except: exm_last_name = None
                try: exm_first_name = x.findtext('first-name')[:50].strip()
                except: exm_first_name = None
                try: exm_department = x.findtext('department')[:100].strip()
                except: exm_department = None

                # Append SQL data into dictionary to be written later
                processed_examiner.append({
                    "table_name" : "uspto.EXAMINER_G",
                    "GrantID" : document_id,
                    "Position" : position,
                    "LastName" : exm_last_name,
                    "FirstName" : exm_first_name,
                    "Department" : exm_department,
                    "FileName" : args_array['file_name']
                })
                #print(processed_examiner)
                position += 1

            for x in exm.findall('assistant-examiner'):
                try: exm_last_name = x.findtext('last-name')[:50].strip()
                except: exm_last_name = None
                try: exm_first_name = x.findtext('first-name')[:50].strip()
                except: exm_first_name = None
                try: exm_department = x.findtext('department')[:100].strip()
                except: exm_department = None

                # Append SQL data into dictionary to be written later
                processed_examiner.append({
                    "table_name" : "uspto.EXAMINER_G",
                    "GrantID" : document_id,
                    "Position" : position,
                    "LastName" : exm_last_name,
                    "FirstName" : exm_first_name,
                    "Department" : exm_department,
                    "FileName" : args_array['file_name']
                })
                #print(processed_examiner)
                position += 1

        # Find main priority claims tag
        pcs = r.find('priority-claims')
        position = 1
        if pcs is not None:
            # Find all priority claims in main tag
            for pc in pcs.findall('priority-claim'):
                # Assign data to vars
                try:  pc_country = pc.findtext('country')[:5].strip()
                except: pc_country = None
                try: pc_kind = pc.attrib['kind'][:45].strip()
                except: pc_kind = None
                try: pc_doc_num = pc.findtext('doc-number')[:45].strip()
                except: pc_doc_num = None
                try: pc_date = USPTOSanitizer.return_formatted_date(pc.findtext('date'), args_array, document_id)
                except: pc_date = None

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

    # Find the abstract
    try:
        a_elem = document_root.find('abstract')
        if a_elem is not None:
            abstract = USPTOSanitizer.strip_for_csv(USPTOSanitizer.return_element_text(a_elem))
        else: abstract = None
    except Exception as e:
        abstract = None
        #traceback.print_exc()
        #logger.error("Exception while extracting abstract from " + str(document_id) + ": " + traceback.print_exc())
    #print(abstract)

    # Find the description
    try:
        d_elem = document_root.find('description')
        if d_elem is not None:
            description = USPTOSanitizer.strip_for_csv(' '.join(d_elem.itertext()))
        else: description = None
    except Exception as e:
        description = None
        #traceback.print_exc()
        #logger.error("Exception while extracting description from " + str(document_id) + ": " + traceback.print_exc())
    #print(description)

    # Find the claims
    try:
        c_elem = document_root.find('claims')
        if c_elem is not None:
            claims = USPTOSanitizer.strip_for_csv(' '.join(c_elem.itertext()))
        else: claims = None
    except Exception as e:
        claims = None
        #traceback.print_exc()
        #logger.error("Exception while extracting claim from " + str(document_id) + ": " + traceback.print_exc())
    #print(claims)

    # Append SQL data into dictionary to be written later
    try:
        processed_grant.append({
            "table_name" : "uspto.GRANT",
            "GrantID" : document_id,
            "Title" : title,
            "IssueDate" : pub_date,
            "Kind" : kind,
            "USSeriesCode" : series_code,
            "Abstract" : abstract,
            "ClaimsNum" : claims_num,
            "DrawingsNum" : number_of_drawings,
            "FiguresNum" : number_of_figures,
            "ApplicationID" : app_no,
            "Description" : description,
            "Claims" : claims,
            "FileDate" : app_date,
            "AppType" : app_type,
            "GrantLength" : grant_length,
            "FileName" : args_array['file_name']
        })
    except Exception as e:
        traceback.print_exc()
        logger.warning("Could not append patent data to array for patent number: " + document_id + " Traceback: " + traceback.format_exc())

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
        "processed_cpcclass" : processed_cpcclass,
        "processed_gracit" : processed_gracit,
        "processed_forpatcit" : processed_forpatcit,
        "processed_nonpatcit" : processed_nonpatcit,
        "processed_foreignpriority" : processed_foreignpriority
    }
