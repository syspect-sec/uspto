import csv

def function_write_csv():
    field_names = {}
    writers = {}

    field_names['grant'] = ['GrantID', 'ID', 'Kind', 'USSeriesCode', 'Title', 'Abstract', 'Claims', 'ClaimsNum', 'DrawingsNum', 'FiguresNum', 'GrantLength', 'ApplicationID', 'FileDate', 'AppType', 'FileName']
    field_names['application'] = ['ApplicationID', 'ID', 'Kind', 'USSeriesCode', 'Title', 'Abstract', 'Claims', 'ClaimsNum', 'DrawingsNum', 'FiguresNum', 'GrantLength', 'ApplicationID', 'FileDate', 'AppType', 'FileName']

    writers['grant'] = csv.DictWriter(open('names.csv', 'w'), fieldnames = field_names['grant'])
    writers['application'] = csv.DictWriter(open('names_app.csv', 'w'), fieldnames = field_names['application'])


    writers['grant'].writeheader()
    writers['application'].writeheader()

    return writers

writers = function_write_csv()
print(writers)
