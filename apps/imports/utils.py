import os
import datetime
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponse

import xlrd
from xlwt import Workbook, XFStyle

from user_groups.models import Group, GroupMembership
from profiles.models import Profile

def handle_uploaded_file(f, file_path):
    destination = open(file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    
def get_user_import_settings(request):
    d = {}
    d['file_name'] = request.session['file_name']
    d['interactive'] = request.session['interactive']
    d['override'] = request.session['override']
    d['key'] = request.session['key']
    d['group'] = request.session['group']
    d['clear_group_membership'] = request.session['clear_group_membership']
    
    try:
        d['interactive'] = int(d['interactive'])
        if d['interactive'] == 1:
            d['interactive'] = True
        else:
            d['interactive'] = False
    except:
        d['interactive'] = False
        
    try:
        d['override'] = int(d['override'])
        if d['override'] == 1:
            d['override'] = True
        else:
            d['override'] = False
    except:
        d['override'] = False
    if d['override']:
        d['str_update'] = 'Override All Fields'
    else:
        d['str_update'] = 'Update Blank Fields'
        
    try:
        d['clear_group_membership'] = int(d['clear_group_membership'])
        if d['clear_group_membership'] == 1:
            d['clear_group_membership'] = True
        else:
            d['clear_group_membership'] = False
    except:
        d['clear_group_membership'] = False
    
            
    return d

def render_excel(filename, col_title_list, data_row_list):
    import StringIO
    output = StringIO.StringIO()
    export_wb = Workbook()
    export_sheet = export_wb.add_sheet('Sheet1')
    col_idx = 0
    for col_title in col_title_list:
        export_sheet.write(0, col_idx, col_title)
        col_idx += 1
    row_idx = 1
    for row_item_list in data_row_list:
        col_idx = 0
        for current_value in row_item_list:
            if current_value:
                current_value_is_date = False
                if isinstance(current_value, datetime.datetime):
                    current_value = xlrd.xldate.xldate_from_datetime_tuple((current_value.year, current_value.month, \
                                                    current_value.day, current_value.hour, current_value.minute, \
                                                    current_value.second), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.date):
                    current_value = xlrd.xldate.xldate_from_date_tuple((current_value.year, current_value.month, \
                                                    current_value.day), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.time):
                    current_value = xlrd.xldate.xldate_from_time_tuple((current_value.hour, current_value.minute, \
                                                    current_value.second))
                    current_value_is_date = True
                elif isinstance(current_value, models.Model):
                    current_value = str(current_value)
                if current_value_is_date:
                    s = XFStyle()
                    s.num_format_str = 'M/D/YY'
                    export_sheet.write(row_idx, col_idx, current_value, s)
                else:
                    export_sheet.write(row_idx, col_idx, current_value)
            col_idx += 1
        row_idx += 1
    export_wb.save(output)
    output.seek(0)
    response = HttpResponse(output.getvalue())
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response

def user_import_process(request, setting_dict, preview=True):
    file_path = os.path.join(setting_dict['file_dir'], setting_dict['file_name'])
    
    # get a list of headers from the spread sheet
    import_header_list = get_header_list(file_path)
    
    book = xlrd.open_workbook(file_path)
    sheet = book.sheet_by_index(0)
    key_list = setting_dict['key'].split(',')
    setting_dict['total'] = sheet.nrows - 1
    setting_dict['count_insert'] = 0
    setting_dict['count_update'] = 0
    setting_dict['count_invalid'] = 0
    
    user_obj_list = []
    
    if not preview:
        #reset group - delete all members in the group
        if setting_dict['clear_group_membership'] and setting_dict['group']:
            GroupMembership.objects.filter(group=setting_dict['group']).delete()
        
    
    for r in  range(1, sheet.nrows):
        user_object_dict = {}
        if not preview:
            user_import_dict = {}
        identity_dict = {} # used to look up the database
        missing_keys = []
        
        for c in range(0, sheet.ncols):
            field_name = import_header_list[c]
            cell = sheet.cell(r, c)
            cell_value = cell.value
            if cell.ctype == xlrd.XL_CELL_DATE:
                date_tuple = xlrd.xldate_as_tuple(cell_value, book.datemode)
                cell_value = datetime.date(date_tuple[0],date_tuple[1],date_tuple[2])
            elif cell.ctype in (2,3) and int(cell_value) == cell_value:
                # so for zipcode 77079, we don't end up with 77079.0
                cell_value = int(cell_value)
            
            user_object_dict[field_name] = cell_value
            if field_name in key_list:
                if cell_value <> '':
                    identity_dict[field_name] = cell_value
                else:
                    missing_keys.append(field_name)
        
        user_object_dict['ROW_NUM'] = r + 1  
            
        if missing_keys:
            user_object_dict['ERROR'] = 'Missing key: %s.' % (', '.join(missing_keys))
            user_object_dict['IS_VALID'] = False
            setting_dict['count_invalid'] += 1
        else:
            user_object_dict['IS_VALID'] = True
            try:
                # TODO: the keys could be the fields in both User and Profile tables, deal with it
                user = User.objects.get(**identity_dict)
                if preview:
                    user_object_dict['ACTION'] = 'update'
                else:
                    user_import_dict['ACTION'] = 'update'
                setting_dict['count_update'] += 1
                
                if preview:
                    populate_user_dict(user, user_object_dict, setting_dict)
            except User.DoesNotExist:
                user = None
                if preview:
                    user_object_dict['ACTION'] = 'insert'
                else:
                    user_import_dict['ACTION'] = 'insert'
                setting_dict['count_insert'] += 1
                
            if not preview:
                user = do_user_import(request, user, user_object_dict, setting_dict)
                user_import_dict['user'] = user
                user_obj_list.append(user_import_dict)
                
        if preview:
            user_obj_list.append(user_object_dict)
                
    return user_obj_list

def do_user_import(request, user, user_object_dict, setting_dict):
    """
        the real work is here - do the insert or update
    """
    from django.db.models.fields import AutoField
    
    if not user:
        user = User()
        insert = True
    else:
        insert = False
    override = setting_dict['override'] # if True, update all fields, otherwise, update blank field
    user_field_names = [field.name for field in User._meta.fields if field.editable and (not field.__class__==AutoField)]
    profile_field_names = [field.name for field in Profile._meta.fields if field.editable and (not field.__class__==AutoField)]
    
    # insert/update user
    for field in user_field_names:
        if field == 'password' or field == 'username' or (not insert and field in setting_dict['key']):
            continue
        if user_object_dict.has_key(field):
            if override:
                setattr(user, field, user_object_dict[field])
            else:
                # fill out the blank field only
                if getattr(user, field) == '':
                    setattr(user, field, user_object_dict[field])
                    
    if insert:
        if user_object_dict.has_key('username') and user_object_dict['username']:
            user.username = user_object_dict['username']
            
        # generate the unique username
        get_unique_username(user)
        
    if user_object_dict.has_key('password') and user_object_dict['password'] and (override or insert):
        # override the password, then hash the password
        #user.password = user_object_dict['password']
        user.set_password(user_object_dict['password'])
        
    if not user.password:
        #user.password = User.objects.make_random_password(length=8)
        user.set_password(User.objects.make_random_password(length=8))
            
    if setting_dict['interactive']:
        user.is_active = 1
    else:
        user.is_active = 0
        
    user.save()
    
    # insert/update profile
    try:
        profile = user.get_profile()
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user, 
                           creator=request.user, 
                           creator_username=request.user.username,
                           owner=request.user, 
                           owner_username=request.user.username, 
                           email=user.email)
        
    for field in profile_field_names:
        if user_object_dict.has_key(field):
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
            gm = GroupMembership.objects.get(group=setting_dict['group'], member=user)
        except GroupMembership.DoesNotExist:
            gm = GroupMembership()
            gm.member = user
            gm.group = setting_dict['group']
            gm.creator_id = request.user.id
            gm.creator_username = request.user.username
            gm.owner_id =  request.user.id
            gm.owner_username = request.user.username
            gm.status =1
            gm.status_detail = 'active'
            gm.save()
    
    return user

