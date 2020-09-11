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
ORDER BY count(*) DESC

--
-- Delete duplicates
--
DELETE uspto.GRANT
FROM uspto.GRANT
INNER JOIN (
SELECT MAX(FileName) AS lastId, GrantID
FROM uspto.GRANT
GROUP BY GrantID
HAVING count(*) > 1) duplic ON duplic.GrantID = uspto.GRANT.GrantID
WHERE uspto.GRANT.FileName < duplic.lastId;
