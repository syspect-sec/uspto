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
DROP TABLE IF EXISTS `uspto`.`PARSER_SUMMARY` ;

CREATE TABLE IF NOT EXISTS uspto.PARSER_SUMMARY (
  `FileName` VARCHAR(45) NOT NULL,
  `TableName` VARCHAR(45) NOT NULL,
  `Count` VARCHAR(45) NOT NULL,
  PRIMARY KEY (FileName, TableName));

-- -----------------------------------------------------
-- Insert Counts for All Tables
-- -----------------------------------------------------

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "AGENT_A", count(*)
FROM AGENT_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "AGENT_G", count(*)
FROM AGENT_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "APPLICANT_A", count(*)
FROM APPLICANT_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "APPLICANT_G", count(*)
FROM APPLICANT_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "APPLICATION", count(*)
FROM APPLICATION
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "ASSIGNEE_A", count(*)
FROM ASSIGNEE_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "ASSIGNEE_G", count(*)
FROM ASSIGNEE_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "ATTORNEY_L", count(*)
FROM ATTORNEY_L
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "CASE_L", count(*)
FROM CASE_L
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "CONTINUITYPARENT_P", count(*)
FROM CONTINUITYPARENT_P
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "CONTINUITYCHILD_P", count(*)
FROM CONTINUITYCHILD_P
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "CPCCLASS_A", count(*)
FROM CPCCLASS_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "CPCCLASS_C", count(*)
FROM CPCCLASS_C
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "CPCCLASS_G", count(*)
FROM CPCCLASS_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "EXAMINER_G", count(*)
FROM EXAMINER_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "FOREIGNPRIORITY_A", count(*)
FROM FOREIGNPRIORITY_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "FOREIGNPRIORITY_G", count(*)
FROM FOREIGNPRIORITY_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "FORPATCIT_G", count(*)
FROM FORPATCIT_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "GRACIT_G", count(*)
FROM GRACIT_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "GRANT", count(*)
FROM GRANT
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "INTCLASS_A", count(*)
FROM INTCLASS_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "INTCLASS_G", count(*)
FROM INTCLASS_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "INTVENTOR_A", count(*)
FROM INVENTOR_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "INVENTOR_G", count(*)
FROM INVENTOR_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "NONPATCIT_G", count(*)
FROM NONPATCIT_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "PARTY_L", count(*)
FROM PARTY_L
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "PATENT_L", count(*)
FROM PATENT_L
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "USCLASS_A", count(*)
FROM USCLASS_A
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "USCLASS_C", count(*)
FROM USCLASS_C
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "USCLASS_G", count(*)
FROM USCLASS_G
GROUP BY FileName
ORDER BY FileName DESC;

INSERT INTO PARSER_SUMMARY
(FileName, TableName, Count)
SELECT FileName, "USCPC_C", count(*)
FROM USCPC_C
GROUP BY FileName
ORDER BY FileName DESC;
