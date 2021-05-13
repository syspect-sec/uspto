--
-- Parser verification of the USPTOParser Database
--
-- Author: Joseph Lee
-- Company: Ripple Software
-- Email: joseph@ripplesoftware.ca
-- Website: https://www.ripplesoftware.ca
-- Github: https://github.com/rippledj/uspto
--
-- This file will output the number of records in
-- the database against the expected number that
-- should be found based on tags found in the
-- original USPTO bulk-data file.
-- This script can only be run after the
-- PARSER_VERIFICATION table has been created using
-- the create_parser_verification_mysql.sql or
-- create_parser_verification_postgresql.sql
-- files and then running `python USPTOParser.py -verify`
--

SELECT *, Count/Expected*100 as Pct
FROM PARSER_VERIFICATION
WHERE FileName = 'ipgb20200107_wk01'
UNION
SELECT *, Count/Expected*100 as Pct
FROM PARSER_VERIFICATION
WHERE FileName = 'ipgb20200114_wk02'
UNION
SELECT *, Count/Expected*100 as Pct
FROM PARSER_VERIFICATION
WHERE FileName = 'ipgb20200107_wk01'
UNION
SELECT *, Count/Expected*100 as Pct
FROM PARSER_VERIFICATION
WHERE FileName = 'ipab20200109_wk02';
