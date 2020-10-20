#!/usr/bin/env python
# -*- coding: utf-8 -*-

# USPTOEnrich.py
# USPTO Bulk Data Parser - Enrich
# Description: This module enriches the USPTO bulk-data
# using Google BigQuery database.  You will require an
# API key for Google Cloud and have prepared the JSON
# key file in your OS environment.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

#
# Import Modules
#
import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from bs4 import BeautifulSoup
import traceback
import pprint
import json

# Big Query query string to collect a group of assignee data
# from an array of
#

# Class for Google BigQuery used to access public patent data
class PatentBigQuery:

    """
    Columns: [
        publication_number, application_number, country_code,
        kind_code, application_kind, application_number_formatted,
        pct_number, family_id, title_localized, abstract_localized,
        claims_localized, claims_localized_html, description_localized,
        description_localized_html, publication_date, filing_date,
        grant_date, priority_date, priority_claim, inventor,
        inventor_harmonized, assignee, assignee_harmonized, examiner,
        uspc, ipc, cpc, fi, fterm, locarno, citation, entity_status, art_unit
    ]
    """

    # Init the connections
    def __init__(self):
        # Define
        credentials = service_account.Credentials.from_service_account_file("/Users/development/Documents/Elaan/Google-Translate-API-af53f9cd6b03.json")
        project_id = 'bulk-epo-data'
        dataset = 'patents-public-data'
        # Connect
        self.client = bigquery.Client(project=project_id, credentials=credentials)
        self.dataset_ref = self.client.dataset(dataset)
        self.v_out = False

    # Get records that match appID
    def get_priority_records_in_list_to_json(self, app_id_list, where_column=None):
        try:

            if where_column == None:
                where_column = "application_number_formatted"

            # Build string from list
            array_string = self.build_string_from_list_for_query(app_id_list, where_column)

            print("-- Querying BigQuery for Application ID list...")
            # Prepare query
            app_query = """
            SELECT a.patent_id, b.organization, b.name_first, b.name_last
            FROM `patents-public-data.patentsview.patent_assignee` as a
            JOIN `patents-public-data.patentsview.assignee` as b ON
            a.assignee_id = b.id
            WHERE a.patent_id
            IN UNNEST([""" + array_string + """])"""
            if self.v_out: print(app_query)
            # Execute the query
            query = self.client.query(app_query)
            resp = query.result()
            print("Total items: " + str(resp.total_rows))
            if resp.total_rows > 0:
                df = resp.to_dataframe()
                json_obj = df.to_json(orient='records')
                return json_obj
            else: return None
        except Exception as e:
            traceback.print_exc()
            print("-- There was an error querying Google BigQuery...")
            return None

    def build_string_from_list_for_query(self, id_list):
        try:
            # Build the part of the query string with list of AppID
            id_string = "','".join(id_list)
            id_string = "'" + id_string + "'"
            #if self.v_out: print(id_string)
            return id_string
        except Exception as e:
            traceback.print_exc()
            print("-- Failed to build string from PatentID list...")
            return None
