-- -----------------------------------------------------
-- Create Databse uspto
-- -----------------------------------------------------

DROP DATABASE IF EXISTS uspto2;
CREATE DATABASE uspto2;

\c uspto2;

DROP SCHEMA IF EXISTS uspto2 CASCADE;
CREATE SCHEMA IF NOT EXISTS uspto2;

-- -----------------------------------------------------
-- Table uspto2.APPLICATION_PAIR
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.APPLICATION_PAIR (
  ApplicationID VARCHAR(20) NOT NULL,
  FileDate DATE DEFAULT NULL,
  AppType VARCHAR(45) DEFAULT NULL,
  ExaminerName VARCHAR(100) DEFAULT NULL,
  GroupArtUnit VARCHAR(45) DEFAULT NULL,
  ConfirmationNum VARCHAR(45) DEFAULT NULL,
  AttorneyDNum VARCHAR(45) DEFAULT NULL,
  ClassSubClass VARCHAR(45) DEFAULT NULL,
  InventorFName VARCHAR(100) DEFAULT NULL,
  CustomerNum VARCHAR(45) DEFAULT NULL,
  Status VARCHAR(200) DEFAULT NULL,
  StatusDate DATE DEFAULT NULL,
  Location VARCHAR(100) DEFAULT NULL,
  LocationDate DATE DEFAULT NULL,
  PubNoEarliest VARCHAR(45) DEFAULT NULL,
  PubDateEarliest DATE DEFAULT NULL,
  PatentNum VARCHAR(45) DEFAULT NULL,
  PatentIssueDate DATE DEFAULT NULL,
  TitleInvention VARCHAR(500) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, FileName));

-- -----------------------------------------------------
-- Table uspto2.APPLICATION
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.APPLICATION (
  ApplicationID VARCHAR(20) NOT NULL,
  PublicationID VARCHAR(20) DEFAULT NULL,
  FileDate DATE DEFAULT NULL,
  Kind VARCHAR(2) DEFAULT NULL,
  USSeriesCode VARCHAR(2) DEFAULT NULL,
  AppType VARCHAR(45) DEFAULT NULL,
  PublishDate DATE DEFAULT NULL,
  Title VARCHAR(500) DEFAULT NULL,
  Abstract TEXT DEFAULT NULL,
  ClaimsNum INT DEFAULT NULL,
  DrawingsNum INT DEFAULT NULL,
  FiguresNum INT DEFAULT NULL,
  Description TEXT DEFAULT NULL,
  Claims TEXT DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, FileName));

-- -----------------------------------------------------
-- Table uspto2.GRANT
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.GRANT (
  GrantID VARCHAR(20) NOT NULL,
  IssueDate DATE DEFAULT NULL,
  Kind VARCHAR(2) DEFAULT NULL,
  USSeriesCode VARCHAR(2) DEFAULT NULL,
  Title VARCHAR(500) DEFAULT NULL,
  Abstract TEXT DEFAULT NULL,
  Description TEXT DEFAULT NULL,
  Claims TEXT DEFAULT NULL,
  ClaimsNum INT DEFAULT NULL,
  DrawingsNum INT DEFAULT NULL,
  FiguresNum INT DEFAULT NULL,
  GrantLength INT DEFAULT NULL,
  ApplicationID VARCHAR(20) DEFAULT NULL,
  FileDate DATE DEFAULT NULL,
  AppType VARCHAR(45) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, FileName));

