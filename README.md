# **USPTO PATENT DATA PARSER**

Copyright (c) 2020 Ripple Software. All rights reserved.

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA

**Author:** Joseph Lee

**Email:** joseph@ripplesoftware.ca

**Website:** https://www.ripplesoftware.ca

**Github Repository:** https://github.com/rippledj/uspto

## **Description:**
This python script is based on a project from University of Illinois (http://abel.lis.illinois.edu/UPDC/Downloads.html). Several parts of the script have been improved to increase the data integrity and performance of the original script.  The script requires Python 3.6 or higher and will not work properly with Python 2.7

The script is run from the command line and will populate a PostgreSQL or MySQL database with the USPTO patent grant and patent application red-book bulk-data.
It is recommended to use PostgreSQL since PG provides better performance over the large data-set.

The usage of the script is outlined below:

## **Instructions:**
There are three steps.
1. Install the required database
2. Run the parser USPTOparser.py
3. Schedule the updater

### 1. Install the database

Run the appropriate database creation scripts depending if you intend to store the USPTO data in MySQL or PostgreSQL.  The script will create a user  'uspto' and limit the scope of the user to the uspto database. If you want to change the default password for the user, edit the appropriate .sql file before running it.  Also, some configuration of your database maybe necessary depending on the settings choose when running the script.  For example the ability to bulk insert CSV files are disabled by default in MySQL.

_MySQL_

installation/uspto_create_database_mysql.sql

_PostgreSQL_

installation/uspto_create_database_postgresql.sql

### 2. Run the parser

Before the USPTOParser.py can run successfully, the database connection and authentication details must be added (if database storage will be specified). Text search for the phrase "# Database args" to find the location where database credentials must be changed. Enter "mysql" or "postgresql" as the database_type. Enter the port of your MySQL or PostgreSQL installation if you have a non-default port. If you changed the default password in the database creation file, then you should also change the password here.

The default setting is to parse USPTO 'Red Book' bibliographic data which results in a database size of about ~70GB.  If you want instead to collect full-text, you must pass the argument '-full' when you run USPTOParser.py.  The full-text database size is ~2TB.

Also, you must specify the location for the data to be stored.  These options are: '-csv' and '-database'.  You must include at least one. These arguments tell the script where you want the data to be stored. You should set the 'database_insert_mode' to specify whether you want the data to be inserted into the database after each data object is found and parsed ('each'), or in bulk post parsing of each file ('bulk').  'bulk' setting greatly improves database performance and reduces the total time to complete the bulk insertion.

Finally, you can set the number of threads with a command line argument '-t [int]' where [int] is a number between 1 and 20.  If you do not specify the number of threads, then the default number of threads will be used, which is 5.  Using the '-balance' argument will turn on the load balancer which will limit the threads CPU usage.  However, if you do not use the '-balance' flag, your computer may crash if your CPU load is too high.

The following example is the command to store in csv file and database with 10 process threads.

$ python USPTOParser.py -csv -database -t 10

The following example is the command to store full-text data in csv file and database with 20 balanced process threads

$ python USPTOParser.py -csv -database -t 20 -full -balance

Finally, the script can be run in 'sandbox mode' or normal mode by setting a flag in the args_array called 'sandbox' which is at the top of the main function.  Running the script in sandbox mode will keep all downloaded .zip files and extracted .xml or .dat files on your computer so that they do not need to be downloaded again if you restart the script or encounter any errors, or so that you may inspect the decompressed data files.

### 3. Check the log files

The script will keep track of processed files in the **LOG** directory. There are log files for grants (**grant_links.log**) and applications (**application_links.log**), and a main log file **USPTO_app.log** which keeps track of errors and warnings from the script.  If the script crashes for any reason, you can simply start the script again and it will clear any partially processed data and start where it left off.  You can set the verbosity of the stdout and **USPTO_app.log** logs with the 'log_level' and 'stdout_level' variables at the top of the main function.

You should check of the **grant_links.log** and **application_links.log** files after the script has completed to make sure that each line in those files says "Processed" at the end.  If the file has not been processed, the line will end with "Unprocessed" and you should run the script again to finish any files that were not processed.

### 4. Schedule the updater

The script will also run in update mode to get all new patent grants and applications which are issued each week by the USPTO. This is done by passing the '-update' argument when running the script as the command below.

$ python USPTOParser.py -update

The script will check your previous data destination(s) settings and get any new patent data release files that have been published on the USPTO website (https://bulkdata.uspto.gov/).  The new files are then parsed and stored in the destinations you previously specified.  Since database data files are released every week, the updater can be scheduled once a week to keep your database up-to-date.

## **Further Information:**

### CPU Load balancing

The script uses a load balancer which detects the number of CPU cores and creates and sleeps threads to maintain a constant CPU load.  The default value is 75%. Therefore, if the 10 minute CPU load is less than 75%, another thread is added.  If the CPU load exceeds 75%, threads are forced to sleep.  These settings can be adjusted in the script.

### Bulk Database Insertion Performance

The method used to insert data into the database can be configured in two ways.  The script can insert each document record immediately after it is parsed or in bulk after a file is finished being parsed.  Using bulk storage utilizes .csv files to temporarily store the data before it is inserted in bulk.  If the '-database' flag is set but the '-csv' is not set, then the .csv. files are erased after being used to load the data.  

### USTPTO Contact

If you have questions about the USPTO patent data you can contact:
Author, Joseph Lee: joseph@ripplesoftware.ca
USPTO: EconomicsData@uspto.gov
