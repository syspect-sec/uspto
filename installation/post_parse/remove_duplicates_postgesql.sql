--
-- Remove Duplciates From Database
--
-- Author: Joseph Lee
-- Company: Ripple Software
-- Email: joseph@ripplesoftware.ca
-- Website: https://www.ripplesoftware.ca
-- Github: https://github.com/rippledj/uspto
--

--
-- Check for duplicate GrantID
--
SELECT GrantID, count(*) as count
FROM uspto.GRANT AS a
GROUP BY a.GrantID
HAVING count(*) > 1
ORDER BY count(*) DESC;

--
-- Delete GrantID duplicates
--
DELETE
FROM uspto.GRANT AS a
USING uspto.GRANT as b
WHERE a.FileName < b.FileName
AND a.GrantID = b.GrantID;


--
-- Also need to expunge duplicate records from other tables with same source file and grantid
--
