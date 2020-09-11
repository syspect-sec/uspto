--
-- Data Summary of the USPTOParser Database
--
-- Author: Joseph Lee
-- Company: Ripple Software
-- Email: joseph@ripplesoftware.ca
-- Website: https://www.ripplesoftware.ca
-- Github: https://github.com/rippledj/uspto
--

-- -----------------------------------------------------
-- Table uspto.GRANT_SUMMARY
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto.GRANT_SUMMARY (
  `count` INT NOT NULL,
  `year` INT NOT NULL,
  PRIMARY KEY (year));

--
-- Populate the GRANT_SUMMARY table with values from USPTO website
-- Source: https://www.uspto.gov/web/offices/ac/ido/oeip/taf/us_stat.htm
--
INSERT INTO uspto.GRANT_SUMMARY (`count`, `year`)
VALUES
("391103","2019"),
("339992","2018"),
("351403","2017"),
("333583","2016"),
("325980","2015"),
("326032","2014"),
("302948","2013"),
("276788","2012"),
("247713","2011"),
("244341","2010"),
("191927","2009"),
("185224","2008"),
("182899","2007"),
("196405","2006"),
("157718","2005"),
("181299","2004"),
("187012","2003"),
("184375","2002"),
("183970","2001"),
("175979","2000"),
("169085","1999"),
("163142","1998"),
("124069","1997"),
("121696","1996"),
("113834","1995"),
("113587","1994"),
("109746","1993"),
("107394","1992"),
("106696","1991"),
("99077","1990"),
("102533","1989"),
("84272","1988"),
("89385","1987"),
("76862","1986"),
("77245","1985"),
("72650","1984"),
("61982","1983"),
("63276","1982"),
("71064","1981"),
("66170","1980"),
("52413","1979"),
("70514","1978"),
("69781","1977"),
("75388","1976"),
("76810","1975"),
("81278","1974"),
("78622","1973"),
("78185","1972"),
("81790","1971"),
("67964","1970"),
("71230","1969"),
("62714","1968"),
("69098","1967"),
("71886","1966"),
("66647","1965"),
("50389","1964"),
("48971","1963");

--
-- Calculate the difference between the USPTO Patent Summary Chart and
-- values parsed into the main database.
--
SELECT
	YEAR(a.IssueDate) AS `Year`,
	b.Count AS `Official Total`,
	count(*) AS `Database Total`,
	count(*) - b.Count AS `Difference`,
	100 - ABS(ROUND(count(*) / b.Count * 100, 2) - 100) AS `Accuracy %`
FROM uspto.GRANT AS a
JOIN uspto.GRANT_SUMMARY AS b ON
YEAR(a.IssueDate) = b.Year
WHERE YEAR(a.IssueDate) IS NOT NULL
GROUP BY YEAR(a.IssueDate)
ORDER BY YEAR(a.IssueDate) DESC;
