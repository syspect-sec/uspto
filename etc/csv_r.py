from csv import reader
# open file in read mode
with open('/Users/development/Downloads/correspondence_address.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        # row variable is a list that represents a row in csv
        print(str(len(row)))
        if len(row) != 12:
            print("-- Malformed length found...")
            exit()


print("-- Finished!")
