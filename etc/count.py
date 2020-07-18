#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

#
# DAT file
#
count = 0
line_no = 0
string_line = None
#with open("/home/development/Desktop/1999.dat", "r", errors='replace') as infile:
    #lines = infile.readlines()
data_file_contents = codecs.open("/home/development/Desktop/1999.dat",'r', 'iso-8859-1')
EOF = False
while not EOF:
#for line in lines:
    line = data_file_contents.readline()
    if not line:
        EOF = True;
    #line = line.decode()
    #line = line.decode("utf-8", errors='replace')
    print(str(line_no) + ": ")
    if "PATN" in line:
        count += 1
    line_no += 1
    if "58939431" in line:
        string_line = line_no
        print("Search line: " + str(string_line))
        exit();
print("PATN Count: " + str(count))
print("Total lines: " +  str(line_no))
print("Search line: " + str(string_line))

#
# CSV file
#
count = 0
line_no = 0
with open("/home/development/Software/uspto/CSV/CSV_G/grant_1999.csv", "r", errors='replace') as infile:
    lines = infile.readlines()

for line in lines:
    #print(line_no + ": " + line)
    if "|" in line:
        count += 1
    line_no += 1
print("CSV Count: " + str(count))
print("CSV Lines: " + str(line_no))
