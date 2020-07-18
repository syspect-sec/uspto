-- -----------------------------------------------------
-- Table uspto.GRANT_SUMMARY
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto.METRICS_G (
  `GrantID` VARCHAR(20) NOT NULL,
  `ForwardCitCnt` INT DEFAULT NULL,
  `BackwardCitCnt` INT DEFAULT NULL,
  `TCT` INT DEFAULT NULL,
  PRIMARY KEY (`GrantID`))
  ENGINE = InnoDB;

--
-- Create metrics Record for all GrantID
--
INSERT INTO uspto.METRICS_G (`GrantID`) SELECT `GrantID` FROM uspto.GRANT;
--
-- Calculate Forward Citations for all GrantID
--
UPDATE uspto.METRICS_G, (select CitedID, count(*) as count from uspto.GRACIT_G group by CitedID) as t2
SET    uspto.METRICS_G.ForwardCitCnt = t2.count
WHERE  uspto.METRICS_G.GrantID = t2.CitedID;
--
-- Set all patents without FWD citations to 0
--
UPDATE uspto.METRICS_G
SET uspto.METRICS_G.ForwardCitCnt = 0
WHERE uspto.METRICS_G.ForwardCitCnt is NULL;
--
-- Calculate Backward Citations for all GrantID
--
UPDATE uspto.METRICS_G, (select GrantID, count(*) as count from uspto.GRACIT_G group by GrantID) as t2
SET    uspto.METRICS_G.BackwardCitCnt = t2.count
WHERE  uspto.METRICS_G.GrantID = t2.GrantID;
--
-- Set all patents without BWD citations to 0
--
UPDATE uspto.METRICS_G
SET uspto.METRICS_G.BackwardCitCnt = 0
WHERE uspto.METRICS_G.BackwardCitCnt is NULL;
