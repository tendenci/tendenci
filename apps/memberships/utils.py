import os
import sys
import csv
from dateutil.parser import parse as dt_parse
from datetime import datetime, date, timedelta

from django.conf import settings
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models import Q

from perms.utils import has_perm, is_admin
from memberships.models import (App, AppField, AppEntry, Membership,
    MembershipType)
from corporate_memberships.models import CorporateMembership


def get_default_membership_fields(use_for_corp=False):
    json_file_path = os.path.join(settings.PROJECT_ROOT,
        'apps/memberships/fixtures/default_membership_application_fields.json')
    json_file = open(json_file_path, 'r')
    data = ''.join(json_file.read())
    json_file.close()
    
    field_list = simplejson.loads(data)
    
    # add default fields for corp. individuals
    if use_for_corp:
        corp_field_list = get_default_membership_corp_fields()
    else:
        corp_field_list = None
        
    if field_list:
        if corp_field_list:
            field_list = field_list + corp_field_list
    else:
        field_list = corp_field_list

    
    return field_list

def get_default_membership_corp_fields():
    json_file_path = os.path.join(settings.PROJECT_ROOT,
        'apps/memberships/fixtures/default_membership_application_fields_for_corp.json')
    json_file = open(json_file_path, 'r')
    data = ''.join(json_file.read())
    json_file.close()
    
    corp_field_list = simplejson.loads(data)
    
    return corp_field_list

def edit_app_update_corp_fields(app):
    """
    Update the membership application's corporate membership fields (corporate_membership_id)
    when editing a membership application.
    """
    if app:
        try:  
            app_field = AppField.objects.get(app=app, field_type='corporate_membership_id')
            if not app.use_for_corp:
                if not hasattr(app, 'corp_app'):
                    app_field.delete()
                else:
                    app.use_for_corp = 1
                    app.save()
        except AppField.DoesNotExist:
            if app.use_for_corp:
                field_list = get_default_membership_corp_fields()
                for field in field_list:
                    field.update({'app':app})
                    AppField.objects.create(**field)

def get_corporate_membership_choices():
    cm_list = [(0, 'SELECT ONE')]
    from django.db import connection
    # use the raw sql because we cannot import CorporateMembership in the memberships app
    cursor = connection.cursor()
    cursor.execute("""
                SELECT id, name 
                FROM corporate_memberships_corporatemembership 
                WHERE status=1 AND status_detail='active' 
                ORDER BY name """ ) 
    account_numbers = []
    for row in cursor.fetchall():
        cm_list.append((row[0], row[1]))
    
    return cm_list

def has_null_byte(file_path):
    f = open(file_path, 'r')
    data = f.read()
    f.close()
    return ('\0' in data)

def csv_to_dict(file_path, **kwargs):
    """
    Returns a list of dicts. Each dict represents record.
    """
    machine_name = kwargs.get('machine_name', False)

    # null byte; assume xls; not csv
    if has_null_byte(file_path):
        return []

    csv_file = csv.reader(open(file_path, 'rU'))
    colnames = csv_file.next()  # row 1;

    if machine_name:
        colnames = [slugify(c).replace('-','') for c in colnames]

    cols = xrange(len(colnames))
    lst = []

    for row in csv_file:
        entry = {}
        rows = len(row)-1
        for col in cols:
            if col > rows:
                break  # go to next row
            entry[colnames[col]] = row[col]
        lst.append(entry)

    return lst  # list of dictionaries

def is_import_valid(file_path):
    """
    Returns a 2-tuple containing a booelean and list of errors

    The import file must be of type .csv and and include
    a membership type column.
    """
    errs = []
    ext = os.path.splitext(file_path)[1]

    if ext != '.csv':
        errs.append("Pleaes make sure you're importing a .csv file.")
        return False, errs

    if has_null_byte(file_path):
        errs.append('This .csv file has null characters, try re-saving it.')
        return False, errs

    # get header column
    f = open(file_path, 'r')
    row = f.readline()
    f.close()

    headers = [slugify(r).replace('-','') for r in row.split(',')]

    required = ('membershiptype',)
    requirements_met = [r in headers for r in required]

    if all(requirements_met):
        return True, []
    else:
        return False, ['Please make sure there is a membership type column.']
    
