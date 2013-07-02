import xlrd

from django.db.models import Q, FloatField
from django.core.validators import email_re

from tendenci.core.imports.utils import extract_from_excel
from tendenci.apps.forms_builder.forms.models import FieldEntry
from tendenci.apps.subscribers.models import SubscriberData, GroupSubscription
from tendenci.apps.user_groups.models import Group


GROUP_FIELDS = [
    'name',
    'label',
    'type',
    'email_recipient',
    'description',
    'auto_respond_priority',
    'notes'
    ]

TYPE_FIELD_CHOICES = [
    '',
    'distribution',
    'security'
    ]

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
                sub.save() # first save to acquire primary key
                for datum in sub_data:
                    datum.subscription = sub
                    datum.save()
                # Needs 2nd save because there is no email field in first save
                sub.save()
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


def user_groups_import_process(import_i, preview=True):
    """
    This function processes each row and store the data
    in the group_object_dict. Then it updates the database
    if preview=False.
    """
    #print "START IMPORT PROCESS"
    data_dict_list = extract_from_excel(import_i.file.name)
    data_dict_list_len = len(data_dict_list)

    group_obj_list = []
    invalid_list = []
    
    import_i.total_invalid = 0
    import_i.total_created = 0
    if not preview: #update import status
        import_i.status = "processing"
        import_i.save()
    
    try:
        # loop through the file's entries and determine valid imports
        start = 0
        finish = data_dict_list_len
        for r in range(start, finish):
            invalid = False
            group_object_dict = {}
            data_dict = data_dict_list[r]

            for key in data_dict.keys():
                group_object_dict[key] = data_dict[key]

            group_object_dict['ROW_NUM'] = data_dict['ROW_NUM']

            # Validate Group Name
            try:
                group_exists = Group.objects.get(name=group_object_dict['name'])
                invalid = True
                invalid_reason = "A GROUP WITH NAME '%s' ALREADY EXISTS" % group_object_dict['name']
            except Group.DoesNotExist:
                pass

            # Validate Type Field
            if not group_object_dict['type'] in TYPE_FIELD_CHOICES:
                invalid = True
                invalid_reason = "INVALID TYPE %s" % group_object_dict['type']

            # Validate Auto Respond Priority
            if group_object_dict['auto_respond_priority']:
                try:
                    group_object_dict['auto_respond_priority'] = float(group_object_dict['auto_respond_priority'])
                except ValueError:
                    invalid = True
                    invalid_reason = "AUTO RESPOND PRIORITY ONLY ACCEPTS FLOAT VALUES"
            else:
                group_object_dict['auto_respond_priority'] = 0

            if invalid:
                group_object_dict['ERROR'] = invalid_reason
                group_object_dict['IS_VALID'] = False
                import_i.total_invalid += 1
                if not preview:
                    invalid_list.append({
                        'ROW_NUM': group_object_dict['ROW_NUM'],
                        'ERROR': group_object_dict['ERROR']})
            else:
                group_object_dict['IS_VALID'] = True
                import_i.total_created += 1

                if not preview:
                    group_import_dict = {}
                    group_import_dict['ACTION'] = 'insert'
                    group = do_group_import(group_object_dict)
                    group_import_dict = {}
                    group_import_dict['group'] = group
                    group_import_dict['ROW_NUM'] = group_object_dict['ROW_NUM']
                    group_obj_list.append(group_import_dict)

            if preview:
                group_obj_list.append(group_object_dict)

        if not preview: # save import status
            import_i.status = "completed"
            import_i.save()
    except Exception, e:
        import_i.status = "failed"
        import_i.failure_reason = unicode(e)
        import_i.save()

    #print "END IMPORT PROCESS"
    return group_obj_list, invalid_list

def do_group_import(group_object_dict):
    """Creates and Event and Place for the given event_object_dict
    """
    group = Group()

    # assure the correct fields get the right value types
    for field in GROUP_FIELDS:
        if field in group_object_dict:
            field_type = Group._meta.get_field_by_name(field)[0]
            if isinstance(field_type, FloatField):
                setattr(group, field, group_object_dict[field])
            else:
                if field_type.max_length:
                    setattr(group, field, unicode(group_object_dict[field])[:field_type.max_length])
                else:
                    setattr(group, field, unicode(group_object_dict[field]))
    # Since the allow_anonymous_view is not included in the GROUP_FIELDS,
    # set it to False
    group.allow_anonymous_view = False
    group.save()

    return group
