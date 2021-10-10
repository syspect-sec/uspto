--
-- Calculate Basic Metrics Tables
--
-- Author: Joseph Lee
-- Company: Ripple Software
-- Email: joseph@ripplesoftware.ca
-- Website: https://www.ripplesoftware.ca
-- Github: https://github.com/rippledj/uspto
--

-- -----------------------------------------------------
-- Table uspto.METRICS_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto.METRICS_G (
  GrantID VARCHAR(20) NOT NULL,
  ForwardCitCnt INT DEFAULT NULL,
  BackwardCitCnt INT DEFAULT NULL,
  TCT DOUBLE PRECISION DEFAULT NULL,
  TCT_M DOUBLE PRECISION DEFAULT NULL,
  FamilySize INT DEFAULT NULL,
  TCTRank INT DEFAULT NULL,
  TCT_MRank INT DEFAULT NULL,
  BWCitCntRank INT DEFAULT NULL,
  FWCitCntRank INT DEFAULT NULL,
  ClaimsNumRanks INT DEFAULT NULL,
  DrawingsNumRanks INT DEFAULT NULL,
  FiguresNumRanks INT DEFAULT NULL,
  PRIMARY KEY (GrantID));

-- -----------------------------------------------------
-- Table uspto.METRICS_C
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto.METRICS_C (
  Schema VARCHAR(5) NOT NULL,
  Section VARCHAR(15) NOT NULL,
  Class VARCHAR(15) NOT NULL,
  SubClass VARCHAR(15) NOT NULL,
  MainGroup VARCHAR(15) DEFAULT NULL,
  SubGroup VARCHAR(15) DEFAULT NULL,
  Size INT DEFAULT NULL,
  AvgBwdCit DOUBLE PRECISION DEFAULT NULL,
  AvgFwdCit DOUBLE PRECISION DEFAULT NULL,
  AvgTCT DOUBLE PRECISION DEFAULT NULL,
  AvgTCT_M DOUBLE PRECISION DEFAULT NULL,
  AvgFamilySize DOUBLE PRECISION DEFAULT NULL,
  AvgClaims DOUBLE PRECISION DEFAULT NULL,
  AvgDrawings DOUBLE PRECISION DEFAULT NULL,
  AvgFigures DOUBLE PRECISION DEFAULT NULL,
  PRIMARY KEY (Schema, Section, Class, SubClass, MainGroup));

--
-- Create metrics Record for all GrantID
--
INSERT INTO uspto.METRICS_G (GrantID) SELECT GrantID FROM uspto.GRANT;

--
-- Calculate Forward Citations for all GrantID
--
UPDATE uspto.METRICS_G AS a
SET ForwardCitCnt = t2.count
FROM (
  SELECT CitedID, count(*) count
  FROM uspto.GRACIT_G
  GROUP BY CitedID
) AS t2
WHERE a.GrantID = t2.CitedID;

--
-- Set all patents without FWD citations to 0
--
UPDATE uspto.METRICS_G
SET ForwardCitCnt = 0
WHERE ForwardCitCnt IS NULL;

