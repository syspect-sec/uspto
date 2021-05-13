--
-- Data Summary of the USPTOParser Database
--
-- Author: Joseph Lee
-- Company: Ripple Software
-- Email: joseph@ripplesoftware.ca
-- Website: https://www.ripplesoftware.ca
-- Github: https://github.com/rippledj/uspto
--
-- This file creates a tables and populates them with
-- the expected number of grants and applications published
-- by the USPTO website: https://www.uspto.gov/web/offices/ac/ido/oeip/taf/us_stat.htm
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

-- -----------------------------------------------------
-- Table uspto.APPLICATION_SUMMARY
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto.APPLICATION_SUMMARY (
  `count` INT NOT NULL,
  `year` INT NOT NULL,
  PRIMARY KEY (year));

--
-- Populate the APPLICATION_SUMMARY table with values from USPTO website
-- Source: https://www.uspto.gov/web/offices/ac/ido/oeip/taf/us_stat.htm
--

INSERT INTO uspto.APPLICATION_SUMMARY (`count`, `year`)
VALUES
("669434","2019"),
("643303","2018"),
("651355","2017"),
("649319","2016"),
("629647","2015"),
("615243","2014"),
("609052","2013"),
("576763","2012"),
("535188","2011"),
("520277","2010"),
("482871","2009"),
("485312","2008"),
("484955","2007"),
("452633","2006"),
("417508","2005"),
("382139","2004"),
("366043","2003"),
("356493","2002"),
("345732","2001"),
("315015","2000"),
("288811","1999"),
("260889","1998"),
("232424","1997"),
("211013","1996"),
("228238","1995"),
("206090","1994"),
("188739","1993"),
("186507","1992"),
("177830","1991"),
("176264","1990"),
("165748","1989"),
("151491","1988"),
("139455","1987"),
("132665","1986"),
("126788","1985"),
("120276","1984"),
("112040","1983"),
("117987","1982"),
("113966","1981"),
("112379","1980"),
("108209","1979"),
("108648","1978"),
("108377","1977"),
("109580","1976"),
("107456","1975"),
("108011","1974"),
("109622","1973"),
("105300","1972"),
("111095","1971"),
("109359","1970"),
("104357","1969"),
("98737","1968"),
("90544","1967"),
("93482","1966"),
("100150","1965"),
("92971","1964"),
("90982","1963");

--
-- Calculate the difference between the USPTO Patent Summary Chart and
-- values parsed into the main database.
--

SELECT *
FROM (
SELECT
	"GRANT" AS `Type`,
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
ORDER BY YEAR(a.IssueDate) DESC
) AS t1
UNION
SELECT *
FROM (
SELECT
	"APPLICATION" AS `Type`,
	YEAR(a.FileDate) AS `Year`,
	b.Count AS `Official Total`,
	count(*) AS `Database Total`,
	count(*) - b.Count AS `Difference`,
	100 - ABS(ROUND(count(*) / b.Count * 100, 2) - 100) AS `Accuracy %`
FROM uspto.APPLICATION AS a
JOIN uspto.APPLICATION_SUMMARY AS b ON
YEAR(a.FileDate) = b.Year
WHERE YEAR(a.FileDate) IS NOT NULL
GROUP BY YEAR(a.FileDate)
ORDER BY YEAR(a.FileDate) DESC
) AS t2;
