from csv import reader
from pprint import pprint

# open file in read mode
longest = []
with open('/Users/development/Downloads/attorneys.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        # row variable is a list that represents a row in csv
        if len(longest):
            for i in range(0,len(row)):
                if len(row[i]) > longest[i]:
                    longest[i] = len(row[i])
        else:
            for i in range(0,len(row)):
                longest.append(len(row[i]))
pprint(longest)
print("-- Finished!")
