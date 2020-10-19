# **USPTO PATENT DATA PARSER**

Copyright (c) 2020 Ripple Software. All rights reserved.

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA

**Author:** Joseph Lee

**Email:** joseph@ripplesoftware.ca

**Website:** https://www.ripplesoftware.ca

**Github Repository:** https://github.com/rippledj/uspto

## **Description:**

The following data description details information about the final parsed database contents and an explanation of table names and their contents.

### **Table Name Suffixes**

Table name suffixes describe the classification of the data in the table.  The following table name suffixes are used.

1. _G : Patent grants
2. _A : Patent applications
3. _C : Patent classification information
4. _L : Data about patent lawsuits
5. _P : Patent Priority Data

### **Table Descriptions**

#### **Patent Grant Tables**

GrantID is used as a foreign key to connect all the patent grant data in normalized database form.

**GRANT**

Contains dates such as the patent issue date, original patent application filing date, counts of the patents claims, drawings and figures, and the kind, series-code, and application type.  The GRANT table also contains patent title, abstract, and full-text claims and description if the full-text option is selected when parsing the bulk-data.

Some of the data is not available in all file-formats such as XML2, or APS.  Therefore caution should be taken when making longitudinal statistical calculations.  

**AGENT_G**

Contains the agent information associated with each patent. Agent is usually a law-firm that handles the patent application ....

**APPLICANTS_G**

The applicant is the organization or personal names of the patent applicant.

**ASSIGNEE_G**

The assignee is the organization or personal names of owner of the patent.

**CPCCLASS_G**

The Cooperative Patent Classifications listed for the patent grant.

**EXAMINER_G**

The USPTO examiner assigned to the evaluation and processing of the patent application into a patent grant.

**FOREIGNPRIORITY_G**

Patents listed on the application as priority applications.  This table includes the priority application document ID as well as the country that the priority application was filed in, and the date the priority application was filed.

**FORPATCIT_G**

Contains any foreign patents listed as reference for a given patent grant.

**GRACIT_G**

Contains any USPTO patents listed as reference for a given patent grant.

**INTCLASS_G**

The International Classifications listed for the patent grant.

**INVENTOR_G**

The named inventor given by the patent applicant.

**METRICS_G**

Statistical metrics for a granted patent, such as forward and backward citation counts, and also Technology Cycle Time (TCT), etc... not finished

**USCLASS_G**

The US Classifications listed for the patent grant.


#### **Patent Application Tables**

ApplicationID is used as a foreign key to connect all the patent application data in normalized database form.

**APPLICATION**

Contains dates such as the patent application filing date, application publish date, counts of the patents claims, drawings and figures, and the kind, series-code, and application type. The APPLICATION table also contains patent title, abstract, and full-text claims and description if the full-text option is selected when parsing the bulk-data.

Some of the data is not available in all file-formats such as XML2, or APS.  Therefore caution should be taken when making longitudinal statistical calculations.

**AGENT_A**

Contains the agent information associated with each patent. Agent is usually a law-firm that handles the patent application ....

**APPLICANT_A**

The applicant is the organization or personal names of the patent applicant.

**ASSIGNEE_A**

The assignee is the organization or personal names of owner of the patent application.

**CPCCLASS_A**

The Cooperative Patent Classifications listed for the patent application.

**FOREIGNPRIORITY_A**

Patent applications listed on the given application as priority applications.  This table includes the priority application document ID as well as the country that the priority application was filed in, and the date the priority application was filed.

**INTCLASS_A**

The International Classifications listed for the patent application.

**INVENTOR_A**

The named inventor given by the patent applicant.

**USCLASS_A**

The US Classifications listed for the patent application.

#### **Patent Classification Tables**

Patent classification tables contain US and CPC class descriptions, and a US to CPC concordance table.

**CPCCLASS_C**

CPC classification titles grouped by section, class, subclass, and groups.

**USCLASS_C**

US classification titles grouped by section, class, subclass.

**USCPC_C**

A US to CPC concordance table.
