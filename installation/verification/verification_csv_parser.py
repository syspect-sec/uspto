#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Verification CSV Parser
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Description: This script will separate the csv exported results from
# verification_query_build.py query.
#

import os

if __name__ == "__main__":

    cwd = os.getcwd() + "/"
    input_filename = "/Users/development/Desktop/Verification_results.csv"
    no_expected_filepath = cwd + "no_expected.txt"

    print("-- Opening input file...")
    # Open the input file for read
    with open(input_filename, "r") as infile:
        contents = infile.readlines()

    print("-- Opening output file...")
    # Open the no_expected_filepath for write
    no_expected_outfile = open(no_expected_filepath, "w+")
    contents.pop(0)
    no_exected_list = []

    # Go though whole file
    for item in contents:
        item_list = []
        item = item.split(",")
        #print(item)
        if item[2] != "NULL" and item[3] != "NULL" and int(item[2]) != 0 and int(item[3]) == 0:
            print("-- Found item with count but no expected: " + item[0] + " - " + item[1]  + "...")
            print("-- Checking if matches other year and table name...")
            # Get the filename and table name
            if len(item[0]) > 4
                # Get only the base of the filetype and year
                if "ipab" in item[0] or "ipgb" in item[0]:
                    filename_start = item[0][:8]
                elif "pgb" in item[0] or "pab" in item[0]:
                    filename_start = item[0][:7]
                item_list.append(item[1])
                no_expected_list.append(item)
            elif len(item[0]) == 4:
                filename_start == item[0]
                table_name = item[1]
                count = item

    for item in
    no_expected_outfile.write(",".join(item).lstrip(","))


    # Close the outfile
    no_expected_outfile.close()
