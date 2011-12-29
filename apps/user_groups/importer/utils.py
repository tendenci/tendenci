import xlrd
from django.core.validators import email_re
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
    for csv_dict in xls_to_dict(file_path):
        # convert dict to model instances
        sub = GroupSubscription(group=group)
        sub_data = []
        for key in csv_dict.keys():
            sub_data.append(SubscriberData(field_label=key, value=csv_dict[key]))
        
        # obtain the email field. Matching is subject to change.
        # assumption: 1 email per subscriber
        sub_email = None
        for datum in sub_data:
            if email_re.match(datum.value):
                sub_email = datum.value
                break
        
        # skip subscription entry if no email
        if sub_email:
            # check for duplicates
            dup = SubscriberData.objects.filter(value=sub_email, subscription__group=group)
            if not dup: # create the subscriber
                sub.save()
                for datum in sub_data:
                    datum.subscription = sub
                    datum.save()
            else: # update the subscription's fields
                sub = dup[0].subscription
                for datum in sub_data:
                    sub.data.filter(field_label=datum.field_label).update(value=datum.value)
            subs.append(sub)
    return subs
