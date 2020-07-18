count = 0
print_lines = False
file = open("/home/development/Software/uspto/TMP/downloads_new/pab20010315.xml", "r");
EOF = False
while not EOF:
#for line in lines:
    line = file.readline()
    #print(line)
    if not line:
        EOF = True;
    elif "<foreign-priority-data" in line:
        print(line + " " + str(count))
        print_lines = True
        count += 1
    elif "</foreign-priority-data" in line:
        print(line + " " + str(count))
        print_lines = False
    if print_lines:
        print(line)
print(count)
