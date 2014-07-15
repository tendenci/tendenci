from django.db.models import FloatField

from tendenci.core.imports.utils import extract_from_excel
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
