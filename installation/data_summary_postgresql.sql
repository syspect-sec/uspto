--
-- Data Summary of the USPTOParser Database
--
-- Author: Joseph Lee
-- Company: Ripple Software
-- Email: joseph@ripplesoftware.ca
-- Website: https://www.ripplesoftware.ca
-- Github: https://github.com/rippledj/uspto
--
SELECT
	YEAR(a.IssueDate) as Year,
	b.Count as 'Official Total',
	count(*) as 'Database Total',
	count(*) - b.Count as 'Difference',
	100 - ABS(ROUND(count(*) / b.Count * 100, 2) - 100) as 'Accuracy %'
FROM uspto.GRANT as a
JOIN uspto.GRANT_SUMMARY as b ON
YEAR(a.IssueDate) = b.Year
WHERE YEAR(a.IssueDate) is not NULL
GROUP BY YEAR(a.IssueDate)
ORDER BY YEAR(a.IssueDate) DESC;