def get_unique_username(user):
    if not user.username:
        if user.email:
            user.username = user.email
    if not user.username:
        if user.first_name and user.last_name:
            user.username = '%s%s' % (user.first_name, user.last_name)
    if not user.username:
        user.username = str(uuid.uuid1())[:8]
        
    # check if this username already exists
    users = User.objects.filter(username__startswith=user.username)
    
    if users:
        t_list = [u.username[len(user.username):] for u in users]
        num = 1
        while str(num) in t_list:
            num += 1
            
        user.username = '%s%s' % (user.username, str(num))
   
    return user.username
                     

# populate user object to its dictionary, so we can display to the preview page
def populate_user_dict(user, user_dict, import_setting_list):
    if not user_dict.has_key('first_name'):
        user_dict['first_name'] = user.first_name
    if not user_dict.has_key('last_name'):
        user_dict['last_name'] = user.last_name
    if not user_dict.has_key('email'):
        user_dict['email'] = user.email
    if not user_dict.has_key('username'):
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
        raise NameError, "%s is not a valid file." % file_path
    header_list = []
    book = xlrd.open_workbook(file_path)
    sheet = book.sheet_by_index(0)
    for col in range(0, sheet.ncols):
        col_item = sheet.cell_value(rowx=0, colx = col)
        header_list.append(col_item)
    return header_list
        
 
    