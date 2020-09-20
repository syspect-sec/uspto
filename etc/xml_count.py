count = 0
stored = []
print_lines = False
file = open("/Volumes/Thar/uspto/TMP/downloads/unzip/ipab20200109_wk02/ipab20200102.xml", "r");
contents = file.readlines()
for line in contents:
    print(line)
    print(count)
    if "app-type=" in line:
        count += 1
        stored.append(line)

print(count)
stored
