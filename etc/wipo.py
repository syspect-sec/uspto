import csv

with open("select.html", "w") as outfile:
    input_file = csv.DictReader(open("../installation/CLS/WIPO_ST_3.csv"))
    for row in input_file:
        outfile.write("<option value='" + row['Code'] + "'>" + row['Country'] + "</option>\n")
