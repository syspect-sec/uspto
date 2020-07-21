The file, "naics_co14.zip" contains a compressed data file which includes a concordance between the 
U.S. Patent Classification System (USPCS)(as of December 31, 2014) and 26 unique product fields based 
on the 2002 North American Industry Classification System (NAICS).  See Table 1, below, for a list of 
those product fields.

The concordance file is an ASCII comma delimited file.  This file format is ideal for importing the 
data into a database software program.  Note that while many spreadsheet software packages may be capable 
of importing ASCII delimited files, this file is probably too large to be handled successfully by many of 
those spreadsheet software packages.

The concordance is contained in the file "naics_co14.zip" which is a compressed data file.  

The file record (line) format is as follows:

     field 1:   USPCS Class (3 characters, with leading zeroes).
     field 2:   USPCS Subclass (6 characters with leading zeroes).  
                Note that there is an implied decimal point following the third character.  Subclasses with 
                letter suffixes will generally have the suffixes placed in the rightmost columns of the field.
     field 3:   NAICS -based product field sequence number (two characters).  See Table 1, below.
     field 4:   OTAF code for the NAICS-based product field (two to four characters).
                 This code indicates the approximate NAICS area to which the USPCS  Class/Subclass has been 
                 concorded.  
                 See Table 1, below.

If a USPCS Class/Subclass has been concorded to more than one NAICS-based product field, additional records 
identifying those relationships will be included in the file.

Questions regarding this file should be directed to:

     U.S. Patent and Trademark Office
     Electronic Information Products Division - PTMT
     P.O. Box 1450
     Alexandria, VA 22313-1450 

     tel  (571) 272-5600
     FAX  (571) 273-0110
--------------------------------------------------------------------------
TABLE 1 - NORTH AMERICAN INDUSTRY CLASSIFICATION SYSTEM (2002) PRODUCT FIELDS


Sequence   OTAF
Number     Code     PRODUCT FIELD TITLE                                                            NAICS CODE
________   ______  ____________________________________________________                           ________________

1	    311    Food                                                                               311	
2	    312    Beverage and Tobacco Products                                                      312	
3	    313+   Textiles, Apparel and Leather                                                      313-316
4	    321	   Wood Products                                                                      321	
5	    322+   Paper, Printing and support activities                                             322,323
6	    R1     Chemicals                                                                          325	
7	    3251   Basic Chemicals                                                                    3251	
8	    3252   Resin, Synthetic Rubber, and Artificial and Synthetic Fibers and Filaments         3252	
9	    3254   Pharmaceutical and Medicines                                                       3254	
10	    325-   Other Chemical Product and Preparation                                             3253,3255,3256,3259
11	    326    Plastics and Rubber Products                                                       326		
12	    327    Nonmetallic Mineral Products                                                       327		
13	    331    Primary Metal                                                                      331		
14	    332    Fabricated Metal Products                                                          332		
15	    333    Machinery                                                                          333		
16	    R2     Computer and Electronic Products                                                   334	
17	    3341   Computer and Peripheral Equipment                                                  3341	
18	    3342   Communications Equipment                                                           3342	
19	    3344   Semiconductors and Other Electronic Components                                     3344	
20	    3345   Navigational, Measuring, Electromedical, and Control Instruments                   3345	
21	    334-   Other Computer and Electronic Products                                             3343,3346	
22	    335    Electrical Equipment, Appliances, and Components                                   335	
23	    R3     Transportation Equipment                                                           336	
24	    3361+  Motor Vehicles, Trailers and Parts                                                 3361-3363	
25	    3364   Aerospace Product and Parts                                                        3364	
26	    336-   Other Transportation Equipment                                                     3365,3366,3369
27	    337    Furniture and Related Products                                                     337	
28	    R4     Miscellaneous Manufacturing                                                        339	
29	    3391   Medical Equipment and Supplies                                                     3391	
30	    339-   Other Miscellaneous                                                                339 (except 3391)
31	    R5     All Industries		




Product fields associated with OTAF codes R1 to R5 are combinations of other product fields.







