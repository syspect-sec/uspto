--
-- Calculate Forward Citations for all GrantID
--
UPDATE uspto.METRICS_G, (SELECT CitedID, count(*) as count
FROM uspto.GRACIT_G GROUP BY CitedID) AS t2
SET uspto.METRICS_G.ForwardCitCnt = t2.count
WHERE uspto.METRICS_G.GrantID = t2.CitedID;
--
-- Set all patents without FWD citations to 0
--
UPDATE uspto.METRICS_G
SET uspto.METRICS_G.ForwardCitCnt = 0
WHERE uspto.METRICS_G.ForwardCitCnt IS NULL;
--
-- Calculate Backward Citations for all GrantID
--
UPDATE uspto.METRICS_G, (select GrantID, count(*) as count
FROM uspto.GRACIT_G GROUP BY GrantID) as t2
SET uspto.METRICS_G.BackwardCitCnt = t2.count
WHERE uspto.METRICS_G.GrantID = t2.GrantID;
--
-- Set all patents without BWD citations to 0
--
UPDATE uspto.METRICS_G
SET uspto.METRICS_G.BackwardCitCnt = 0
WHERE uspto.METRICS_G.BackwardCitCnt IS NULL;

--
-- Combines the CONTINUITYCHILD_P and CONTINUITYPARENT_P
-- tables and provdies a count of unique country codes that
-- an application has been filed in.
--
UPDATE METRICS_G m
JOIN (
  SELECT
  ApplicationID,
   COUNT( DISTINCT
   CASE
   WHEN `RefID` REGEXP '^[0-9]+$' THEN 'US'
   ELSE SUBSTRING(`RefID`, 5, 2)
   END
   ) FamilySize,
   GrantID
  FROM (
    SELECT g.ApplicationID, ChildApplicationID `RefID`, g.GrantID
    FROM CONTINUITYCHILD_P `child`
    JOIN uspto.GRANT as g ON child.ApplicationID = g.ApplicationID
    UNION
    SELECT g2.ApplicationID, ParentApplicationID `RefID`, g2.GrantID
    FROM CONTINUITYPARENT_P `par`
    JOIN uspto.GRANT as g2 ON par.ApplicationID = g2.ApplicationID
  ) t1
  GROUP BY ApplicationID
) t2 ON m.GrantID = t2.GrantID
SET m.FamilySize = t2.FamilySize

--
-- Set all patents without FamilySize to 0
--
UPDATE uspto.METRICS_G
SET uspto.METRICS_G.FamilySize = 0
WHERE uspto.METRICS_G.FamilySize IS NULL;
