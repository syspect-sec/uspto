

The file, "sic_08.zip" contains a compressed data file which includes a concordance between 
the U.S. Patent Classification System (USPCS)(as of December 31, 2008) and 
41 unique product fields based on the 1987 Standard Industrial Classification 
System (SIC).  See Table 1, below, for a list of those product fields.

The concordance file is an ASCII comma delimited file with elements placed 
in quotes.  This file format is ideal for importing the data into a database 
software program.  Note that while many spreadsheet software packages may be 
capable of importing ASCII delimited files, this file is probably too large 
to be handled successfully by many of those spreadsheet software packages.

The concordance is contained in the file "sic_co08.zip" which is a
compressed data file.  

The hard drive must have a minimum of roughly 7 megabytes of free space.  

The file record (line) format is as follows:

     field 1:  USPCS Class (3 characters, with leading zeroes).
     field 2:  USPCS Subclass (6 characters with leading zeroes).  
                Note that there is an implied decimal point following the 
                third character.  Subclasses with letter suffixes will generally
                have the suffixes placed in the rightmost columns of the field.
     field 3:  SIC-based product field sequence number (two characters, right
                justified and blank filled).  See Table 1, below.
     field 4:  OTAF code for the SIC-based product field (two to four characters).
                This code indicates the approximate SIC area to which the USPCS 
                Class/Subclass has been concorded.  See Table 1, below.

If a USPCS Class/Subclass has been concorded to more than one SIC-based
product field, additional records identifying those relationships will
be included in the file.

The sort order of the records (lines) contained in the concordance file
is: by class, then by subclass, and then by sequence number.

Questions regarding this file should be directed to:

     U.S. Patent and Trademark Office
     Electronic Information Products Division - PTMT
     P.O. Box 1450
     Alexandria, VA 22313-1450 

     tel  (571) 272-5600
     FAX  (571) 273-0110
--------------------------------------------------------------------------
Table 1.  STANDARD INDUSTRIAL CLASIFICATION PRODUCT FIELDS

(table with corresponding SEQUENCE NUMBER, OTAF CODE, OTAF
 PRODUCT FIELD TITLE, and SIC CODES)

*  OTAF CODES which are prefaced with an "R" represent combinations or 
   "roll-ups" of unique OTAF CODES.

SEQUENCE OTAF   OTAF
NUMBER   CODE   PRODUCT FIELD TITLE                                                     SIC CODES
_______ ____    _____________________________________________________________________   _________
1        20     FOOD AND KINDRED PRODUCTS                                               20
2        22     TEXTILE MILL PRODUCTS                                                   22
3        R1     CHEMICALS AND ALLIED PRODUCTS                                           28
4        R2       Chemicals, except drugs and medicines                                 281,282,284-289
5        R3         Basic industrial inorganic and organic chemistry                    281,286
6        281          Industrial inorganic chemistry                                    281
7        286          Industrial organic chemistry                                      286
8        282        Plastics materials and synthetic resins                             282
9        287        Agricultural chemicals                                              287
10       R4         All other chemicals                                                 284,285,289
11       284          Soaps, detergents, cleaners, perfumes, cosmetics and toiletries   284
12       285          Paints, varnishes, lacquers, enamels, and allied products         285
13       289          Miscellaneous chemical products                                   289
14       283      Drugs and medicines                                                   283
15       1329   PETROLEUM AND NATURAL GAS EXTRACTION AND REFINING                       13,29
16       30     RUBBER AND MISCELLANEOUS PLASTICS PRODUCTS                              30
17       32     STONE, CLAY, GLASS AND CONCRETE PRODUCTS                                32
18       R5     PRIMARY METALS                                                          33,3462,3463
19       331+     Primary ferrous products                                              331,332,3399,3462
20       333+     Primary and secondary non-ferrous metals                              333-336,339(except 3399),3463
21       34-    FABRICATED METAL PRODUCTS                                               34(except 3462,3463,348)
22       R6     MACHINERY, EXCEPT ELECTRICAL                                            35
23       351      Engines and turbines                                                  351
24       352      Farm and garden machinery and equipment                               352
25       353      Construction, mining and material handling machinery and equipment    353
26       354      Metal working machinery and equipment                                 354
27       357      Office computing and accounting machines                              357
28       R7       Other machinery, except electrical                                    355,356,358,359
29       355        Special industry machinery, except metal working                    355
30       356        General industrial machinery and equipment                          356
31       358        Refrigeration and service industry machinery                        358
32       359        Miscellaneous machinery, except electrical                          359
33       R8     ELECTRICAL AND ELECTRONIC MACHINERY, EQUIPMENT AND SUPPLIES             36,3825
34       R9       Electrical equipment, except communications equipment                 361-364,369,3825
35       361+       Electrical transmission and distribution equipment                  361,3825
36       362        Electrical industrial apparatus                                     362
37       R10        Other electrical machinery, equipment and supplies                  363,364,369
38       363          Household appliances                                              363
39       364          Electrical lighting and wiring equipment                          364
40       369          Miscellaneous electrical machinery, equipment and supplies        369
41       R11      Communications equipment and electronic components                    365-367
42       365        Radio and television receiving equipment except communication types 365
43       366+       Electronic components and accessories and communications equipment  366-367
44       R12    TRANSPORTATION EQUIPMENT                                                37,348
45       R13      Motor vehicles and other transportation equipment, except aircraft    348,371,373-376,379
46       371        Motor vehicles and other motor vehicle equipment                    371
47       376        Guided missiles and space vehicles and parts                        376
48       R14        Other transportation equipment                                      373-375,379(except 3795)
49       373          Ship and boat building and repairing                              373
50       374          Railroad equipment                                                374
51       375          Motorcycles, bicycles, and parts                                  375
52       379-         Miscellaneous transportation equipment                            379(except 3795)
53       348+       Ordinance except missiles                                           348,3795
54       372      Aircraft and parts                                                    372
55       38-    PROFESSIONAL AND SCIENTIFIC INSTRUMENTS                                 38(except 3825)
56       99     ALL OTHER SIC'S                                                         99
57       R15    ALL INDUSTRIES