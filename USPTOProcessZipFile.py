# USPTOProcessZipFile.py
# USPTO Bulk Data Parser - Processes ZIP Files
# Description: Imported to Process Modules.  Extracts XML file contents from a downloaded ZIP file.
# Author: Joseph Lee
# Email: joseph@ripplesoftware.ca
# Website: www.ripplesoftware.ca
# Github: www.github.com/rippledj/uspto

# ImportPython Modules
import time
import os
import sys
import traceback
import subprocess
import shutil
import zipfile
import urllib.request, urllib.parse, urllib.error
import codecs

# Import USPTO Parser Functions
import USPTOLogger

# Extract a zip file and return the contents of the XML file as an array of lines
def extract_xml_file_from_zip(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the zipfile to read it
    try:
        zip_file = zipfile.ZipFile(args_array['temp_zip_file_name'], 'r')
        # Find the xml file from the extracted filenames
        for filename in zip_file.namelist():
            if '.xml' in filename or '.sgml' in filename:
                xml_file_name = filename
        # Print stdout message that xml file was found
        print('[xml file found. Filename: {0}]'.format(xml_file_name))
        logger.info('xml file found. Filename: ' + xml_file_name)
        # Open the file to read lines out of
        xml_file = zip_file.open(xml_file_name, 'r')
        # If sandbox mode then extract the xml file
        if args_array['sandbox'] == True:
            zip_file.extract(xml_file_name, args_array['temp_directory'] + "/unzip/" + args_array['file_name'])
        # Extract the contents from the file
        xml_file_contents = xml_file.readlines()
        # Close the file being read from
        zip_file.close()
        # If not sandbox mode, then delete the .zip file
        if args_array['sandbox'] == False and os.path.exists(args_array['temp_zip_file_name']):
            # Print message to stdout
            print('[Purging .zip file ' + args_array['temp_zip_file_name'] + '...]')
            logger.info('Purging .zip file ' + args_array['temp_zip_file_name'] + '...')
            os.remove(args_array['temp_zip_file_name'])

        print('[xml file contents extracted ' + xml_file_name + '...]')
        logger.info('xml file contents extracted ' + xml_file_name + '...')
        # Return the file contents as array
        return xml_file_contents

    # The zip file has failed using python's ZipFile
    except:
        print('[Zip file ' + args_array['temp_zip_file_name'] + ' failed to unzip with Python module...]')
        logger.warning('Zip file ' + args_array['temp_zip_file_name'] + ' failed to unzip with Python module')
        traceback.print_exc()

        # Attempt to download the file again
        try:
            # Print message to stdout
            print('[Removing corrupted zip file ' + args_array['temp_zip_file_name'] + ']')
            logger.warning('Removing corrupted file ' + args_array['temp_zip_file_name'])
            # Remove the corrupted zip file
            delete_zip_file(args_array['temp_zip_file_name'])
            # Return None to signal failed status
            return None
        except:
            print('[Failed to remove zip file ' + args_array['temp_zip_file_name'] + ' ]')
            logger.warning('Failed to remove zip file ' + args_array['temp_zip_file_name'])
            traceback.print_exc()
            # Return False to signify that zip file could not be deleted
            return False

    # Finally, if nothing was returned already, return None
    finally:
        pass
        #TODO: need to remove the zip file here if



# Extract a zip file and return the contents of the CSV file as an array of lines
def extract_csv_file_from_zip(args_array):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the zipfile to read it
    try:
        zip_file = zipfile.ZipFile(args_array['temp_zip_file_name'], 'r')
        # Find the csv file from the extracted filenames
        for filename in zip_file.namelist():
            if '.csv' in filename:
                csv_file_name = filename
        # Print stdout message that csv file was found
        print('[csv file found. Filename: {0}]'.format(csv_file_name))
        logger.info('csv file found. Filename: ' + csv_file_name)
        # If extract the csv file
        extracted_csv_filepath = args_array['temp_directory'] + "/unzip/"
        zip_file.extract(csv_file_name, extracted_csv_filepath)
        # Close the zip file being read from
        zip_file.close()

        # Return the file contents as array
        return extracted_csv_filepath + csv_file_name

    # The zip file has failed using python's ZipFile
    except:
        print('[Zip file ' + args_array['temp_zip_file_name'] + ' failed to unzip with Python module...]')
        logger.warning('Zip file ' + args_array['temp_zip_file_name'] + ' failed to unzip with Python module')
        traceback.print_exc()

        # Attempt to download the file again
        try:
            # Print message to stdout
            print('[Removing corrupted zip file ' + args_array['temp_zip_file_name'] + ']')
            logger.warning('Removing corrupted file ' + args_array['temp_zip_file_name'])
            # Remove the corrupted zip file
            delete_zip_file(args_array['temp_zip_file_name'])
            # Return None to signal failed status
            return None
        except:
            print('[Failed to remove zip file ' + args_array['temp_zip_file_name'] + ' ]')
            logger.warning('Failed to remove zip file ' + args_array['temp_zip_file_name'])
            traceback.print_exc()
            # Return False to signify that zip file could not be deleted
            return False

    # Finally, if nothing was returned already, return None
    finally:
        pass

# Extract a zip file and return the contents of the XML file as an array of lines
def extract_dat_file_from_zip(args_array, indexed=False):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Extract the zipfile to read it
    try:
        zip_file = zipfile.ZipFile(args_array['temp_zip_file_name'], 'r')
        data_file_name = ""
        for name in zip_file.namelist():
            if '.dat' in name or '.txt' in name:
                data_file_name = name
                # Print and log that the .dat file was not found
                print('[APS .dat data file found. Filename: {0}]'.format(data_file_name))
                logger.info('APS .dat file found. Filename: ' + data_file_name)
        # If .dat file not found, then print error message
        if data_file_name == "":
            # Print and log that the .dat file was not found
            logger.error('APS .dat file not found. Filename: ' + args_array['url_link'])

        # Check if an unzip directory exists in the temp directory
        if not os.path.exists(args_array['temp_directory'] + "/unzip"):
            os.mkdir(args_array['temp_directory'] + "/unzip")
        # Check if a directory exists for the specific file being unzipped
        if not os.path.exists(args_array['temp_directory'] + "/unzip/" + args_array['file_name']):
            # Make a directory for the particular downloaded zip file
            os.mkdir(args_array['temp_directory'] + "/unzip/" + args_array['file_name'])

        # Open the zip file and extract the .dat file contents
        zip_file.extract(data_file_name, args_array['temp_directory'] + "/unzip/" + args_array['file_name'])
        # Close the zip file
        zip_file.close()
        # Create a temp file name for the extracted .dat file
        temp_data_file_path = args_array['temp_directory'] + "/unzip/" + args_array['file_name'] + "/" + data_file_name

        # Open the .dat file contents from the extracted zip_file
        data_file_contents = codecs.open(temp_data_file_path, 'r', 'iso-8859-1')

        # If a flag is set for an indexable file object
        # then parse into a list
        if indexed:
            indexed_list = []
            for item in data_file_contents:
                indexed_list.append(item)
            data_file_contents = indexed_list

        # Delete the extracted data file
        if not args_array['sandbox']:
            os.remove(temp_data_file_path)

        # If not sandbox mode, then delete the .zip file
        if args_array['sandbox'] == False and os.path.exists(args_array['temp_zip_file_name']):
            # Print message to stdout
            print('[Purging .zip file ' + args_array['temp_zip_file_name'] + '...]')
            logger.info('Purging .zip file ' + args_array['temp_zip_file_name'] + '...')
            os.remove(args_array['temp_zip_file_name'])

        # Print message to stdout
        print('[APS .dat data file contents extracted ' + data_file_name + '...]')
        logger.info('APS .dat data file contents extracted ' + data_file_name + '...')

        # Return the file contents as array
        return data_file_contents

    # Since zip file could not unzip, remove it
    except:
        # Print exception information to file
        traceback.print_exc()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
        # Remove the zip file and return error code
        try:
            # Print message to stdout
            print('[Removing corrupted zip file ' + args_array['temp_zip_file_name'] + ']')
            logger.warning('Removing corrupted file ' + args_array['temp_zip_file_name'])
            # Remove the corrupted zip file
            delete_zip_file(args_array['temp_zip_file_name'])
            # Return None to signal failed status
            return None
        except:
            # Print exception information to file
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("Exception: " + str(exc_type) + " in Filename: " + str(fname) + " on Line: " + str(exc_tb.tb_lineno) + " Traceback: " + traceback.format_exc())
            # Print message to stdout
            print('[Failed to remove zip file ' + args_array['temp_zip_file_name'] + ' ]')
            logger.error('Failed to remove zip file ' + args_array['temp_zip_file_name'])
            # Return False to signify that zip file could not be deleted
            return False

# Deletes a zip file
def delete_zip_file(filename):

    logger = USPTOLogger.logging.getLogger("USPTO_Database_Construction")

    # Check that a zip file
    if ".zip" in filename:
        # Remove the file
        os.remove(filename)
        print("[.Zip file " + filename + " has been removed...]")
        logger.warning(".Zip file " + filename + " has been removed...")
