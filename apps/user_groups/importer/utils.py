import xlrd
from subscribers.models import SubscriberData, GroupSubscription

def xls_to_dict(file_path):
    """
    Returns a list of dicts. Each dict represents record.
    """
    xls = xlrd.open_workbook(file_path)
    lst = []
    
    for i in range(xls.nsheets):
        sheet = xls.sheet_by_index(i)
        cols = sheet.ncols
        for row in range(1, sheet.nrows):
            entry = {}
            for col in range(cols):
                entry[sheet.cell(0, col).value] = sheet.cell(row, col).value
            lst.append(entry)
    
    return lst  # list of dictionaries

def parse_subs_from_csv(group, file_path):
    """
    Parse subscribers from csv file.
    """
    subs = []
    for csv_dict in xls_to_dict(file_path):  # field mapping
        sub = GroupSubscription.objects.create(group=group)
        for key in csv_dict.keys():
            SubscriberData.objects.create(
                subscription=sub,
                field_label=key,
                value=csv_dict[key],
            )
        subs.append(sub)
    return subs
