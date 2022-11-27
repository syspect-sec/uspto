import csv
import re

files = [
"application_links.log",
"grant_links.log",
"legal_links.log",
"pair_links.log"
]

# Verifies a filename using regex
def verify(filename):
    #pattern = re.compile(r'^ipab|pab|ipgb|pgb[/d{8,}]_wk[\d{2,}]')
    pattern = re.compile(r'^[ipagb]{3,4}[0-9]{8}_wk[0-9]{2}$|^[0-9]{4}$|^[a-z_]{5,20}$')
    if re.search(pattern, filename):
        print("MATCH: " + filename)
    else:
        print("NO MATCH!: " + filename)


for item in files:
    with open('../LOG/' + item, 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        list_of_csv = list(csv_reader)
        for line in list_of_csv:
            if len(line) != 0:
                #filename = line[0].split("/")[-1].rstrip(".zip").rstrip(".csv").rstrip(".txt")
                filename = line[0].split("/")[-1].split(".")[0].strip()
                verify(filename)
