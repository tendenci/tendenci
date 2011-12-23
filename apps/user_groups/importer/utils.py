import csv
from subscribers.models import SubscriberData, GroupSubscription

def xls_to_dict(file_path):
    """
    Returns a list of dicts. Each dict represents record.
    """
    xls_file = open(file_path, 'rU')
    xls = csv.reader(x.replace('\0', '') for x in xls_file)
    col = xls.next()
    lst = []
    
    try:
        for row in xls:
            entry = {}
            for i in xrange(len(col)):
                entry[col[i]] = row[i].decode('latin-1')
            lst.append(entry)
    except csv.Error as e:
        return []

    return lst  # list of dictionaries

def parse_subs_from_csv(group, file_path):
    """
    Parse subscribers from csv file.
    """
    for csv_dict in xls_to_dict(file_path):  # field mapping
        sub = GroupSubscription.objects.create(group=group)
        for key in csv_dict.keys():
            print key
            #SubscriberData.objects.create(
            #    subscription=sub,
            #    field_label=key,
            #    value=csv_dict[key],
            #)

