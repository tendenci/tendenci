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

from perms.utils import has_perm, is_admin
from memberships.models import AppField, Membership, MembershipType
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

def csv_to_dict(file_path):
    """
    Returns a list of dicts. Each dict represents record.
    """
    csv_file = csv.reader(open(file_path, 'rU'))
    col = csv_file.next()
    lst = []

    try:
        for row in csv_file:
            entry = {}
            for i in xrange(len(col)):
                entry[col[i]] = row[i].decode('latin-1')
            lst.append(entry)
    except csv.Error as e:
        # NULL byte error
        # stop everything; return empty list
        # Empty list will raise an error msg
        # this can typically be corrected by
        # saving the file as a .csv
        return []

    return lst  # list of dictionaries

def is_import_valid(file_path):
    """
    Run import file against required files
    'username' and 'membership-type' are required fields
    """
    memberships = csv_to_dict(file_path)  # list of membership dicts
    membership_keys = [slugify(m) for m in memberships[0].keys()]
    #required = ('username','membership-type')
    #there is no username in the export at the moment.
    required = ('membership-type',)
    requirements = [r in membership_keys for r in required]

    return all(requirements)
    
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