def count_active_memberships(date):
    """
    Counts all active memberships in a given date
    """
    mems = Membership.objects.filter(
                create_dt__lte=date,
                expire_dt__gt=date,
            )
    count = mems.count()

    return count

def prepare_chart_data(days, height=300):
    """
    Creates a list of tuples of a day and membership count per day.
    """
    
    data = []
    max_count = 0
    
    #append mem count per day
    for day in days:
        count = count_active_memberships(day)
        if count > max_count:
            max_count = count
        data.append({
                'day':day,
                'count':count,
            })
    
    # normalize height
    try:
        kH = height*1.0/max_count
    except Exception:
        kH = 1.0
    for d in data:
        d['height'] = int(d['count']*kH)
        
    return data

def month_days(year, month):
    "Returns iterator for days in selected month"
    day = date(year, month, 1)
    while day.month == month:
        yield day
        day += timedelta(days=1) 

def get_days(request):
    "returns a list of days in a month"
    now = date.today()
    year = int(request.GET.get('year') or str(now.year))
    month = int(request.GET.get('month') or str(now.month))
    days = list(month_days(year, month)) 
    return days

def has_app_perm(user, perm, obj=None):
    """
    Wrapper for perm's has_perm util.
    This consider's the app's status_detail
    """
    allow = has_perm(user, perm, obj)
    if is_admin(user):
        return allow
    if obj.status_detail != 'published':
        return allow
    else:
        return False

def get_over_time_stats():
    """
    Returns membership statistics over time.
        Last Month 
        Last 3 Months 
        Last 6 Months 
        Last 9 Months 
        Last 12 Months
        Year to Date
    """
    today = date.today()
    year = datetime(day=1, month=1, year=today.year)
    times = [
        ("Last Month", months_back(1), 1),
        ("Last 3 Months", months_back(3), 2),
        ("Last 6 Months", months_back(6), 3),
        ("Last 9 Months", months_back(9), 4),
        ("Last 12 Months", months_back(12), 5),
        ("Year to Date", year, 5),
    ]

    stats = []
    for time in times:
        start_dt = time[1]
        d = {}
        active_mems = Membership.objects.filter(expire_dt__gt=start_dt)
        d['new'] = active_mems.filter(subscribe_dt__gt=start_dt).count() #just joined in that time period
        d['renewing'] = active_mems.filter(renewal=True).count()
        d['active'] = active_mems.count()
        d['time'] = time[0]
        d['start_dt'] = start_dt
        d['end_dt'] = today
        d['order'] = time[2]
        stats.append(d)

    return sorted(stats, key=lambda x:x['order'])

def months_back(n):
    """Return datetime minus n months"""
    from dateutil.relativedelta import relativedelta

    return date.today() + relativedelta(months=-n)

def get_status_filter(status):
    if status == "pending":
        return Q(is_approved=None)
    elif status == "approved":
        return Q(is_approved=True)
    elif status == "disapproved":
        return Q(is_approved=False)
    else:
        return Q()

def get_app_field_labels(app):
    """Get a list of field labels for this app.
    """
    labels_list = []
    fields = app.fields.all().order_by('position')
    for field in fields:
        labels_list.append(field.label)
        
    return labels_list

