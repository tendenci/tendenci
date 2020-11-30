from builtins import str
import os
import datetime
import re
import csv

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponse
from django.db.models.fields import AutoField, FieldDoesNotExist
from django.utils.encoding import smart_str
from tendenci.apps.base.utils import validate_email
from django.core.files.storage import default_storage

import xlrd
from xlwt import Workbook, XFStyle
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.apps.profiles.models import Profile
from tendenci.apps.base.utils import normalize_newline


# number rows to process per request
ROWS_TO_PROCESS = 10

# field.__class__.__name__
# DateTimeField
user_fields = [field for field in User._meta.fields if field.editable
               and (not field.__class__ == AutoField)]
user_field_names = [smart_str(field.name) for field in user_fields]
user_field_types = [field.__class__.__name__ for field in user_fields]
field_type_dict = dict(zip(user_field_names, user_field_types))
user_fields = None
user_field_types = None

profile_fields = [field for field in Profile._meta.fields if field.editable
                  and (not field.__class__ == AutoField)]
profile_field_names = [smart_str(field.name) for field in profile_fields]
profile_field_types = [field.__class__.__name__ for field in profile_fields]
field_type_dict.update(dict(zip(profile_field_names, profile_field_types)))
profile_fields = None
profile_field_types = None


def handle_uploaded_file(f, file_path):
    destination = default_storage.open(file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def get_user_import_settings(request, id):
    d = {}

    if id not in request.session:
        return d

    d['file_name'] = (request.session[id]).get('file_name', u'')
    d['interactive'] = request.session[id].get('interactive', False)
    d['override'] = request.session[id].get('override', False)
    d['key'] = request.session[id].get('key', u'')
    d['group'] = request.session[id].get('group', u'')
    d['clear_group_membership'] = request.session[id].get(
                                'clear_group_membership', False
                                )

    if d['override'] == "False":
        d['override'] = False

    if d['interactive'] == "False":
        d['interactive'] = False

    if d['override']:
        d['str_update'] = 'Override All Fields'
    else:
        d['str_update'] = 'Update Blank Fields'

    return d


def render_excel(filename, title_list, data_list, file_extension='.xls'):
    if file_extension == '.csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        csv_writer = csv.writer(response)

        csv_writer.writerow(title_list)

        for row_item_list in data_list:
            for i in range(0, len(row_item_list)):
                if row_item_list[i]:
                    if isinstance(row_item_list[i], datetime.datetime):
                        row_item_list[i] = row_item_list[i].strftime(
                                    '%Y-%m-%d %H:%M:%S'
                                    )
                    elif isinstance(row_item_list[i], datetime.date):
                        row_item_list[i] = row_item_list[i].strftime(
                                '%Y-%m-%d'
                                )
                    elif isinstance(row_item_list[i], datetime.time):
                        row_item_list[i] = row_item_list[i].strftime(
                            '%H:%M:%S'
                            )
            csv_writer.writerow(row_item_list)
    else:
        from io import BytesIO
        output = BytesIO()
        export_wb = Workbook()
        export_sheet = export_wb.add_sheet('Sheet1')
        col_idx = 0
        for col_title in title_list:
            export_sheet.write(0, col_idx, "%s" % col_title)
            col_idx += 1
        row_idx = 1
        for row_item_list in data_list:
            col_idx = 0
            for cell_value in row_item_list:
                if cell_value:
                    cell_value_is_date = False
                    if isinstance(cell_value, datetime.datetime):
                        cell_value = xlrd.xldate.xldate_from_datetime_tuple((
                            cell_value.year, cell_value.month,
                            cell_value.day, cell_value.hour,
                            cell_value.minute,
                            cell_value.second), 0)
                        cell_value_is_date = True
                    elif isinstance(cell_value, datetime.date):
                        cell_value = xlrd.xldate.xldate_from_date_tuple((
                            cell_value.year,
                            cell_value.month,
                            cell_value.day), 0)
                        cell_value_is_date = True
                    elif isinstance(cell_value, datetime.time):
                        cell_value = xlrd.xldate.xldate_from_time_tuple((
                                cell_value.hour,
                                cell_value.minute,
                                cell_value.second))
                        cell_value_is_date = True
                    elif isinstance(cell_value, models.Model):
                        cell_value = str(cell_value)
                    if cell_value_is_date:
                        s = XFStyle()
                        s.num_format_str = 'M/D/YY'
                        export_sheet.write(row_idx, col_idx, cell_value, s)
                    else:
                        export_sheet.write(row_idx, col_idx, cell_value)
                col_idx += 1
            row_idx += 1
        export_wb.save(output)
        output.seek(0)
        str_out = output.getvalue()
        response = HttpResponse(str_out)
        response['Content-Type']  = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    return response


def user_import_process(request, setting_dict, preview=True, id=''):
    """
    This function processes each row and store the data
    in the user_object_dict. Then it updates the database
    if preview=False.
    """
    key_list = setting_dict['key'].split(',')
    # key(s)- user field(s) or profile fields(s)? that is import to identify
    key_user_list = [key for key in key_list if key in user_field_names]
    key_profile_list = [key for key in key_list if key in profile_field_names]

    setting_dict['total'] = request.session[id].get('total',  0)
    setting_dict['count_insert'] = 0
    setting_dict['count_update'] = 0
    setting_dict['count_invalid'] = 0

    data_dict_list = request.session[id].get('data_dict_list',  [])
    data_dict_list_len = len(data_dict_list)

    user_obj_list = []
    invalid_list = []

    start = 0
    if not preview:
        finish = start + ROWS_TO_PROCESS
        if finish > data_dict_list_len:
            finish = data_dict_list_len
    else:
        finish = data_dict_list_len

    for r in range(start, finish):
        user_object_dict = {}
        if not preview:
            user_import_dict = {}
        identity_user_dict = {}  # used to look up the User
        identity_profile_dict = {}  # used to look up the Profile
        missing_keys = []

        data_dict = data_dict_list[r]

        missing_keys = [key for key in data_dict
                        if key in key_list
                        and data_dict[key] == '']

        for key in data_dict:
            user_object_dict[key] = data_dict[key]

            if key in key_list and data_dict[key] != '':
                if key in key_user_list:
                    identity_user_dict[key] = data_dict[key]
                if key in key_profile_list:
                    identity_profile_dict[key] = data_dict[key]

        user_object_dict['ROW_NUM'] = data_dict['ROW_NUM']

        if missing_keys:
            user_object_dict['ERROR'] = 'Missing key: %s.' % (
                            ', '.join(missing_keys))
            user_object_dict['IS_VALID'] = False
            setting_dict['count_invalid'] += 1
            if not preview:
                invalid_list.append({'ROW_NUM': user_object_dict['ROW_NUM'],
                                     'ERROR': user_object_dict['ERROR']})
        else:
            user_object_dict['IS_VALID'] = True

            # the keys could be the fields in both User and Profile tables
            user = get_user_by_key(identity_user_dict, identity_profile_dict)
            if user:
                if preview:
                    user_object_dict['ACTION'] = 'update'
                else:
                    user_import_dict['ACTION'] = 'update'
                setting_dict['count_update'] += 1

                if preview:
                    populate_user_dict(user, user_object_dict, setting_dict)
            else:
                #user = None
                if preview:
                    user_object_dict['ACTION'] = 'insert'
                else:
                    user_import_dict['ACTION'] = 'insert'
                setting_dict['count_insert'] += 1

            if not preview:
                user = do_user_import(request, user,
                                      user_object_dict,
                                      setting_dict)
                user_import_dict['user'] = user
                user_import_dict['ROW_NUM'] = user_object_dict['ROW_NUM']
                user_obj_list.append(user_import_dict)

        if preview:
            user_obj_list.append(user_object_dict)

    if not preview:
        if finish < data_dict_list_len:
            # not finished yet, store some data in the session
            count_insert = request.session[id].get('count_insert',  0) + \
            setting_dict['count_insert']
            count_update = request.session[id].get('count_update',  0) + \
            setting_dict['count_update']

            setting_dict['is_completed'] = False

            for r in range(start, finish):
                # remove those already processed rows
                data_dict_list.remove(data_dict_list[0])

            d = request.session[id]
            d.update({'is_completed': False,
                      'count_insert': count_insert,
                      'count_update': count_update,
                      'data_dict_list': data_dict_list})
            request.session[id] = d
        else:
            setting_dict['is_completed'] = True
            setting_dict['count_insert'] += request.session[id].get(
                                        'count_insert', 0)
            setting_dict['count_update'] += request.session[id].get(
                                            'count_update', 0)
            d = request.session[id]
            d.update({'is_completed': True})
            request.session[id] = d

    return user_obj_list, invalid_list


def get_user_by_key(identity_user_dict, identity_profile_dict):
    user = None

    if identity_user_dict and identity_profile_dict:
        users = User.objects.filter(**identity_user_dict)
        profiles = Profile.objects.filter(user__in=users).filter(
                        **identity_profile_dict
                        )
        if profiles:
            user = profiles[0].user
    elif identity_user_dict:
        users = User.objects.filter(**identity_user_dict)
        if users:
            user = users[0]
    else:
        profiles = Profile.objects.filter(**identity_profile_dict)
        if profiles:
            user = profiles[0].user

    return user


def do_user_import(request, user, user_object_dict, setting_dict):
    """
        the real work is here - do the insert or update
    """

    insert = not bool(user)  # insert or update
    user = user or User()  # existing or new user
    override = setting_dict['override']  # update ALL fields

    # insert/update user
    for field in user_field_names:
        if field == 'password' or field == 'username' or \
            (not insert and field in setting_dict['key']):
            continue
        if field in user_object_dict:
            if override:
                setattr(user, field, user_object_dict[field])
            else:
                # fill out the blank field only
                if getattr(user, field) == '':
                    setattr(user, field, user_object_dict[field])

    if insert:
        if 'username' in user_object_dict:  # set username
            user.username = user_object_dict['username']

        # generate if not username
        user.username = get_unique_username(user)

    if 'password' in user_object_dict and (insert or override):
        user.set_password(user_object_dict['password'])

    if not user.password:
        user.set_password(User.objects.make_random_password(length=8))

    user.is_active = bool(setting_dict['interactive'])

    if not bool(validate_email(user.email)):
        user.email = ''  # if not valid; empty it out

    # loop through user properties; truncate at max_length
    for key, value in user.__dict__.items():
        max_length = 90
        try:
            max_length = User._meta.get_field(key).max_length
        except FieldDoesNotExist:
            max_length = None
        if max_length:  # truncate per max_length field attribute
            setattr(user, key, value[:max_length])

    # username and email required
    if user.username and user.email:

        # insert/update record
        if insert:
            user.save(force_insert=True)
        else:
            user.save(force_update=True)

        try:  # get or create
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user,
               creator=request.user,
               creator_username=request.user.username,
               owner=request.user,
               owner_username=request.user.username,
            )

        for field in profile_field_names:
            if field in user_object_dict:

                if override:
                    setattr(profile, field, user_object_dict[field])
                else:
                    # fill out the blank field only
                    if getattr(profile, field) == '':
                        setattr(profile, field, user_object_dict[field])

        profile.save()

        # add to group
        if setting_dict['group']:
            try:
                gm = GroupMembership.objects.get(group=setting_dict['group'],
                                                 member=user)
            except GroupMembership.DoesNotExist:
                gm = GroupMembership()
                gm.member = user
                gm.group = setting_dict['group']
                gm.creator_id = request.user.id
                gm.creator_username = request.user.username
                gm.owner_id = request.user.id
                gm.owner_username = request.user.username
                gm.status = 1
                gm.status_detail = 'active'
                gm.save()

    return user


