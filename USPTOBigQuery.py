#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Google BigQuery PAIR Patent Data Retrieval
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Description: Contains many functions for querying Google BigQuery API for patents
#

#
# Import Modules
#
import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import traceback
import pprint
import json

# Import USPTO Parser modules
import USPTOLogger
import USPTOSanitizer
import SQLProcessor

# Class for Google BigQuery used to access public patent data
class PatentBigQuery:


    # Init the connections
    def __init__(self, args_array):
        # Define vars for authentication
        credentials = service_account.Credentials.from_service_account_file("/Users/development/Documents/Elaan/Google-Translate-API-af53f9cd6b03.json")
        project_id = 'bulk-epo-data'
        dataset = 'patents-public-data'
        # Connect
        self.client = bigquery.Client(project=project_id, credentials=credentials)
        self.dataset_ref = self.client.dataset(dataset)
        self.v_out = False

    # Retrieves the CPC classifications for all 2005 patents
    # Which are not included in the uspto bulk data
    def get_2005_grant_classifications(self, args_array):

        # Start timer
        start_time = time.time()
        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        print("-- Checking for existing 2005 grant CPC class data file...")
        # Check for existing datafile already and read in from file if exists
        if os.path.isfile(args_array['BQ_2005_classification_dataframe_filename']):
            print("-- Found existing 2005 grant CPC class data file...")
            # Read the dataframe back from file
            df = pd.read_pickle(args_array['BQ_2005_classification_dataframe_filename'])
            # Conver to JSON object
            json_obj = df.to_json(orient='records')

            print("-- All 2005 patent classification codes retreived from Google BigQuery successfully.")
            logger.info("-- All 2005 patent classification codes retreived from Google BigQuery successfully.")

            #pprint.pprint(json_obj)
            return json_obj

        # If file is not found then get from BigQuery
        else:
            print("-- No existing 2005 grant CPC class data file found...")
            print("-- Fetching 2005 grant CPC class data from Google BigQuery...")
            try:
                # Build query to retrieve all US grants CPC code from 2005
                sql = """
                SELECT
                publication_number, cpc, ipc, grant_date
                FROM `patents-public-data.patents.publications`
                WHERE grant_date > 20041231 AND grant_date < 20060101
                AND publication_number LIKE 'US%' """
                print(sql)
                # Prepare query for BigQuery submission
                query = self.client.query(sql)
                # Get results
                resp = query.result()
                # Convert response to df
                df = resp.to_dataframe()
                # Serialize the dataframe to a file
                bq.pickle_dataframe_response(df, args_array['BQ_2005_classification_dataframe_filename'])
                print("-- 2005 grant CPC class stored to file " + args_array['BQ_2005_classification_dataframe_filename'] + "...")
                # Conver to JSON object
                json_obj = df.to_json(orient='records')

                print("-- All 2005 classification codes retreived from Google BigQuery successfully")
                logger.info("-- All 2005 classification codes retreived from Google BigQuery successfully")

                # Return the JSON object of data
                #pprint.pprint(json_obj)
                return json_obj

            except Exception as e:
                # If the insertion process failed then exit with status 1
                traceback.print_exc()
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                print("-- Failed to retrieve 2005 classification codes from Google BigQuery")
                logger.info("-- Failed to retrieve all 2005 classification codes from Google BigQuery")
                exit(1)

    # Inserts the CPC classifications for all 2005 patents
    # into the database
    def insert_2005_grant_classifications(self, args_array, json_obj):

        # Start timer
        start_time = time.time()
        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        try:

            # Insert the items in the json object into the appropiate
            # patent grant in the database
            for item in json_obj:
                # Extract the patent grant ID from the document number
                publication_number = item['publication_number'].split("-")[1]
                # Create an array to hold all CPC codes for the patent
                cpc_array = []
                ipc_array = []
                # Loop through all CPC codes for the item and
                # convert to dict
                for code in item['cpc']:
                    cpc_dict = USPTOSanitizer.extract_BQ_CPC_string_to_dict(code['code'])
                    # Append the CPC dict to array
                    cpc_array.append(cpc_dict)
                # Loop through all IPC codes for the item and
                # convert to dict
                for code in itemp['ipc']:
                    ipc_dict = USPTOSanitizer.extract_BQ_CPC_string_to_dict(code['code'])
                    # Append the CPC dict to array
                    ipc_array.append(ipc_dict)

                # Pass the publication_number and cpc_array to SQL to be inserted
                args_array['database_connection'].insert_CPC_patched_item(publication_number, cpc_array)
                # Pass the publication_number and ipc_array to SQL to be inserted
                args_array['database_connection'].insert_IPC_patched_item(publication_number, ipc_array)

            print("-- All 2005 classification codes inserted into database successfully")
            logger.info("-- All 2005 classification codes inserted into database successfully")
            exit(0)

        except Exception as e:
            # If the insertion process failed then exit with status 1
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
            print("-- Failed to insert all 2005 classification codes inserted into database")
            logger.info("-- Failed to insert all 2005 classification codes inserted into database")
            exit(1)

#
# Main Function
#
# NOTE: You can modify this code and run the class from command line
if __name__ == "__main__":

    input_file = os.getcwd() + "/df_cpc_results.json"
    output_file = os.getcwd() + "/df_cpc_results.json"
    json_output_file = os.getcwd() + "/json_cpc_results.json"

    # Parse Items
    parse_items = False
    parse_list = True

    # Instansiate class object
    bq = PatentBigQuery()
    df = bq.get_2005_grant_cpc(output_file)

    json_obj = df.to_json(orient='records')
    pprint.pprint(json_obj)
