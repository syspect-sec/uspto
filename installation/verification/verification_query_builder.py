#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Verification Query Builder
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Description: Accepts a file with all the FileNames column included in the
# STARTED_FILES table.  One per line.  A query script will be built that
# shows the results of the verification processess for each file in the bulk-data.
#

# Import modules
import os

# Main Function
if __name__ == "__main__":

    started_files_csv_filepath = "/Users/development/Desktop/started_files.txt"
    destination_filepath = "/Users/development/Desktop/started_files_query.sql"
    print("-- Looking for: " + started_files_csv_filepath)

    # Define the query string.
    query_string = ""
    base_query_start = """
    SELECT *, Count/Expected*100 as Pct
    FROM PARSER_VERIFICATION
    WHERE FileName = '"""
    base_query_finish = """'
    UNION"""

    # Check if the source file is found
    if os.path.isfile(started_files_csv_filepath):
        print("-- Found the STARTED_FILES csv file...")
        # Import the csv from the file
        with open(started_files_csv_filepath, "r") as infile:
            contents = infile.readlines()
        # Each item build into query
        for item in contents:
            # Append to the quert string with the item
            query_string += base_query_start + item.strip() + base_query_finish

        # Strip off the last union
        query_string = query_string.rstrip("UNION")
        print(query_string)
        print("-- Query string built...")
        print("-- Writing query string to file...")
        with open(destination_filepath, "w+") as outfile:
            outfile.write(query_string)
        print("-- Query string written to file...")

    else:
        print("-- Cannot find the STARTED_FILES csv file...")