def get_unique_username(user):

    if not user.username:
        if user.email:
            user.username = user.email

    if not user.username:
        if user.first_name and user.last_name:
            user.username = '%s%s' % (user.first_name[0], user.last_name)

    p = re.compile(r'[^\w.@+-]+', re.IGNORECASE)
    user.username = p.sub('', user.username)

    # the maximum length of username is 150
    # truncate to 147 to leave some room to append more if needed.
    if len(user.username) > 147:
        user.username = user.username[:147]
    # check if this username already exists
    users = User.objects.filter(username__istartswith=user.username)

    if users:
        t_list = [u.username[len(user.username):] for u in users]
        num = 1
        while str(num) in t_list:
            num += 1
        user.username = '%s%s' % (user.username, str(num))

    return user.username


# populate user object to its dictionary, so we can display to the preview page
def populate_user_dict(user, user_dict, import_setting_list):
    if 'first_name' not in user_dict:
        user_dict['first_name'] = user.first_name
    if 'last_name' not in user_dict:
        user_dict['last_name'] = user.last_name
    if 'email' not in user_dict:
        user_dict['email'] = user.email
    if 'username' not in user_dict:
        user_dict['username'] = user.username
    if not import_setting_list['override']:
        if user.first_name:
            user_dict['first_name'] = user.first_name
        if user.last_name:
            user_dict['last_name'] = user.last_name
        if user.email:
            user_dict['email'] = user.email
        if user.username:
            user_dict['username'] = user.username
    if not user_dict['username']:
        user_dict['username'] = user.username