def get_notice_token_help_text(notice=None):
    """Get the help text for how to add the token in the email content,
        and display a list of available token.
    """
    help_text = ''
    if notice and notice.membership_type:
        membership_types = [notice.membership_type]
    else:
        membership_types = MembershipType.objects.filter(status=1, status_detail='active')
    
    # get a list of apps from membership types
    apps_list = []    
    for mt in membership_types:
        apps = App.objects.filter(membership_types=mt)
        if apps:
            apps_list.extend(apps)
            
    apps_list = set(apps_list)
    apps_len = len(apps_list)
     
    # render the tokens
    help_text += '<div style="margin: 1em 10em;">'
    help_text += """
                <div style="margin-bottom: 1em;">
                You can use tokens to display member info or site specific information.
                A token is composed of a field label or label lower case with underscore (_)
                instead of spaces, wrapped in 
                {{ }} or [ ]. <br />
                For example, token for "First Name" field: {{ first_name }}
                </div> 
                """
                
    help_text += '<div id="toggle_token_view"><a href="javascript:;">Click to view available tokens</a></div>'
    help_text += '<div id="notice_token_list">'
    if apps_list: 
        for app in apps_list:
            if apps_len > 1:
                help_text += '<div style="font-weight: bold;">%s</div>' % app.name
            labels_list = get_app_field_labels(app)
            help_text += "<ul>"
            for label in labels_list:
                help_text += '<li>{{ %s }}</li>' % slugify(label).replace('-', '_')
            help_text += "</ul>"
    else:
        help_text += '<div>No field tokens because there is no applications.</div>'
            
    other_labels = ['membernumber',
                    'membershiptype',
                    'membershiplink',
                    'renewlink',
                    'expirationdatetime',
                    'sitecontactname',
                    'sitecontactemail',
                    'sitedisplayname',
                    'timesubmitted'
                    ]
    help_text += '<div style="font-weight: bold;">Non-field Tokens</div>'
    help_text += "<ul>"
    for label in other_labels:
        help_text += '<li>{{ %s }}</li>' % label
    help_text += "</ul>"
        
    help_text += "</div>"
         
        
    help_text += "</div>"
    
    help_text += """
                <script>
                    $(document).ready(function() {
                        $('#notice_token_list').hide();
                         $('#toggle_token_view').click(function () {
                        $('#notice_token_list').toggle();
                         });
                    });
                </script>
                """
              
    return help_text


def spawn_username(*args):
    """
    Join arguments to create username [string].
    Find similiar usernames; auto-increment newest username.
    Return new username [string].
    """
    if not args:
        raise Exception('spawn_username() requires atleast 1 argument; 0 were given')

    import re

    max_length = 8

    un = ' '.join(args)             # concat args into one string
    un = re.sub('\s+','_',un)       # replace spaces w/ underscores
    un = re.sub('[^\w.-]+','',un)   # remove non-word-characters
    un = un.strip('_.- ')           # strip funny-characters from sides
    un = un[:max_length].lower()    # keep max length and lowercase username

    others = [] # find similiar usernames
    for u in User.objects.filter(username__startswith=un):
        if u.username.replace(un, '0').isdigit():
            others.append(int(u.username.replace(un,'0')))

    if others and 0 in others:
        # the appended digit will compromise the username length
        # there would have to be more than 99,999 duplicate usernames
        # to kill the database username max field length
        un = '%s%s' % (un, str(max(others)+1))

    return un.lower()

def get_user(**kwargs):
    """
    Get user via single keyword argument.
    Example: get_user(username=username)
    Only works with unique fields e.g. id, username
    """
    for k, v in kwargs.items():

        try:
            user = User.objects.get(**{k:v})
        except User.MultipleObjectsReturned:
            user = User.objects.filter(**{k:v})[0]
        except User.DoesNotExist:
            user = None

        if user:
            break  # get out of for loop

    return user

def get_membership_stats():
    now = datetime.now()
    summary = []
    types = MembershipType.objects.all()
    total_active = 0
    total_pending = 0
    total_expired = 0
    total_total = 0
    for mem_type in types:
        mems = Membership.objects.filter(membership_type = mem_type)
        active = mems.filter(status_detail='active', expire_dt__gt=now)
        expired = mems.filter(status_detail='active', expire_dt__lte=now)
        pending = AppEntry.objects.filter(app__membership_types=mem_type, is_approved__isnull=True)
        total_all = active.count() + pending.count() + expired.count()
        total_active += active.count()
        total_pending += pending.count()
        total_expired += expired.count()
        total_total += total_all
        summary.append({
            'type':mem_type,
            'active':active.count(),
            'pending':pending.count(),
            'expired':expired.count(),
            'total':total_all,
        })
    
    return (sorted(summary, key=lambda x:x['type'].name),
        (total_active, total_pending, total_expired, total_total))
