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
-- Delete duplicate GrantID
--
DELETE
FROM uspto.GRANT AS a
USING uspto.GRANT AS b
WHERE a.FileName < b.Filename
AND a.GrantID = a.GrantID;
