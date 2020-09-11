--
-- Calculate Forward Citations for all GrantID
--
UPDATE uspto.METRICS_G, (SELECT CitedID, count(*) as count
FROM uspto.GRACIT_G GROUP BY CitedID) AS t2
SET    uspto.METRICS_G.ForwardCitCnt = t2.count
WHERE  uspto.METRICS_G.GrantID = t2.CitedID;
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
SET    uspto.METRICS_G.BackwardCitCnt = t2.count
WHERE  uspto.METRICS_G.GrantID = t2.GrantID;
--
-- Set all patents without BWD citations to 0
--
UPDATE uspto.METRICS_G
SET uspto.METRICS_G.BackwardCitCnt = 0
WHERE uspto.METRICS_G.BackwardCitCnt IS NULL;
