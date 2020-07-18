#!/usr/bin/env python
# -*- coding: utf-8 -*-


#
# DAT file
#
infile = open("/home/development/Desktop/1999_small.dat", "r", errors='replace')

file_EOF = False
while not file_EOF:
    line = infile.readline()
    if not line:
        file_EOF = True
    print(line)

print(finished)