def get_header_list(file_path):
    if not os.path.isfile(file_path):
        raise NameError("%s is not a valid file." % file_path)

    header_list = []
    book = xlrd.open_workbook(file_path)
    sheet = book.sheet_by_index(0)
    for col in range(0, sheet.ncols):
        col_item = sheet.cell_value(rowx=0, colx=col)
        header_list.append(col_item)
    return header_list


def get_header_list_from_content(file_content, file_name):
    header_list = []
    if file_content and len(file_name) > 4:
        file_ext = file_name[-4:].lower()

        if file_ext == '.csv':
            line_return_index = file_content.find('\n')
            header_list = ((file_content[:line_return_index]
                            ).strip('\r')).split(',')
        else:
            book = xlrd.open_workbook(file_contents=file_content)
            nsheets = book.nsheets
            for i in range(0, nsheets):
                sh = book.sheet_by_index(i)
                for c in range(0, sh.ncols):
                    col_item = sh.cell_value(rowx=0, colx=c)
                    header_list.append(col_item)
    return header_list


def extract_from_excel(file_path):
    if not default_storage.exists(file_path):
        raise NameError("%s is not a valid file." % file_path)

    file_ext = (file_path[-4:]).lower()
    if file_ext != '.csv' and file_ext != '.xls':
        raise NameError(
    "%s is not a valid file type (should be either .csv or .xls)." % file_path
        )

    fields = []
    data_list = []

    if file_ext == '.csv':
        import csv
        import dateutil.parser as dparser

        normalize_newline(file_path)
        data = csv.reader(default_storage.open(file_path, 'rU'))

        # read the column header
        fields = next(data)
        fields = [smart_str(field) for field in fields]

        r = 1
        for row in data:
            item = dict(zip(fields, row))
            for key in item:
                if key in field_type_dict and \
                field_type_dict[key] == 'DateTimeField':
                    item[key] = dparser.parse(item[key])
            item['ROW_NUM'] = r + 1
            data_list.append(item)
            r += 1
    else:
        book = xlrd.open_workbook(file_path)
        nsheets = book.nsheets
        nrows = book.sheet_by_index(0).nrows

        # get the fields from the first row
        for i in range(0, nsheets):
            sh = book.sheet_by_index(i)
            for c in range(0, sh.ncols):
                col_item = sh.cell_value(rowx=0, colx=c)
                fields.append(smart_str(col_item))

        # get the data - skip the first row
        for r in  range(1, nrows):
            row = []
            for i in range(0, nsheets):
                sh = book.sheet_by_index(i)
                for c in range(0, sh.ncols):
                    cell = sh.cell(r, c)
                    cell_value = cell.value
                    if cell.ctype == xlrd.XL_CELL_DATE:
                        date_tuple = xlrd.xldate_as_tuple(
                                        cell_value, book.datemode)
                        cell_value = datetime.date(date_tuple[0],
                                                   date_tuple[1],
                                                    date_tuple[2])
                    elif cell.ctype in (2, 3) \
                        and int(cell_value) == cell_value:
                        # so for zipcode 77079,
                        # we don't end up with 77079.0
                        cell_value = int(cell_value)
                    row.append(cell_value)

            item = dict(zip(fields, row))
            item['ROW_NUM'] = r + 1
            data_list.append(item)

    return data_list
