#!/usr/bin/env python
# -*- coding: utf-8 -*-
# USPTO SQLProcessor
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

import MySQLdb
import psycopg2
import traceback
import time
import sys
import os
from pprint import pprint

# Import USPTO Parser Functions
import USPTOLogger
import USPTOSanitizer

class SQLProcess:

    # TODO: write the script to accept a database password from stdin
    def __init__(self, database_args):

        # Pass the database type to class variable
        self.database_type = database_args['database_type']

        # Define class variables
        self._host = database_args['host']
        self._port = database_args['port']
        self._username = database_args['user']
        self._password = database_args['passwd']
        self._dbname = database_args['db']
        self._charset = database_args['charset']
        self._conn = None
        self._cursor = None

    def connect(self):

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        # Connect to MySQL
        if self.database_type == "mysql":

            try:
                if self._conn == None:
                    self._conn = MySQLdb.connect(
                        host = self._host,
                        user = self._username,
                        passwd = self._password,
                        db = self._dbname,
                        port = self._port,
                        charset = self._charset
                    )
                    print("Connection to MySQL database established.")
                    logger.info("Connection to MySQL database established.")

                if self._cursor == None:
                    self._cursor = self._conn.cursor()
                    self._cursor.connection.autocommit(True)
            except:
                traceback.print_exc()
                exit()

        # Connect to PostgreSQL
        if self.database_type == "postgresql":

            if self._conn == None:
                # Get a connection, if a connect cannot be made an exception will be raised here
                self._conn = psycopg2.connect("host=" + self._host +  " dbname=" + self._dbname + " user=" + self._username + " password=" + self._password + " port=" + str(self._port))
                self._conn.autocommit = True

            if self._cursor == None:
                # conn.cursor will return a cursor object, you can use this cursor to perform queries
                self._cursor = self._conn.cursor()
                print("Connection to PostgreSQL database established.")
                logger.info("Connection to PostgreSQL database established.")

            # Get a list of all tables available in the database
            table_list = self.get_list_of_all_uspto_tables();


    # Load the insert query into the database
    def load(self, sql, args_array):

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        # Connect to database if not connected
        if self._conn == None:
            self.connect()

        # Execute the query passed into funtion
        try:
            self._cursor.execute(sql)
            #self._conn.commit()
        except Exception as e:
            # If there is an error and using databse postgresql
            # Then rollback the commit??
            if self.database_type == "postgresql":
                self._conn.rollback()

            print("Database INSERT query failed... " + args_array['file_name'] + " into table: " + args_array['table_name'] + " Document ID Number " + args_array['document_id'])
            logger.error("Database INSERT query failed..." + args_array['file_name'] + " into table: " + args_array['table_name'] + " Document ID Number " + args_array['document_id'])
            print("Query string: " + sql)
            logger.error("Query string: " + sql)
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())


    # This function accepts an array of csv files which need to be inserted
    # using COPY command in postgresql and LOAD INFILE in MySQL
    def load_csv_bulk_data(self, args_array, data_type, csv_file_obj):

        # Set the start time
        start_time = time.time()

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")
        print('[Staring to load csv files in bulk to ' + args_array['database_type'] + ']')
        logger.info('Staring to load csv files in bulk to ' + args_array['database_type'])

        # Connect to database if not connected
        if self._conn == None:
            self.connect()

        if "table_name" in csv_file_obj:
            # Print message to stdout and log about which table is being inserted
            print("Database bulk load query started for: " + data_type + " from filename: " + csv_file_obj['csv_file_name'])
            logger.info("Database bulk load query started for: " + data_type + " from filename: " + csv_file_obj['csv_file_name'])

            # If postgresql build query
            if self.database_type == "postgresql":

                # Set flag to determine if the query was successful
                bulk_insert_successful = False
                bulk_insert_failed_attempts = 0
                # Loop until successfull insertion
                while bulk_insert_successful == False:

                    try:
                        sql = "COPY " + self._dbname + "." + csv_file_obj['table_name'] + " FROM STDIN DELIMITER '|' CSV HEADER"
                        self._cursor.copy_expert(sql, open(csv_file_obj['csv_file_name'], "r"))
                        # Return a successfull insertion flag
                        bulk_insert_successful = True

                    except Exception as e:
                        # Roll back the transaction
                        self._conn.rollback()
                        # Increment the failed counter
                        bulk_insert_failed_attempts += 1
                        print("Database bulk load query failed... " + csv_file_obj['csv_file_name'] + " into table: " + csv_file_obj['table_name'])
                        logger.error("Database bulk load query failed..." + csv_file_obj['csv_file_name'] + " into table: " + csv_file_obj['table_name'])
                        print("Query string: " + sql)
                        logger.error("Query string: " + sql)
                        traceback.print_exc()
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                        # If the cause was a dupllicate entry error, then try to clean the file
                        traceback_array = traceback.format_exc().splitlines()
                        for line in traceback_array:
                            if "duplicate key" in line:
                                # Insert the csv file item by item
                                #self.insert_csv_item_by_item(csv_file_obj['csv_file_name'], args_array)
                                # Remove the offending line from csv file
                                self.remove_item_from_csv(traceback_array, csv_file_obj['csv_file_name'], "duplicate_key_violation")
                            elif "violates not-null constraint" in line:
                                # Remove the offending line from csv file
                                self.remove_item_from_csv(traceback_array, csv_file_obj['csv_file_name'], "not_null_violation")


                        # Return a unsucessful flag
                        if bulk_insert_failed_attempts > 20:
                            return False

            # If MySQL build query
            elif self.database_type == "mysql":

                # Set flag to determine if the query was successful
                bulk_insert_successful = False
                bulk_insert_failed_attempts = 0
                # Loop until the file was successfully deleted
                # NOTE : Used because MySQL has table lock errors
                while bulk_insert_successful == False:

                    try:
                        # TODO: consider "SET foreign_key_checks = 0" to ignore
                        # TODO: LOCAL is used to set duplicate key to warning instead of error
                        # TODO: IGNORE is also used to ignore rows that violate duplicate unique key constraints
                        bulk_insert_sql = "LOAD DATA LOCAL INFILE '" + csv_file_obj['csv_file_name'] + "' INTO TABLE " + csv_file_obj['table_name'] + " FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n' IGNORE 1 LINES"
                        bulk_insert_sql = bulk_insert_sql.replace("\\", "/")

                        # Execute the query built above
                        self._cursor.execute(bulk_insert_sql)
                        # Return a successfull insertion flag
                        bulk_insert_successful = True

                    except Exception as e:

                        # Increment the failed counter
                        bulk_insert_failed_attempts += 1
                        print("Database bulk load query attempt " + str(bulk_insert_failed_attempts) + " failed... " + csv_file_obj['csv_file_name'] + " into table: " + csv_file_obj['table_name'])
                        logger.error("Database bulk load query attempt " + str(bulk_insert_failed_attempts) + " failed..." + csv_file_obj['csv_file_name'] + " into table: " + csv_file_obj['table_name'])
                        print("Query string: " + bulk_insert_sql)
                        logger.error("Query string: " + bulk_insert_sql)
                        traceback.print_exc()
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                        # Return a unsucessful flag
                        if bulk_insert_failed_attempts > 8:
                            return False

        # Return a successfull message from the database query insert.
        return True

    # Used to retrieve ID by matching fields of values
    def query(self,sql):
        #try:
        if self._conn == None:
            self.connect()
            self._cursor.execute(sql)
            #self._conn.commit()
            result = self._cursor.fetchone()
            return int(result[0])
        else:
            self._cursor.execute(sql)
            #self._conn.commit()
            result = self._cursor.fetchone()
            return int(result[0])
        #finally:
            #self.close()

    # Used to remove records from database when a file previously
    # started being processed and did not finish. (when insert duplicate ID error happens)
    def remove_previous_file_records(self, call_type, file_name):

        # Set process time
        start_time = time.time()

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")
        print("[Checking database for previous attempt to process the " + call_type + " file: " + file_name + "...]")
        logger.info("[Checking database for previous attempt to process the " + call_type + " file:" + file_name + "...]")

        # Connect to database if not connected
        if self._conn == None:
            self.connect()

        # Set the table_name
        table_name = "STARTED_FILES"

        # Build query to check the STARTED_FILES table to see if this file has been started already.
        check_file_started_sql = "SELECT COUNT(*) as count FROM " + self._dbname + "." + table_name + " WHERE FileName = '" + file_name + "' LIMIT 1"

        # Execute the query to check if file has been stared before
        try:
            self._cursor.execute(check_file_started_sql)
            # Check the count is true or false.
            check_file_started = self._cursor.fetchone()

        except Exception as e:
            # Set the variable and automatically check if database records exist
            check_file_started = True
            # If there is an error and using databse postgresql
            # Then rollback the commit??
            if self.database_type == "postgresql":
                self._conn.rollback()

            print("Database check if " + call_type + " file started failed... " + file_name + " from table: " + self._dbname + ".STARTED_FILES")
            logger.error("Database check if " + call_type + " file started failed... " + file_name + " from table: " + self._dbname + ".STARTED_FILES")
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

        # If no previous attempts to process the file have been found
        if check_file_started[0] == 0:
            # Insert the file_name into the table keeping track of STARTED_FILES
            if self.database_type == "postgresql":
                insert_file_started_sql = "INSERT INTO " + self._dbname + "." + table_name + "  (FileName) VALUES($$" + file_name + "$$)"
            elif self.database_type == "mysql":
                insert_file_started_sql = "INSERT INTO " + self._dbname + "." + table_name + " (FileName) VALUES('" + file_name + "')"

            print("No previous attempt found to process the " + call_type + " file: " + file_name + " in table: " + self._dbname + ".STARTED_FILES")
            logger.info("No previous attempt found to process the " + call_type + " file:" + file_name + " in table: " + self._dbname + ".STARTED_FILES")

            # Insert the record into the database that the file has been started.
            try:
                self._cursor.execute(insert_file_started_sql)

            except Exception as e:
                # If there is an error and using databse postgresql
                # Then rollback the commit??
                if self.database_type == "postgresql":
                    self._conn.rollback()
                print("Database check for previous attempt to process " + call_type + " file failed... " + file_name + " into table: " + self._dbname + ".STARTED_FILES")
                logger.error("Database check for previous attempt to process " + call_type + " file failed... " + file_name + " into table: " + self._dbname + ".STARTED_FILES")
                traceback.print_exc()
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())


        # If the file was found in the STARTED_FILES table,
        # delete all the records of that file in all tables.
        elif check_file_started[0] != 0:

            print("Found previous attempt to process the " + call_type + " file: " + file_name + " in table: " + self._dbname + ".STARTED_FILES")
            logger.info("Found previous attempt to process the " + call_type + " file:" + file_name + " in table: " + self._dbname + ".STARTED_FILES")

            # Build array to hold all table names to have
            # records deleted for patent grants
            if call_type == "grant":
                table_name_array = [
                    "GRANT",
                    "INTCLASS_G",
                    "CPCCLASS_G",
                    "USCLASS_G",
                    "INVENTOR_G",
                    "AGENT_G",
                    "ASSIGNEE_G",
                    "APPLICANT_G",
                    "NONPATCIT_G",
                    "EXAMINER_G",
                    "GRACIT_G",
                    "FORPATCIT_G",
                    "FOREIGNPRIORITY_G"
                ]
            # Records deleted for patent applications
            elif call_type == "application":
                table_name_array = [
                    "APPLICATION",
                    "INTCLASS_A",
                    "USCLASS_A",
                    "CPCCLASS_A",
                    "FOREIGNPRIORITY_A",
                    "AGENT_A",
                    "ASSIGNEE_A",
                    "INVENTOR_A",
                    "APPLICANT_A"
                ]

            # Records deleted for PAIR data
            elif call_type == "PAIR":
                table_name_array = [
                    "TRANSACTION_P",
                    "ADJUSTMENT_P",
                    "ADJUSTMENTDESC_P",
                    "CORRESPONDENCE_P",
                    "CONTINUITYCHILD_P",
                    "CONTINUITYPARENT_P",
                    "EXTENSION_P",
                    "EXTENSIONDESC_P"
                ]

            # Records deleted for classifcation data
            elif call_type == "class":
                table_name_array = [
                    "USCLASS_C",
                    "CPCCLASS_C",
                    "USCPC_C",
                    "WIPOST3_C"
                ]

            # Records deleted for patent litigation data
            elif call_type == "legal":
                table_name_array = [
                    "CASE_L",
                    "PATENT_L",
                    "ATTORNEY_L",
                    "PARTY_L"
                ]

            print("Starting to remove previous attempt to process the " + call_type + " file: " + file_name + " in table: " + self._dbname + ".STARTED_FILES")
            logger.info("Starting to remove previous attempt to process the " + call_type + " file:" + file_name + " in table: " + self._dbname + ".STARTED_FILES")

            # Loop through each table_name defined by call_type
            for table_name in table_name_array:

                # Build the SQL query here
                remove_previous_record_sql = "DELETE FROM " + self._dbname + "." + table_name + " WHERE FileName = '" + file_name + "'"

                # Set flag to determine if the query was successful
                records_deleted = False
                records_deleted_failed_attempts = 1
                # Loop until the file was successfully deleted
                # NOTE : Used because MySQL has table lock errors
                while records_deleted == False and records_deleted_failed_attempts < 10:
                    # Execute the query pass into funtion
                    try:
                        self._cursor.execute(remove_previous_record_sql)
                        records_deleted = True
                        #TODO: check the numer of records deleted from each table and log/print
                        # Print and log finished check for previous attempt to process file
                        print("Finished database delete of previous attempt to process the " + call_type + " file: " + file_name + " table: " + table_name)
                        logger.info("Finished database delete of previous attempt to process the " + call_type + " file:" + file_name + " table: " + table_name)

                    except Exception as e:

                        # If there is an error and using databse postgresql
                        # Then rollback the commit??
                        if self.database_type == "postgresql":
                            self._conn.rollback()
                        print("Database delete attempt " + str(records_deleted_failed_attempts) + " failed... " + file_name + " from table: " + table_name)
                        logger.error("Database delete attempt " + str(records_deleted_failed_attempts) + " failed..." + file_name + " from table: " + table_name)
                        # Increment the failed attempts
                        records_deleted_failed_attempts += 1
                        traceback.print_exc()
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())


    # Used to verify whether the applicationID is in the current table APPLICATION
    def verify(self,sql):
        if self._conn == None:
            self.connect()
            self._cursor.execute(sql)
            #self._conn.commit()
            return self._cursor.fetchone()
        else:
            self._cursor.execute(sql)
            #self._conn.commit()
            return self._cursor.fetchone() #None or not

    def executeParam(self, sql, param):
        #try:
        if self._conn == None:
            self.connect()
            self._cursor.execute(sql, param)
            #self._conn.commit()
            result = self._cursor.fetchall()  #fetchone(), fetchmany(n)
            return result  #return a tuple ((),())
        else:
            self._cursor.execute(sql, param)
            #self._conn.commit()
            result = self._cursor.fetchall()  #fetchone(), fetchmany(n)
            return result  #return a tuple ((),())
        #finally:
            #self.close()

    # Get a list of all tables in the uspto database
    def get_list_of_all_uspto_tables(self):

        # Set process time
        start_time = time.time()

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")
        print("[Checking database for list of all tables...]")
        logger.info("[Checking database for list of all tables...]")

        # Connect to database if not connected
        if self._conn == None:
            self.connect()

        # Execute the query to check if file has been stared before
        try:
            # If using PostgreSQL
            if self.database_type == "postgresql":
                # Build query to get list of all tables in uspto database
                get_table_list_sql = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
                self._cursor.execute(get_table_list_sql)
                # Check the count is true or false.
                table_list = self._cursor.fetchall()
                # Print list of tables found
                for item in table_list:
                    print("--  Table Found: " + item[1])
            # MySQL
            elif self.database_type == "mysql":
                # Build query to get list of all tables in uspto database
                get_table_list_sql = "SHOW TABLES"
                self._cursor.execute(get_table_list_sql)
                # Check the count is true or false.
                table_list = self._cursor.fetchall()
                # Print list of tables found
                for item in table_list:
                    print("--  Table Found: " + item[1])

        except Exception as e:
            # If there is an error and using databse postgresql
            # Then rollback the commit??
            if self.database_type == "postgresql":
                self._conn.rollback()

            # Print and log general fail comment
            print("Database check for table list failed...")
            logger.error("Database check for table list failed")
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

    def close(self):

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        if self._cursor != None:
            self._cursor.close()
            self._cursor = None
        if self._conn != None:
            self._conn.close()
            self._conn = None

        print('Connection to database closed successfully.')
        logger.info('Connection to database closed successfully.')

    # Searches a csv file and extracts any items with the ID in traceback string
    def remove_item_from_csv(self, traceback_array, csv_file_name, violation_type):

        # Set process time
        start_time = time.time()

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")
        print("[Looking for error lines in file " + csv_file_name + "]")
        logger.warning("[Looking for error lines in file " + csv_file_name + "]")

        # Search traceback_array for the item ID
        for line in traceback_array:
            # Find the line that indicates the line of csv file
            # that causese error
            if line.startswith("CONTEXT:"):
                # Get the error line number
                error_line = line.split("line")[1].strip()
                if not error_line.isnumeric(): error_line = error_line.split(":")[0]
                print("Error line number in file " + csv_file_name + " identified as line number " + error_line)
                logger.warning("Error line number in file " + csv_file_name + " identified as line number " + error_line)

                # Open original file in read only mode and dummy file in write mode
                with open(csv_file_name, 'r') as read_file:
                    # Pass the file contents into an array
                    csv_file_array = read_file.readlines()
                    # Pop off the error line
                    del csv_file_array[int(error_line) - 1]
                    #csv_file_array.pop(error_line - 1)
                # Open the file again with write permissions
                with open(csv_file_name, 'w') as write_file:
                    for line in csv_file_array:
                        write_file.write(line)

                print("Error line " + error_line + " has been found and removed from: " + csv_file_name)
                logger.warning("Error line " + error_line + " has been found and removed from: " + csv_file_name)

    # This function will open the csv file and then
    # load it into the database item by item
    def insert_csv_item_by_item(self, csv_file, args_array):

        # Set the start time of operation
        start_time = time.time()

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")
        print("[Reverting to item-by-item insertion for csv file " + csv_file + "...]")
        logger.info("[Reverting to item-by-item insertion for csv file " + csv_file + "...]")

        # Open the file to read and extract array
        with open(csv_file, "r") as csv_infile:
            csv_contents = csv_infile.readlines()

        # Get a list of column names from first item
        fields = csv_contents[0].split("|")
        # Pop the field headers from file
        csv_contents.pop()

        # Insert each item into database
        for item in csv_contents:
            # Build the insert array with field names as keys
            insert_dict = {}
            # Get the table name and add to dict
            insert_dict['table_name'] = self.get_table_name_from_csv_filename(csv_file)

            # Create a data dictionary for the item
            insert_values = item.split("|")
            for i in range(len(fields)):
                insert_dict[fields[i]] = insert_values[i]
            # Build a sql query string for the item
            sql = self.build_sql_insert_query(insert_dict, args_array)
            # Submit the item to database insertion
            self.load(sql, args_array)

        print("[Completed item-by-item insertion for csv file " + csv_file + "...]")
        logger.info("[Completed item-by-item insertion for csv file " + csv_file + "...]")

    # This function accepts the csv_file, extracts the filename and
    # returns the name of the database table associated
    def get_table_name_from_csv_filename(self, csv_file):
        # Get the table extention
        if "CSV_G" in csv_file: table_ext = "_G"
        elif "CSV_A" in csv_file: table_ext = "_A"
        elif "CSV_L" in csv_file: table_ext = "_L"
        elif "CSV_P" in csv_file: table_ext = "_P"
        elif "CSV_C" in csv_file: table_ext = "_C"
        # Remove file extention
        csv_file = csv_file.split("/")[-1].replace(".csv", "")
        # Get target table name
        if "_" in csv_file: table_name = csv_file.split("_")[0].upper()
        else: table_name = csv_file
        # return with extension
        return self._dbname + "." + table_name + table_ext


    # This function accepts a table name and a dictionary
    # with keys as column names and values as data.
    # It builds an sql query out of this array.
    def build_sql_insert_query(self, insert_data_array, args_array):

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        uspto_xml_format = args_array['uspto_xml_format']

        # Set a length counter used to find when the last item is appended to query string
        array_length_counter = 1
        length_of_array = len(insert_data_array) - 1
        # Pass the table name to variable
        table_name = insert_data_array['table_name']
        # Pop the table name off the array to be stored into database
        del insert_data_array['table_name']

        sql_query_string = "INSERT INTO " + table_name + " "
        sql_column_string = "("
        sql_value_string = " VALUES ("
        # Concatenate the list of keys and values to sql format
        for key, value in list(insert_data_array.items()):

            # Don't escape values that are None (NULL)
            if value is not None and isinstance(value, int) == False:
                # Escape all values for sql insertion
                value = USPTOSanitizer.escape_value_for_sql(str(value.encode('utf-8')))
                # Since postgresql uses `$` as delimiter, must  strip from first and last char
                value = value.strip("$").replace("$$$", "$").replace("$$", "$")

            # If the last item in the array then append line without comma at end
            if length_of_array == array_length_counter:
                sql_column_string += key
                # Check for None value and append
                if value == None:
                    sql_value_string += 'NULL'
                else:
                    # PostgreSQL strings will be escaped slightly different than MySQL
                    if args_array['database_type'] == 'postgresql':
                        sql_value_string += "$$" + str(value)+ "$$"
                    elif args_array['database_type'] == 'mysql':
                        sql_value_string += '"' + str(value) + '"'
            # If not the last item then append with comma
            else:
                sql_column_string += key + ", "
                # Check if value is None
                if value == None:
                    sql_value_string +=  'NULL,'
                else:
                    if args_array['database_type'] == 'postgresql':
                        sql_value_string +=  "$$" + str(value) + "$$,"
                    elif args_array['database_type'] == 'mysql':
                        sql_value_string += '"' + str(value) + '",'
            array_length_counter += 1
        # Add the closing bracket
        sql_column_string += ") "
        sql_value_string += ");"

        # Concatenate the pieces of the query
        sql_query_string += sql_column_string + sql_value_string
        logger.info(sql_query_string)
        # Return the query string
        return sql_query_string


    # Check if PARSER_VERIFICATION table exists and if not create it
    def checkParserVerificationTable(self, args_array):

        # Set the start time of operation
        start_time = time.time()

        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        print('[Checking for PARSER_VERIFICATION table in database. Time consuming:{0} Time Finished: {1}]'.format(time.time() - start_time, time.strftime("%c")))
        logger.info('[Checking for PARSER_VERIFICATION table in database. Time consuming:{0} Time Finished: {1}]'.format(time.time() - start_time, time.strftime("%c")))

        # List of all tables that should be verified
        table_name_array = [
            "GRANT",
            "INTCLASS_G",
            "CPCCLASS_G",
            "USCLASS_G",
            "INVENTOR_G",
            "AGENT_G",
            "ASSIGNEE_G",
            "APPLICANT_G",
            "NONPATCIT_G",
            "EXAMINER_G",
            "GRACIT_G",
            "FORPATCIT_G",
            "FOREIGNPRIORITY_G",
            "APPLICATION",
            "INTCLASS_A",
            "USCLASS_A",
            "CPCCLASS_A",
            "FOREIGNPRIORITY_A",
            "AGENT_A",
            "ASSIGNEE_A",
            "INVENTOR_A",
            "APPLICANT_A",
            "TRANSACTION_P",
            "ADJUSTMENT_P",
            "ADJUSTMENTDESC_P",
            "CORRESPONDENCE_P",
            "CONTINUITYCHILD_P",
            "CONTINUITYPARENT_P",
            "EXTENSION_P",
            "EXTENSIONDESC_P",
            "USCLASS_C",
            "CPCCLASS_C",
            "USCPC_C",
            "CASE_L",
            "PATENT_L",
            "ATTORNEY_L",
            "PARTY_L"
        ]

        try:
            # Set bool to track table found
            table_found = False

            # If using PostgreSQL
            if self.database_type == "postgresql":
                # Build query to get list of all tables in uspto database
                get_table_list_sql = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
                self._cursor.execute(get_table_list_sql)
                # Check the count is true or false.
                table_list = self._cursor.fetchall()
                # Print list of tables found
                if args_array['stdout_level'] == 1: pprint(table_list)
                # CHeck for PARSER_VERIFICATION table
                for item in table_list:
                    if item[1] == "PARSER_VERIFICATION": table_found = True
                # If the table is found then return
                if table_found: return True
                # If table not found then create table
                else:

                    print('- Creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                    logger.info('- Creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                    create_table_sql = """
                    CREATE TABLE IF NOT EXISTS """ + self._dbname + """.PARSER_VERIFICATION (
                      FileName VARCHAR(45) NOT NULL,
                      TableName VARCHAR(45) NOT NULL,
                      Count INT(11) NOT NULL,
                      Expected INT(11) DEFAULT NULL,
                      PRIMARY KEY (FileName, TableName));
                    """
                    self._cursor.execute(create_table_sql)

                    print('- Finished creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                    logger.info('- Finished creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                    # Populate the PARSER_VERIFICATION table with data for
                    # all other tables counted by source FileName
                    for table in table_name_array:

                        print('- Populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                        logger.info('- Populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                        populate_count_sql = """
                        INSERT INTO """ + self._dbname + """.PARSER_VERIFICATION
                        (FileName, TableName, Count)
                        SELECT FileName, '""" + table +  """', count(*)
                        FROM """ + self._dbname + """.""" + table + """
                        GROUP BY FileName;
                        """
                        if args_array['stdout_level'] == 1: print(populate_count_sql)
                        self._cursor.execute(populate_count_sql)
                        print('- Finished populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                        logger.info('- Finished populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

            # If using MySQL
            elif self.database_type == "mysql":
                # Build query to get list of all tables in uspto database
                get_table_list_sql = "SHOW TABLES"
                self._cursor.execute(get_table_list_sql)
                # Check the count is true or false.
                table_list = self._cursor.fetchall()
                # Print list of tables found
                if args_array['stdout_level'] == 1: pprint(table_list)
                # CHeck for PARSER_VERIFICATION table
                for item in table_list:
                    if item[0] == "PARSER_VERIFICATION": table_found = True
                # If the table is found then return
                if table_found: return True
                # If table not found then create table
                else:

                    print('- Creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                    logger.info('- Creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                    create_table_sql = """
                    CREATE TABLE IF NOT EXISTS """ + self._dbname + """.PARSER_VERIFICATION (
                      `FileName` VARCHAR(45) NOT NULL,
                      `TableName` VARCHAR(45) NOT NULL,
                      `Count` INT(11) NOT NULL,
                      `Expected` INT(11) DEFAULT NULL,
                      PRIMARY KEY (`FileName`, `TableName`));
                    """
                    self._cursor.execute(create_table_sql)

                    print('- Finished creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                    logger.info('- Finished creating PARSER_VERIFICATION table in uspto database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                    # Populate the PARSER_VERIFICATION table with data for
                    # all other tables counted by source FileName
                    for table in table_name_array:

                        print('- Populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                        logger.info('- Populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                        populate_count_sql = """
                        INSERT INTO """ + self._dbname + """.PARSER_VERIFICATION
                        (FileName, TableName, Count)
                        SELECT FileName, '""" + table +  """', count(*)
                        FROM """ + self._dbname + """.""" + table + """
                        GROUP BY FileName;
                        """
                        if args_array['stdout_level'] == 1: print(populate_count_sql)
                        self._cursor.execute(populate_count_sql)
                        print('- Finished populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                        logger.info('- Finished populating PARSER_VERIFICATION with ' + table + ' table counts in database. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

        except Exception as e:
            # If there is an error and using databse postgresql
            # Then rollback the commit??
            if self.database_type == "postgresql":
                self._conn.rollback()

            # Print and log general fail comment
            print("Database build of PARSER_VERIFICATION table list failed!")
            logger.error("Database build of PARSER_VERIFICATION table list failed!")
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())

        print('[Finished creating PARSER_VERIFICATION table in database. Time consuming:{0} Time Finished: {1}]'.format(time.time() - start_time, time.strftime("%c")))
        logger.info('[Finished creatingr PARSER_VERIFICATION table in database. Time consuming:{0} Time Finished: {1}]'.format(time.time() - start_time, time.strftime("%c")))


    # Stores the counts of XML tags counted in files
    def storeVerificationExtraction(self, counts_dict, args_array):

        # Set the start time of operation
        start_time = time.time()
        # Import logger
        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        # Extract the file_name from args_array
        file_name = args_array['file_name']
        # Remove the table name from the dict
        del counts_dict['file_name']

        # Loop through all key, values and insert exptected value
        # into PARSER_VERIFICATION for the table / filename combination
        for table_name, count in counts_dict.items():

            try:

                print('-- Inserting expected value for ' + table_name + ' into PARSER_VERIFICATION table.')
                logger.info('-- Inserting expected value for ' + table_name + ' into PARSER_VERIFICATION table.')

                # Check if a record exists for the file_name / table_name
                check_exists = """
                SELECT count(*) as count
                FROM """ + self._dbname + """.PARSER_VERIFICATION
                WHERE FileName = '""" + file_name + """'
                AND TableName = '""" + table_name + """';"""
                if args_array['stdout_level'] == 1: print(check_exists)
                self._cursor.execute(check_exists)
                result = self._cursor.fetchone()

                # Insert or update depending on result of count
                if result[0] == 0:

                    tag_count_sql = """
                    INSERT INTO """ + self._dbname + """.PARSER_VERIFICATION
                    (FileName, TableName, Count, Expected)
                    VALUES ('""" + file_name + """', '""" + table_name + """', 0, """ + str(count) + """);"""

                    if args_array['stdout_level'] == 1: print(tag_count_sql)
                    self._cursor.execute(tag_count_sql)

                else:

                    tag_count_sql = """
                    UPDATE """ + self._dbname + """.PARSER_VERIFICATION
                    SET expected = """ + str(count) +  """
                    WHERE FileName = '""" + file_name + """'
                    AND TableName = '""" + table_name + """';"""

                    if args_array['stdout_level'] == 1: print(tag_count_sql)
                    self._cursor.execute(tag_count_sql)

            except Exception as e:
                # If there is an error and using databse postgresql
                # Then rollback the commit??
                if self.database_type == "postgresql":
                    self._conn.rollback()

                # Print and log general fail comment
                print("-- Updating PARSER_VERIFICATION table list failed!")
                logger.error("-- Updating PARSER_VERIFICATION table list failed!")
                traceback.print_exc()
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
                # Return the failed state
                return False


        # Return the sucess message
        return True


    # Inserts additional CPC classes collected from Google BigQuery
    def insert_CPC_patched_item(grant_id, cpc_array):

        # Set the start time of operation
        start_time = time.time()
        # Import logger
        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        try:

            # Set the position
            position = 1

            # Loop through all CPC code dictionaries and insert to CPCCLASS_G
            for cpc_code in cpc_array:

                insert_CPC_sql = """
                INSERT INTO """ + self._dbname + """.CPCCLASS_G
                (GrantID, Position, Section, Class, SubClass, MainGroup, SubGroup, Malformed, FileName)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    grant_id,
                    position,
                    cpc_code['Section'],
                    cpc_code['Class'],
                    cpc_code['SubClass'],
                    cpc_code['MainGroup'],
                    cpc_code['SubGroup'],
                    0,
                    "big_query"
                )
                if args_array['stdout_level'] == 1: print(insert_CPC_sql)
                self._cursor.execute(insert_CPC_sql, values)
                print('-- Finished inserting ' + publication_number + ' into CPCCLASS_G table. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                logger.info('-- Finished inserting ' + publication_number + ' into CPCCLASS_G table. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                # Increment position for next item
                position += 1

        except Exception as e:
            # If there is an error and using databse postgresql
            # Then rollback the commit??
            if self.database_type == "postgresql":
                self._conn.rollback()

            # Print and log general fail comment
            print("-- Inserting 2005 grant CPC data into CPCCLASS_G table list failed!")
            logger.error("-- Inserting 2005 grant CPC data into CPCCLASS_G table list failed!")
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
            # Return the failed state
            return False

    # Inserts additional IPC classes collected from Google BigQuery
    def insert_IPC_patched_item(grant_id, ipc_array):

        # Set the start time of operation
        start_time = time.time()
        # Import logger
        logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

        try:

            # Set the position
            position = 1

            # Loop through all IPC code dictionaries and insert to IPCCLASS_G
            for cpc_code in cpc_array:

                insert_IPC_sql = """
                INSERT INTO """ + self._dbname + """.INTCLASS_G
                (GrantID, Position, Section, Class, SubClass, MainGroup, SubGroup, Malformed, FileName)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    grant_id,
                    position,
                    cpc_code['Section'],
                    cpc_code['Class'],
                    cpc_code['SubClass'],
                    cpc_code['MainGroup'],
                    cpc_code['SubGroup'],
                    0,
                    "big_query"
                )
                if args_array['stdout_level'] == 1: print(insert_IPC_sql)
                self._cursor.execute(insert_IPC_sql, values)
                print('-- Finished inserting ' + publication_number + ' into IPCCLASS_G table. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))
                logger.info('-- Finished inserting ' + publication_number + ' into IPCCLASS_G table. Time consuming:{0} Time Finished: {1}'.format(time.time() - start_time, time.strftime("%c")))

                # Increment position for next item
                position += 1

        except Exception as e:
            # If there is an error and using databse postgresql
            # Then rollback the commit??
            if self.database_type == "postgresql":
                self._conn.rollback()

            # Print and log general fail comment
            print("-- Inserting 2005 grant IPC data into IPCCLASS_G table list failed!")
            logger.error("-- Inserting 2005 grant IPC data into IPCCLASS_G table list failed!")
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
            # Return the failed state
            return False