--
-- Calculate Backward Citations for all GrantID
--
UPDATE uspto.METRICS_G AS a
SET BackwardCitCnt = t2.count
FROM (
  SELECT GrantID, count(*) AS count
  FROM uspto.GRACIT_G
  GROUP BY GrantID
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Set all patents without BWD citations to 0
--
UPDATE uspto.METRICS_G
SET BackwardCitCnt = 0
WHERE BackwardCitCnt IS NULL;

--
-- Calculate TCT for all GrantID
--
UPDATE uspto.METRICS_G AS a
SET TCT = t2.tct
FROM (
  SELECT a.grantid, AVG(date_part('year', b.issuedate) -  date_part('year', a.date)) AS tct
  FROM uspto.GRACIT_G AS a
  LEFT JOIN uspto.grant AS b ON
  a.grantid=b.grantid
  GROUP BY a.grantid
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate TCT_M for all GrantID
-- ** TCT_M is the TCT in months rather than years
--
UPDATE uspto.METRICS_G AS a
SET TCT_M = t2.tct_m
FROM (
  SELECT a.grantid, AVG(EXTRACT(YEAR FROM AGE(b.issuedate,a.date)) * 12 + EXTRACT(MONTH FROM AGE(b.issuedate, a.date)) ) AS tct_m
  FROM uspto.GRACIT_G AS a
  LEFT JOIN uspto.grant AS b ON
  a.grantid=b.grantid
  GROUP BY a.grantid
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate FamilySize for all GrantID
--

--
-- Calculate Number of Claims Rank by CPC Main Group
--
UPDATE uspto.METRICS_G AS a
SET ClaimsNumRank = t2.claimsnum_rank
FROM (
  SELECT a.grantid,
	NTILE(100) OVER (
		PARTITION BY b.section, b.class, b.subclass, b.maingroup
		ORDER BY a.claimsnum DESC
	) claimsnum_rank
  FROM uspto.grant AS a
  LEFT JOIN uspto.cpcclass_g AS b ON
  a.grantid=b.grantid
  WHERE b.position=1 and a.claimsnum IS NOT NULL
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate Number of Drawings Rank by CPC Main Group
--
UPDATE uspto.METRICS_G AS a
SET DrawingsNumRank = t2.drawingsnum_rank
FROM (
  SELECT a.grantid,
	NTILE(100) OVER (
		PARTITION BY b.section, b.class, b.subclass, b.maingroup
		ORDER BY a.drawingsnum DESC
	) drawingsnum_rank
  FROM uspto.grant AS a
  LEFT JOIN uspto.cpcclass_g AS b ON
  a.grantid=b.grantid
  WHERE b.position=1 and a.drawingsnum IS NOT NULL
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate Number of Figures Rank by CPC Main Group
--
UPDATE uspto.METRICS_G AS a
SET FiguresNumRank = t2.figuresnum_rank
FROM (
  SELECT a.grantid,
	NTILE(100) OVER (
		PARTITION BY b.section, b.class, b.subclass, b.maingroup
		ORDER BY a.figuresnum DESC
	) figuresnum_rank
  FROM uspto.grant AS a
  LEFT JOIN uspto.cpcclass_g AS b ON
  a.grantid=b.grantid
  WHERE b.position=1 and a.figuresnum IS NOT NULL
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate TCT Rank by CPC Main Group
--
UPDATE uspto.METRICS_G AS a
SET TCTRank = t2.tct_rank
FROM (
  SELECT a.grantid,
	NTILE(100) OVER (
		PARTITION BY b.section, b.class, b.subclass, b.maingroup
		ORDER BY a.tct ASC
	) tct_rank
  FROM uspto.metrics_g AS a
  LEFT JOIN uspto.cpcclass_g AS b ON
  a.grantid=b.grantid
  WHERE b.position=1 and a.tct IS NOT NULL
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate TCT_M Rank By CPC Main Group
--
UPDATE uspto.METRICS_G AS a
SET TCT_MRank = t2.tct_m_rank
FROM (
  SELECT a.grantid,
	NTILE(100) OVER (
		PARTITION BY b.section, b.class, b.subclass, b.maingroup
		ORDER BY a.tct_m ASC
	) tct_m_rank
  FROM uspto.metrics_g AS a
  LEFT JOIN uspto.cpcclass_g AS b ON
  a.grantid=b.grantid
  WHERE b.position=1 and a.tct_m IS NOT NULL
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate BW Citation Count Rank By CPC Main Group
--
UPDATE uspto.METRICS_G AS a
SET BWCitCntRank = t2.bw_cit_rank
FROM (
  SELECT a.grantid,
	NTILE(100) OVER (
		PARTITION BY b.section, b.class, b.subclass, b.maingroup
		ORDER BY a.backwardcitcnt DESC
	) bw_cit_rank
  FROM uspto.metrics_g AS a
  LEFT JOIN uspto.cpcclass_g AS b ON
  a.grantid=b.grantid
  WHERE b.position=1 and a.backwardcitcnt IS NOT NULL
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Calculate FW Citation Count Rank By CPC Main Group
--
UPDATE uspto.METRICS_G AS a
SET FWCitCntRank = t2.fw_cit_rank
FROM (
  SELECT a.grantid,
	NTILE(100) OVER (
		PARTITION BY b.section, b.class, b.subclass, b.maingroup
		ORDER BY a.forwardcitcnt DESC
	) fw_cit_rank
  FROM uspto.metrics_g AS a
  LEFT JOIN uspto.cpcclass_g AS b ON
  a.grantid=b.grantid
  WHERE b.position=1 and a.forwardcitcnt IS NOT NULL
) AS t2
WHERE a.GrantID = t2.GrantID;

--
-- Create Metrics Record for Each CPC Class Combination
--
-- ** This includes each patent in all its assigned classes
INSERT INTO uspto.METRICS_C
(schema, section, class, subclass, maingroup, subgroup, size)
SELECT 'CPC' as schema, section, class, subclass, maingroup, NULL as subgroup, COUNT(*)
FROM uspto.cpcclass_g
GROUP BY schema, section, class, subclass, maingroup
UNION
SELECT 'INT' as schema, section, class, subclass, maingroup, NULL as subgroup, COUNT(*)
FROM uspto.intclass_g
GROUP BY schema, section, class, subclass, maingroup;


-- Calculate other metrics for all CPC Classes
-- ** This includes each patent in all its assigned classes
UPDATE uspto.METRICS_C AS m
SET
avgbwdcit = t2.avgbwdcit,
avgfwdcit = t2.avgfwdcit,
avgtct = t2.avgtct,
avgtct_m = t2.avgtct_m,
avgclaims = t2.avgclaims,
avgdrawings = t2.avgdrawings,
avgfigures = t2.avgfigures
FROM (
  SELECT
  a.section, a.class, a.subclass, a.maingroup,
  AVG(b.backwardcitcnt) AS avgbwdcit,
  AVG(b.forwardcitcnt) AS avgfwdcit,
  AVG(b.tct) AS avgtct,
  AVG(b.tct_m) AS avgtct_m,
  AVG(c.claimsnum) AS avgclaims,
  AVG(c.drawingsnum) AS avgdrawings,
  AVG(c.figuresnum) AS avgfigures
  FROM uspto.cpcclass_g AS a
  LEFT JOIN uspto.metrics_g AS b ON
  a.grantid=b.grantid
  LEFT JOIN uspto.grant AS c ON
  a.grantid=c.grantid
  WHERE a.maingroup IS NOT NULL AND a.subgroup IS NOT NULL
  GROUP BY a.section, a.class, a.subclass, a.maingroup
) AS t2
WHERE
m.schema = 'CPC'
AND m.section = t2.section
AND m.class = t2.class
AND m.subclass = t2.subclass
AND m.maingroup = t2.maingroup;

--
-- Calculate other metrics for all INT Classes
-- ** This includes each patent in all its assigned classes
UPDATE uspto.METRICS_C AS m
SET
avgbwdcit = t2.avgbwdcit,
avgfwdcit = t2.avgfwdcit,
avgtct = t2.avgtct,
avgtct_m = t2.avgtct_m,
avgclaims = t2.avgclaims,
avgdrawings = t2.avgdrawings,
avgfigures = t2.avgfigures
FROM (
  SELECT
  a.section, a.class, a.subclass, a.maingroup
  AVG(b.backwardcitcnt) AS avgbwdcit,
  AVG(b.forwardcitcnt) AS avgfwdcit,
  AVG(b.tct) AS avgtct,
  AVG(b.tct_m) AS avgtct_m,
  AVG(c.claimsnum) AS avgclaims,
  AVG(c.drawingsnum) AS avgdrawings,
  AVG(c.figuresnum) AS avgfigures
  FROM uspto.intclass_g AS a
  LEFT JOIN uspto.metrics_g AS b ON
  a.grantid=b.grantid
  LEFT JOIN uspto.grant AS c ON
  a.grantid=c.grantid
  GROUP BY a.section, a.class, a.subclass, a.maingroup
) AS t2
WHERE
m.schema = 'INT'
AND m.section = t2.section
AND m.class = t2.class
AND m.subclass = t2.subclass;
