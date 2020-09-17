count = 0
print_lines = False
file = open("/Users/development/Software/uspto/CSV/CSV_P/correspondence.csv", "r");
EOF = False
while not EOF:
#for line in lines:
    line = file.readline()
    #print(line)
    if not line:
        EOF = True;
    elif "|" in line:
        count = len(line.split("|"))

    if count != 12:
        print(count)
        print(line)
        exit()
    else:
        print(count)
        print(line)
