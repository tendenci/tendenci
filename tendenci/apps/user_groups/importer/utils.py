import xlrd
from django.db.models import Q
from django.core.validators import email_re
from forms_builder.forms.models import FieldEntry
from subscribers.models import SubscriberData, GroupSubscription

def get_subscriber(email, group):
    """
    Return a GroupSubscription with the given email and group.
    """
    sub = GroupSubscription.objects.filter(
        Q(group=group), 
        Q(Q(data__value=email) or Q(subscriber__fields__value=email))
    )
    if sub:
        return sub[0]
    return None

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
            try:
                if email_re.match(datum.value):
                    sub_email = datum.value
                    break
            except:
                pass
        
        # skip subscription entry if no email
        if sub_email:
            # check for duplicates
            dup = get_subscriber(sub_email, group)
            if not dup: # create the subscriber
                sub.save()
                for datum in sub_data:
                    datum.subscription = sub
                    datum.save()
            else: # update the subscription's fields
                sub = dup
                for datum in sub_data:
                    # check form entry fields
                    if sub.subscriber:
                        field_entry = sub.subscriber.fields.filter(field__label=datum.field_label)
                    else:
                        field_entry = None
                    if field_entry: #existing Field Entry
                        field_entry.update(value=datum.value)
                    else:
                        sub_datum = sub.data.filter(field_label=datum.field_label)
                        if sub_datum: #existing SubscriberData
                            sub_datum.update(value=datum.value)
                        else:
                            datum.subscription = sub
                            datum.save()
            subs.append(sub)
    return subs