-- -----------------------------------------------------
-- Table uspto2.INTCLASS_A
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.INTCLASS_A (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Section VARCHAR(15) DEFAULT NULL,
  Class VARCHAR(15) DEFAULT NULL,
  SubClass VARCHAR(15) DEFAULT NULL,
  MainGroup VARCHAR(15) DEFAULT NULL,
  SubGroup VARCHAR(15) DEFAULT NULL,
  Malformed BOOLEAN DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

  -- -----------------------------------------------------
  -- Table uspto2.CPCCLASS_A
  -- -----------------------------------------------------

  CREATE TABLE IF NOT EXISTS uspto2.CPCCLASS_A (
    ApplicationID VARCHAR(20) NOT NULL,
    Position INT NOT NULL,
    Section VARCHAR(15) DEFAULT NULL,
    Class VARCHAR(15) DEFAULT NULL,
    SubClass VARCHAR(15) DEFAULT NULL,
    MainGroup VARCHAR(15) DEFAULT NULL,
    SubGroup VARCHAR(15) DEFAULT NULL,
    Malformed BOOLEAN DEFAULT NULL,
    FileName VARCHAR(45),
    PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.USCLASS_A
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.USCLASS_A (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Class VARCHAR(5) DEFAULT NULL,
  SubClass VARCHAR(15) DEFAULT NULL,
  Malformed BOOLEAN DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.INVENTOR_A
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.INVENTOR_A (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  FirstName VARCHAR(100) DEFAULT NULL,
  LastName VARCHAR(100) DEFAULT NULL,
  City VARCHAR(100) DEFAULT NULL,
  State VARCHAR(100) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  Nationality VARCHAR(100) DEFAULT NULL,
  Residence VARCHAR(300) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.ATTORNEY_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.ATTORNEY_P (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  RegNo VARCHAR(20) DEFAULT NULL,
  FirstName VARCHAR(45) DEFAULT NULL,
  LastName VARCHAR(45) DEFAULT NULL,
  Phone VARCHAR(45) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.FOREIGNPRIORITY_A
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.FOREIGNPRIORITY_A (
  ApplicationID VARCHAR(20) NOT NULL,
  DocumentID VARCHAR(100) NOT NULL,
  Position INT NOT NULL,
  Kind VARCHAR(45) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  PriorityDate DATE DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.TRANSACTION
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.TRANSACTION_P (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Description TEXT DEFAULT NULL,
  Date DATE DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.CORRESPONDENCE_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.CORRESPONDENCE_P (
  ApplicationID VARCHAR(20) NOT NULL,
  Name_1 VARCHAR(100) DEFAULT NULL,
  Name_2 VARCHAR(100) DEFAULT NULL,
  Address TEXT DEFAULT NULL,
  City VARCHAR(50) DEFAULT NULL,
  RegionCode VARCHAR(50) DEFAULT NULL,
  RegionName VARCHAR(50) DEFAULT NULL,
  PostalCode VARCHAR(20) DEFAULT NULL,
  CountryCode VARCHAR(5) DEFAULT NULL,
  CountryName VARCHAR(50) DEFAULT NULL,
  CustomerNum VARCHAR(45) DEFAULT NULL,
  FileName VARCHAR(45) NOT NULL,
  PRIMARY KEY (ApplicationID, FileName));

-- -----------------------------------------------------
-- Table uspto2.CONTINUITYPARENT_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.CONTINUITYPARENT_P (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT DEFAULT NULL,
  ParentApplicationID VARCHAR(45) NOT NULL,
  FileDate DATE DEFAULT NULL,
  ContinuationType VARCHAR(50) NOT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, ParentApplicationID, FileName));

-- -----------------------------------------------------
-- Table uspto2.CONTINUITYCHILD_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.CONTINUITYCHILD_P (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT DEFAULT NULL,
  ChildApplicationID VARCHAR(45) NOT NULL,
  FileDate DATE DEFAULT NULL,
  ContinuationType VARCHAR(50) NOT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, ChildApplicationID, FileName));

-- -----------------------------------------------------
-- Table uspto2.ADJUSTMENT_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.ADJUSTMENT_P (
  ApplicationID VARCHAR(20) NOT NULL,
  PriorAfter BOOLEAN DEFAULT NULL,
  FileDate DATE DEFAULT NULL,
  IssueDate DATE DEFAULT NULL,
  PreIssuePetitions VARCHAR(45) DEFAULT NULL,
  PostIssuePetitions VARCHAR(45) DEFAULT NULL,
  USPTOAdjustDays VARCHAR(45) DEFAULT NULL,
  USPTODelayDays VARCHAR(45) DEFAULT NULL,
  ThreeYears VARCHAR(45) DEFAULT NULL,
  APPLDelayDays VARCHAR(45) DEFAULT NULL,
  TotalTermAdjustDays VARCHAR(45) DEFAULT NULL,
  ADelays VARCHAR(45) DEFAULT NULL,
  BDelays VARCHAR(45) DEFAULT NULL,
  CDelays VARCHAR(45) DEFAULT NULL,
  OverlapDays VARCHAR(45) DEFAULT NULL,
  NonOverlapDelays VARCHAR(45) DEFAULT NULL,
  FileName VARCHAR(45),
  PTOManualAdjust VARCHAR(45) DEFAULT NULL);

-- -----------------------------------------------------
-- Table uspto2.ADJUSTMENTDESC_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.ADJUSTMENTDESC_P (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  PriorAfter BOOLEAN DEFAULT NULL,
  Number INT DEFAULT NULL,
  Date DATE DEFAULT NULL,
  ContentDesc TEXT DEFAULT NULL,
  PTODays VARCHAR(45) DEFAULT NULL,
  APPLDays VARCHAR(45) DEFAULT NULL,
  Start VARCHAR(45) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.EXTENSION_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.EXTENSION_P (
  ApplicationID VARCHAR(20) NOT NULL,
  FileDate DATE DEFAULT NULL,
  USPTOAdjustDays INT DEFAULT NULL,
  USPTODelays INT DEFAULT NULL,
  CorrectDelays INT DEFAULT NULL,
  FileName VARCHAR(45),
  TotalExtensionDays INT DEFAULT NULL);

-- -----------------------------------------------------
-- Table uspto2.EXTENSIONDESC_P
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.EXTENSIONDESC_P (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Date DATE DEFAULT NULL,
  Description TEXT DEFAULT NULL,
  PTODays VARCHAR(45) DEFAULT NULL,
  APPLDays VARCHAR(45) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.AGENT_A
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.AGENT_A (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  OrgName VARCHAR(300) DEFAULT NULL,
  LastName VARCHAR(100) DEFAULT NULL,
  FirstName VARCHAR(100) DEFAULT NULL,
  Address VARCHAR(200) DEFAULT NULL,
  City VARCHAR(50) DEFAULT NULL,
  State VARCHAR(5) DEFAULT NULL,
  Country VARCHAR(5) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.ASSIGNEE_A
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.ASSIGNEE_A (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  OrgName VARCHAR(300) DEFAULT NULL,
  FirstName VARCHAR(100) DEFAULT NULL,
  LastName VARCHAR(100) DEFAULT NULL,
  Role VARCHAR(45) DEFAULT NULL,
  City VARCHAR(100) DEFAULT NULL,
  State VARCHAR(100) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.APPLICANT_A
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.APPLICANT_A (
  ApplicationID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  OrgName VARCHAR(300) DEFAULT NULL,
  FirstName VARCHAR(100) DEFAULT NULL,
  LastName VARCHAR(100) DEFAULT NULL,
  City VARCHAR(100) DEFAULT NULL,
  State VARCHAR(100) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (ApplicationID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.USCLASS_C
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.USCLASS_C (
  Class VARCHAR(3) NULL,
  SubClass VARCHAR(6) DEFAULT NULL,
  Indent VARCHAR(2) DEFAULT  NULL,
  SubClassSqsNum VARCHAR(4) DEFAULT NULL,
  NextHigherSub VARCHAR(6) DEFAULT NULL,
  Title TEXT DEFAULT NULL,
  FileName VARCHAR(45) NOT NULL
);

-- -----------------------------------------------------
-- Table uspto2.CPCClASS_C
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.CPCClASS_C (
  Section VARCHAR(15) DEFAULT NULL,
  Class VARCHAR(15) DEFAULT NULL,
  SubClass VARCHAR(15) DEFAULT NULL,
  MainGroup VARCHAR(15) DEFAULT NULL,
  SubGroup VARCHAR(15) DEFAULT NULL,
  Title TEXT DEFAULT NULL,
  FileName VARCHAR(45) NOT NULL
);

-- -----------------------------------------------------
-- Table uspto2.USCPC_C
-- -----------------------------------------------------
DROP TABLE IF EXISTS uspto2.USCPC_C ;

CREATE TABLE IF NOT EXISTS uspto2.USCPC_C (
  USClass VARCHAR(15) NOT NULL,
  CPCClass VARCHAR(15) DEFAULT NULL,
  Position INT NOT NULL,
  FileName VARCHAR(45) NOT NULL,
  PRIMARY KEY (USClass, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.INTCLASS_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.INTCLASS_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Section VARCHAR(15) DEFAULT NULL,
  Class VARCHAR(15) DEFAULT NULL,
  SubClass VARCHAR(15) DEFAULT NULL,
  MainGroup VARCHAR(15) DEFAULT NULL,
  SubGroup VARCHAR(15) DEFAULT NULL,
  Malformed BOOLEAN DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.CPCCLASS_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.CPCCLASS_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Section VARCHAR(15) DEFAULT NULL,
  Class VARCHAR(15) DEFAULT NULL,
  SubClass VARCHAR(15) DEFAULT NULL,
  MainGroup VARCHAR(15) DEFAULT NULL,
  SubGroup VARCHAR(15) DEFAULT NULL,
  Malformed BOOLEAN DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.NONPATCIT_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.NONPATCIT_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Citation TEXT DEFAULT NULL,
  Category VARCHAR(20) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.APPLICANT_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.APPLICANT_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  OrgName VARCHAR(300) DEFAULT NULL,
  FirstName VARCHAR(100) DEFAULT NULL,
  LastName VARCHAR(100) DEFAULT NULL,
  City VARCHAR(100) DEFAULT NULL,
  State VARCHAR(100) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.INVENTOR_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.INVENTOR_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  FirstName VARCHAR(100) DEFAULT NULL,
  LastName VARCHAR(100) DEFAULT NULL,
  City VARCHAR(100) DEFAULT NULL,
  State VARCHAR(100) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  Nationality VARCHAR(100) DEFAULT NULL,
  Residence VARCHAR(300) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.USCLASS_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.USCLASS_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  Class VARCHAR(5) DEFAULT NULL,
  SubClass VARCHAR(15) DEFAULT NULL,
  Malformed BOOLEAN DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.AGENT_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.AGENT_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  OrgName VARCHAR(300) DEFAULT NULL,
  LastName VARCHAR(100) DEFAULT NULL,
  FirstName VARCHAR(100) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.ASSIGNEE_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.ASSIGNEE_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  OrgName VARCHAR(500) DEFAULT NULL,
  Role VARCHAR(45) DEFAULT NULL,
  City VARCHAR(100) DEFAULT NULL,
  State VARCHAR(100) DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.EXAMINER_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.EXAMINER_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  LastName VARCHAR(50) DEFAULT NULL,
  FirstName VARCHAR(50) DEFAULT NULL,
  Department VARCHAR(100) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.GRACIT_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.GRACIT_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  CitedID VARCHAR(20) DEFAULT NULL,
  Kind VARCHAR(10) DEFAULT NULL,
  Name VARCHAR(100) DEFAULT NULL,
  Date DATE DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  Category VARCHAR(20) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.FORPATCIT_G
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.FORPATCIT_G (
  GrantID VARCHAR(20) NOT NULL,
  Position INT NOT NULL,
  CitedID VARCHAR(25) DEFAULT NULL,
  Kind VARCHAR(10) DEFAULT NULL,
  Name VARCHAR(100) DEFAULT NULL,
  Date DATE DEFAULT NULL,
  Country VARCHAR(100) DEFAULT NULL,
  Category VARCHAR(20) DEFAULT NULL,
  FileName VARCHAR(45),
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.FOREIGNPRIORITY_G
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS uspto2.FOREIGNPRIORITY_G (
  GrantID VARCHAR(20) NOT NULL,
  DocumentID VARCHAR(45) NOT NULL,
  Position INT NOT NULL,
  Kind VARCHAR(45) DEFAULT NULL,
  Country VARCHAR(5) DEFAULT NULL,
  PriorityDate DATE DEFAULT NULL,
  FileName VARCHAR(45) NOT NULL,
  PRIMARY KEY (GrantID, Position, FileName));

-- -----------------------------------------------------
-- Table uspto2.CASES_L
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.CASE_L (
  CaseID VARCHAR(15) NOT NULL,
  PacerID VARCHAR(10) NOT NULL,
  CourtTitle VARCHAR(150) DEFAULT NULL,
  DistrictID VARCHAR(15) DEFAULT NULL,
  CaseTitle VARCHAR(250) DEFAULT NULL,
  AssignedTo VARCHAR(100) DEFAULT NULL,
  ReferredTo VARCHAR(100) DEFAULT NULL,
  Cause VARCHAR(100) DEFAULT NULL,
  JurisdictionBasis VARCHAR(30) DEFAULT NULL,
  FiledDate DATE DEFAULT NULL,
  CloseDate DATE DEFAULT NULL,
  LastFileDate DATE DEFAULT NULL,
  JuryDemand VARCHAR(20) DEFAULT NULL,
  Demand VARCHAR(20) DEFAULT NULL,
  LeadCase VARCHAR(100) DEFAULT NULL,
  RelatedCase TEXT DEFAULT NULL,
  Settlement TEXT DEFAULT NULL,
  CaseIDRaw VARCHAR(50) DEFAULT NULL,
  CaseType1 VARCHAR(20) DEFAULT NULL,
  CaseType2 VARCHAR(20) DEFAULT NULL,
  CaseType3 VARCHAR(20) DEFAULT NULL,
  CaseTypeNote VARCHAR(30) DEFAULT NULL,
  FileName VARCHAR(45) NOT NULL,
  PRIMARY KEY (CaseID, FileName));

-- -----------------------------------------------------
-- Table uspto2.ATTORNEY_L
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.ATTORNEY_L (
  CaseID VARCHAR(15) NOT NULL,
  CaseIDRaw VARCHAR(50) DEFAULT NULL,
  PartyType VARCHAR(30) DEFAULT NULL,
  Name VARCHAR(100) NOT NULL,
  ContactInfo TEXT DEFAULT NULL,
  Position VARCHAR(200) DEFAULT NULL,
  FileName VARCHAR(45) DEFAULT NULL);

-- -----------------------------------------------------
-- Table uspto2.PARTY_L
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.PARTY_L (
  CaseID VARCHAR(15) NOT NULL,
  PartyType VARCHAR(50) NOT NULL,
  Name VARCHAR(1000) NOT NULL,
  FileName VARCHAR(45) NOT NULL);

-- -----------------------------------------------------
-- Table uspto2.PATENT_L
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.PATENT_L (
  CaseID VARCHAR(15) NOT NULL,
  PacerID VARCHAR(10) NOT NULL,
  NOS VARCHAR(10) DEFAULT NULL,
  PatentID VARCHAR(20) NOT NULL,
  PatentDocType VARCHAR(30) DEFAULT NULL,
  FileName VARCHAR(45) NOT NULL,
  PRIMARY KEY (CaseID, PatentID, FileName));

-- -----------------------------------------------------
-- Table uspto2.STARTED_FILES
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS uspto2.STARTED_FILES (
  FileName VARCHAR(45),
  PRIMARY KEY (FileName));

-- -----------------------------------------------------
-- Create PostgreSQL Users
-- -----------------------------------------------------

-- Drop user if exists and create a new user with password
DROP USER IF EXISTS uspto;
CREATE USER uspto LOGIN PASSWORD 'Ld58KimTi06v2PnlXTFuLG4';

-- Change the owner of uspto database to uspto user
ALTER DATABASE uspto2 OWNER TO uspto;
ALTER SCHEMA uspto2 OWNER to uspto;
ALTER DATABASE uspto2 SET search_path TO uspto;

-- Grant privileges to all corresponding databases
GRANT USAGE ON SCHEMA uspto2 TO uspto;
GRANT ALL ON ALL TABLES IN SCHEMA uspto2 TO uspto;
