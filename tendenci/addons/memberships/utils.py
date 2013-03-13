import os
import csv
import re
from decimal import Decimal
from datetime import datetime, date, timedelta, time
import dateutil.parser as dparser
import pytz
from sets import Set
import time as ttime

from django.http import Http404, HttpResponseServerError
from django.conf import settings
from django.utils import simplejson
from django.contrib.auth.models import User
from django.template import loader
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core import exceptions
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str
from django.db.models.fields import AutoField
from django.db.models import ForeignKey, OneToOneField

from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import has_perm
from tendenci.addons.memberships.models import (App,
                                                AppField,
                                                AppEntry,
                                                Membership,
                                                MembershipType,
                                                MembershipDefault,
                                                MembershipDemographic,
                                                MembershipApp,
                                                MembershipAppField)
from tendenci.core.base.utils import normalize_newline
from tendenci.apps.profiles.models import Profile
from tendenci.apps.profiles.utils import make_username_unique
from tendenci.core.payments.models import PaymentMethod
from tendenci.apps.entities.models import Entity


def get_default_membership_fields(use_for_corp=False):
    json_file_path = os.path.join(settings.TENDENCI_ROOT,
        'addons/memberships/fixtures/default_membership_application_fields.json')
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
    json_file_path = os.path.join(settings.TENDENCI_ROOT,
        'addons/memberships/fixtures/default_membership_application_fields_for_corp.json')
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
                    field.update({'app': app})
                    AppField.objects.create(**field)


def get_corporate_membership_choices():
    cm_list = [(0, 'SELECT ONE')]
    from django.db import connection
    # use the raw sql because we cannot import CorporateMembership
    # in the memberships app
    cursor = connection.cursor()
    cursor.execute(
        """SELECT cm.id, cp.name
        FROM corporate_memberships_corpmembership cm
        INNER JOIN corporate_memberships_corpprofile cp
        ON cm.corp_profile_id=cp.id
        WHERE cm.status=True AND cm.status_detail='active'
        ORDER BY cp.name"""
    )

    for row in cursor.fetchall():
        cm_list.append((row[0], row[1]))

    return cm_list


def get_membership_type_choices(user, membership_app, renew=False,
                                corp_membership=None):
    mt_list = []
    # show only the membership type assiciated with this corp_membership
    # when joining under a corporation.
    if corp_membership:
        membership_types = [corp_membership.corporate_membership_type.membership_type]
    else:
        membership_types = membership_app.membership_types.all()
        if not user or not user.profile.is_superuser:
            membership_types = membership_types.filter(admin_only=False)
        membership_types = membership_types.order_by('position')

    currency_symbol = get_setting("site", "global", "currencysymbol")

    for mt in membership_types:
        if not renew:
            if mt.admin_fee:
                price_display = '%s - %s%0.2f (+ %s%s admin fee )' % (
                                              mt.name,
                                              currency_symbol,
                                              mt.price,
                                              currency_symbol,
                                              mt.admin_fee)
            else:
                price_display = '%s - %s%0.2f' % (mt.name,
                                                  currency_symbol,
                                                  mt.price)
        else:
            price_display = '%s - %s%0.2f' % (mt.name,
                                              currency_symbol,
                                              mt.renewal_price)

        price_display = mark_safe(price_display)
        mt_list.append((mt.id, price_display))

    return mt_list


def get_selected_demographic_fields(membership_app, forms):
    """
    Get the selected demographic fields for the app.
    """
    demographic_field_dict = dict([(field.name, field) \
                        for field in MembershipDemographic._meta.fields \
                        if field.get_internal_type() != 'AutoField'])
    demographic_field_names = demographic_field_dict.keys()
    app_fields = MembershipAppField.objects.filter(
                                membership_app=membership_app,
                                display=True
                                ).values(
                        'label', 'field_name', 'required')
    selected_fields = []
    for app_field in app_fields:
        if app_field['field_name'] in demographic_field_names:
            field = forms.CharField(
                    widget=forms.TextInput({'size': 30}),
                    label=app_field['label'],
                    required=app_field['required'])
            selected_fields.append((app_field['field_name'], field))
    return selected_fields


def get_selected_demographic_field_names(membership_app=None):
    """
    Get the selected demographic field names.
    """
    if not membership_app:
        membership_app = MembershipApp.objects.current_app()
    demographic_field_names = [field.name \
                        for field in MembershipDemographic._meta.fields \
                        if field.get_internal_type() != 'AutoField']
    app_field_names = MembershipAppField.objects.filter(
                                membership_app=membership_app,
                                display=True
                                ).values_list('field_name', flat=True)
    selected_field_names = []
    for field_name in app_field_names:
        if field_name in demographic_field_names:
            selected_field_names.append(field_name)
    return selected_field_names


def membership_rows(user_field_list,
                    profile_field_list,
                    demographic_field_list,
                    membership_field_list,
                    foreign_keys,
                    export_status_detail=''):
    # grab all except the archived
    memberships = MembershipDefault.objects.filter(
                                status=True
                                ).exclude(
                                status_detail='archive'
                                )
    if export_status_detail:
        if export_status_detail == 'pending':
            memberships = memberships.filter(
                        status_detail__icontains='pending'
                                )
        else:
            memberships = memberships.filter(
                        status_detail=export_status_detail)

    for membership in memberships:
        row_dict = {}
        user = membership.user
        [profile] = Profile.objects.filter(user=user)[:1] or [None]
        [demographic] = MembershipDemographic.objects.filter(user=user)[:1] or [None]

        for field_name in user_field_list:
            row_dict[field_name] = get_obj_field_value(field_name, user)
        if profile:
            for field_name in profile_field_list:
                row_dict[field_name] = get_obj_field_value(
                                                field_name, profile,
                                                field_name in foreign_keys)
        if demographic:
            for field_name in demographic_field_list:
                row_dict[field_name] = get_obj_field_value(
                                                field_name, demographic,
                                                field_name in foreign_keys)
        for field_name in membership_field_list:
            row_dict[field_name] = get_obj_field_value(
                                            field_name, membership,
                                            field_name in foreign_keys)

        yield row_dict


def get_obj_field_value(field_name, obj, is_foreign_key=False):
    value = getattr(obj, field_name)
    if value and is_foreign_key:
        value = value.id
    return value


def process_export(export_type='all_fields',
                   export_status_detail='active',
                   identifier=''):
    from tendenci.core.perms.models import TendenciBaseModel
    if export_type == 'main_fields':
        base_field_list = []
        user_field_list = ['first_name', 'last_name', 'username',
                           'email', 'is_active', 'is_staff',
                           'is_superuser']
        profile_field_list = ['member_number', 'company',
                              'phone', 'address',
                              'address2', 'city',
                              'state', 'zipcode',
                              'country']
        demographic_field_list = []
        membership_field_list = ['membership_type',
                                 'corp_profile_id',
                                 'corporate_membership_id',
                                 'join_dt',
                                 'expire_dt',
                                 'renewal',
                                 'renew_dt',
                                 'status',
                                 'status_detail'
                                 ]
    else:
        base_field_list = [smart_str(field.name) for field \
                           in TendenciBaseModel._meta.fields \
                         if not field.__class__ == AutoField]
        user_field_list = [smart_str(field.name) for field \
                           in User._meta.fields \
                         if not field.__class__ == AutoField]
        # remove password
        user_field_list.remove('password')
        profile_field_list = [smart_str(field.name) for field \
                           in Profile._meta.fields \
                         if not field.__class__ == AutoField]
        profile_field_list = [name for name in profile_field_list \
                                   if not name in base_field_list]
        profile_field_list.remove('guid')
        profile_field_list.remove('user')
        demographic_field_list = [smart_str(field.name) for field \
                           in MembershipDemographic._meta.fields \
                         if not field.__class__ == AutoField]
        demographic_field_list.remove('user')
        membership_field_list = [smart_str(field.name) for field \
                           in MembershipDefault._meta.fields \
                         if not field.__class__ == AutoField]
        membership_field_list.remove('user')

    title_list = user_field_list + profile_field_list + \
        membership_field_list + demographic_field_list + \
        base_field_list

    # list of foreignkey fields
    if export_type == 'main_fields':
        fks = ['membership_type']
    else:
        user_fks = [field.name for field in User._meta.fields \
                       if isinstance(field, (ForeignKey, OneToOneField))]
        profile_fks = [field.name for field in Profile._meta.fields \
                       if isinstance(field, (ForeignKey, OneToOneField))]
        demographic_fks = [field.name for field in MembershipDemographic._meta.fields \
                       if isinstance(field, (ForeignKey, OneToOneField))]
        membership_fks = [field.name for field in MembershipDefault._meta.fields \
                    if isinstance(field, (ForeignKey, OneToOneField))]

        fks = Set(user_fks + profile_fks + demographic_fks + membership_fks)

    if not identifier:
        identifier = int(ttime.time())
    file_name_temp = 'export/memberships/%s_temp.csv' % identifier
    with default_storage.open(file_name_temp, 'wb') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(title_list)
        # corp_membership_rows is a generator - for better performance
        for row_dict in membership_rows(user_field_list,
                                        profile_field_list,
                                        demographic_field_list,
                                        membership_field_list,
                                        fks,
                                        export_status_detail):
            items_list = []
            for field_name in title_list:
                item = row_dict.get(field_name)
                if item is None:
                    item = ''
                if item:
                    if isinstance(item, datetime):
                        item = item.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(item, date):
                        item = item.strftime('%Y-%m-%d')
                    elif isinstance(item, time):
                        item = item.strftime('%H:%M:%S')
                    elif isinstance(item, basestring):
                        item = item.encode("utf-8")
                items_list.append(item)
            csv_writer.writerow(items_list)
    # rename the file name
    file_name = 'export/memberships/%s.csv' % identifier
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))
    # delete the temp file
    default_storage.delete(file_name_temp)


def has_null_byte(file_path):
    f = default_storage.open(file_path, 'r')
    data = f.read()
    f.close()
    return ('\0' in data)


def csv_to_dict(file_path, **kwargs):
    """
    Returns a list of dicts. Each dict represents a row.
    """
    machine_name = kwargs.get('machine_name', False)

    # null byte; assume xls; not csv
    if has_null_byte(file_path):
        return []

    normalize_newline(file_path)
    csv_file = csv.reader(default_storage.open(file_path, 'rU'))
    colnames = csv_file.next()  # row 1;

    if machine_name:
        colnames = [slugify(c).replace('-', '') for c in colnames]

    cols = xrange(len(colnames))
    lst = []

    # make sure colnames are unique
    duplicates = {}
    for i in cols:
        for j in cols:
            # compare with previous and next fields
            if i != j and colnames[i] == colnames[j]:
                number = duplicates.get(colnames[i], 0) + 1
                duplicates[colnames[i]] = number
                colnames[j] = colnames[j] + "-" + str(number)

    for row in csv_file:
        entry = {}
        rows = len(row) - 1
        for col in cols:
            if col > rows:
                break  # go to next row
            entry[colnames[col]] = row[col].strip()
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
    f = default_storage.open(file_path, 'r')
    row = f.readline()
    f.close()

    headers = [slugify(r).replace('-', '') for r in row.split(',')]

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
    return MembershipDefault.objects.filter(
        status=True,
        status_detail='active',
        create_dt__lte=date,
        expire_dt__gt=date,
    ).count()


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
            'day': day,
            'count': count,
        })

    # normalize height
    try:
        kH = height * 1.0 / max_count
    except Exception:
        kH = 1.0
    for d in data:
        d['height'] = int(d['count'] * kH)

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
    if user.profile.is_superuser:
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
        active_mems = MembershipDefault.objects.filter(
            status=True, status_detail='active')
        active_mems = active_mems.filter(expire_dt__gt=start_dt)
        d['new'] = active_mems.filter(join_dt__gt=start_dt).count()  # just joined in that time period
        d['renewing'] = active_mems.filter(renewal=True).count()
        d['active'] = active_mems.count()
        d['time'] = time[0]
        d['start_dt'] = start_dt
        d['end_dt'] = today
        d['order'] = time[2]
        stats.append(d)

    return sorted(stats, key=lambda x: x['order'])


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
        membership_types = MembershipType.objects.filter(
                                             status=True,
                                             status_detail='active')

    # get a list of apps from membership types
    apps_list = []
    for mt in membership_types:
        apps = MembershipApp.objects.filter(membership_types=mt)
        if apps:
            apps_list.extend(apps)

    apps_list = set(apps_list)
    apps_len = len(apps_list)

    # render the tokens
    help_text += '<div style="margin: 1em 10em;">'
    help_text += """
                <div style="margin-bottom: 1em;">
                You can use tokens to display member info or site specific
                information.
                A token is a field name wrapped in
                {{ }} or [ ]. <br />
                For example, token for first_name field: {{ first_name }}.
                Please note that tokens for member number, membership link,
                and expiration date/time are not available until the membership
                is approved.
                </div>
                """

    help_text += '<div id="toggle_token_view"><a href="javascript:;">' + \
                'Click to view available tokens</a></div>'
    help_text += '<div id="notice_token_list">'
    if apps_list:
        for app in apps_list:
            if apps_len > 1:
                help_text += '<div style="font-weight: bold;">%s</div>' % (
                                                            app.name)
            fields = MembershipAppField.objects.filter(
                                        membership_app=app,
                                        display=True,
                                        ).exclude(
                                        field_name=''
                                        ).order_by('order')
            help_text += "<ul>"
            for field in fields:
                help_text += '<li>{{ %s }} - (for %s)</li>' % (
                                                       field.field_name,
                                                       field.label)
            help_text += "</ul>"
    else:
        help_text += '<div>No field tokens because there is no ' + \
                    'applications.</div>'

    other_labels = ['member_number',
                    'membership_type',
                    'membership_link',
                    'renew_link',
                    'expire_dt',
                    'site_contact_name',
                    'site_contact_email',
                    'site_display_name',
                    'time_submitted',
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

    max_length = 8

    un = ' '.join(args)             # concat args into one string
    un = re.sub('\s+', '_', un)       # replace spaces w/ underscores
    un = re.sub('[^\w.-]+', '', un)   # remove non-word-characters
    un = un.strip('_.- ')           # strip funny-characters from sides
    un = un[:max_length].lower()    # keep max length and lowercase username

    others = []  # find similiar usernames
    for u in User.objects.filter(username__startswith=un):
        if u.username.replace(un, '0').isdigit():
            others.append(int(u.username.replace(un, '0')))

    if others and 0 in others:
        # the appended digit will compromise the username length
        # there would have to be more than 99,999 duplicate usernames
        # to kill the database username max field length
        un = '%s%s' % (un, str(max(others) + 1))

    return un.lower()


def get_user(**kwargs):
    """
    Returns first user that matches filters.
    If no user is found then a non type object is returned.
    """
    [user] = User.objects.filter(**kwargs)[:1] or [None]
    return user


def get_membership_stats():
    summary = []
    types = MembershipType.objects.all()
    total_active = 0
    total_pending = 0
    total_expired = 0
    total_total = 0
    for mem_type in types:
        mems = MembershipDefault.objects.filter(membership_type=mem_type)
        active = mems.filter(status=True, status_detail='active')
        pending = mems.filter(status=True, status_detail='pending')
        expired = mems.filter(status=True, status_detail='expired')
        total_all = active.count() + pending.count() + expired.count()
        total_active += active.count()
        total_pending += pending.count()
        total_expired += expired.count()
        total_total += total_all
        summary.append({
            'type': mem_type,
            'active': active.count(),
            'pending': pending.count(),
            'expired': expired.count(),
            'total': total_all,
        })

    return (sorted(summary, key=lambda x: x['type'].name),
        (total_active, total_pending, total_expired, total_total))


def make_csv(**kwargs):
    """
    Make a CSV file
    """
    from django.template.defaultfilters import slugify
    from tendenci.core.imports.utils import render_excel

    slug = kwargs.get('slug')

    if not slug:
        raise Http404

    try:
        app = App.objects.get(slug=slug)
    except App.DoesNotExist, App.MultipleObjectsReturned:
        raise Http404

    file_name = "%s.csv" % slugify(app.name)

    exclude_params = (
        'horizontal-rule',
        'header',
    )

    fields = AppField.objects.filter(app=app, exportable=True).exclude(field_type__in=exclude_params).order_by('position')
    labels = [field.label for field in fields]

    extra_labels = [
        'username',
        'Member Number',
        'Join Date',
        'Renew Date',
        'Expiration Date',
        'Status',
        'Status Detail',
        'Invoice Number',
        'Invoice Amount',
        'Invoice Balance'
    ]
    labels.extend(extra_labels)
    return render_excel(file_name, labels, [], '.csv')


class NoMembershipTypes(Exception):
    pass


def render_to_max_types(*args, **kwargs):
    if not isinstance(args,list):
        args = []
        args.append('memberships/max_types.html')

    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}

    response = HttpResponseServerError(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)
    
    return response


def normalize_field_names(fieldnames):
    for i in range(0, len(fieldnames)):
        # clean up the fieldnames
        # ex: change First Name to first_name
        fieldnames[i] = fieldnames[i].lower().replace(' ', '_')

    return fieldnames


def memb_import_parse_csv(mimport):
    """
    Parse csv data into a dictionary.
    """
    normalize_newline(mimport.upload_file.name)
    csv_reader = csv.reader(
        default_storage.open(mimport.upload_file.name, 'rb'))
    fieldnames = csv_reader.next()
    fieldnames = normalize_field_names(fieldnames)

    data_list = []

    for row in csv_reader:
        data_list.append(dict(zip(fieldnames, row)))

    return fieldnames, data_list


def check_missing_fields(memb_data, key):
    """
    Check if we have enough data to process for this row.
    """
    missing_field_msg = ''
    if key in ['member_number/email/fn_ln_phone',
               'email/member_number/fn_ln_phone']:
        if not any([memb_data['member_number'],
                    memb_data['email'],
                    all([memb_data['first_name'],
                         memb_data['last_name'],
                         memb_data['phone']])]):
            missing_field_msg = "Missing key(s) member_number or " + \
                                "'email' or ('first name', 'last name' and 'phone')"

    elif key in ['member_number/email', 'email/member_number']:
        if not any([memb_data['member_number'],
                    memb_data['email']]):
            missing_field_msg = "Missing key 'member_number' or 'email'"
    elif key == 'member_number':
        if not memb_data['member_number']:
            missing_field_msg = "Missing key 'member_number'"
    else:  # email
        if not memb_data['email']:
            missing_field_msg = "Missing key 'email'"

    return missing_field_msg


def get_user_by_email(email):
    """
    Get user by email address.
    """
    if not email:
        return None

    [user] = User.objects.filter(email__iexact=email).order_by(
                    '-is_active', '-is_superuser', '-is_staff'
                        )[:1] or [None]
    return user


def get_user_by_member_number(member_number):
    """
    Get user by member number.
    """
    if not member_number:
        return None

    [profile] = Profile.objects.filter(
                member_number=member_number).order_by(
                    '-user__is_active',
                    '-user__is_superuser',
                    '-user__is_staff'
                        )[:1] or [None]
    if profile:
        return profile.user
    return None


def get_user_by_fn_ln_phone(first_name, last_name, phone):
    """
    Get user by first name, last name and phone.
    """
    if not first_name or last_name or phone:
        return None

    [profile] = Profile.objects.filter(
                user__first_name=first_name,
                user__last_name=last_name,
                phone=phone).order_by(
                    '-user__is_active',
                    '-user__is_superuser',
                    '-user__is_staff'
                        )[:1] or [None]
    if profile:
        return profile.user
    return None


class ImportMembDefault(object):
    """
    Check and process (insert/update) a membership.
    """
    def __init__(self, request_user, mimport,
                               dry_run=True, **kwargs):
        """
        :param mimport: a instance of MembershipImport
        :param dry_run: if True, do everything except updating the database.
        """
        self.key = mimport.key
        self.request_user = request_user
        self.mimport = mimport
        self.dry_run = dry_run
        self.summary_d = self.init_summary()
        self.user_fields = dict([(field.name, field) \
                            for field in User._meta.fields \
                            if field.get_internal_type() != 'AutoField'])
        self.profile_fields = dict([(field.name, field) \
                            for field in Profile._meta.fields \
                            if field.get_internal_type() != 'AutoField' and \
                            field.name not in ['user', 'guid']])
        self.membership_fields = dict([(field.name, field) \
                            for field in MembershipDefault._meta.fields \
                            if field.get_internal_type() != 'AutoField' and \
                            field.name not in ['user', 'guid']])
        self.private_settings = self.set_default_private_settings()
        self.t4_timezone_map = {'AST': 'Canada/Atlantic',
                             'EST': 'US/Eastern',
                             'CST': 'US/Central',
                             'MST': 'US/Mountain',
                             'AKST': 'US/Alaska',
                             'PST': 'US/Pacific',
                             'GMT': 'UTC'
                             }
        self.t4_timezone_map_keys = self.t4_timezone_map.keys()

    def init_summary(self):
        return {
                 'insert': 0,
                 'update': 0,
                 'update_insert': 0,
                 'invalid': 0
                 }

    def set_default_private_settings(self):
        # public, private, all-members, member-type
        memberprotection = get_setting('module',
                                       'memberships',
                                       'memberprotection')
        d = {'allow_anonymous_view': False,
             'allow_user_view': False,
             'allow_member_view': False,
             'allow_user_edit': False,
             'allow_member_edit': False}

        if memberprotection == 'public':
            d['allow_anonymous_view'] = True
        if memberprotection == 'all-members':
            d['allow_user_view'] = True
        if memberprotection == 'member-type':
            d['allow_member_view'] = True
        return d

    def process_default_membership(self, memb_data, **kwargs):
        """
        Check if it's insert or update. If dry_run is False,
        do the import to the membership_default.

        :param memb_data: a dictionary that includes the info of a membership
        """
        self.memb_data = memb_data
        self.field_names = memb_data.keys()
        user = None
        memb = None
        user_display = {
            'error': u'',
            'user': None,
        }

        missing_fields_msg = check_missing_fields(self.memb_data, self.key)

        # don't process if we have missing value of required fields
        if missing_fields_msg:
            user_display['error'] = missing_fields_msg
            user_display['action'] = 'skip'
            if not self.dry_run:
                self.summary_d['invalid'] += 1
        else:
            if self.key == 'member_number/email/fn_ln_phone':
                user = get_user_by_member_number(
                                    self.memb_data['member_number'])
                if not user:
                    user = get_user_by_email(self.memb_data['email'])
                    if not user:
                        user = get_user_by_fn_ln_phone(
                                           self.memb_data['first_name'],
                                           self.memb_data['last_name'],
                                           self.memb_data['phone']
                                           )
            elif self.key == 'email/member_number/fn_ln_phone':
                user = get_user_by_email(self.memb_data['email'])
                if not user:
                    user = get_user_by_member_number(
                                self.memb_data['member_number'])
                    if not user:
                        user = get_user_by_fn_ln_phone(
                                           self.memb_data['first_name'],
                                           self.memb_data['last_name'],
                                           self.memb_data['phone'])
            elif self.key == 'member_number/email':
                user = get_user_by_member_number(
                                self.memb_data['member_number'])
                if not user:
                    user = get_user_by_email(self.memb_data['email'])
            elif self.key == 'email/member_number':
                user = get_user_by_email(self.memb_data['email'])
                if not user:
                    user = get_user_by_member_number(
                                self.memb_data['member_number'])
            elif self.key == 'member_number':
                user = get_user_by_member_number(
                                self.memb_data['member_number'])
            else:  # email
                user = get_user_by_email(self.memb_data['email'])

            if user:
                user_display['user_action'] = 'update'
                user_display['user'] = user
                # pick the most recent one
                [memb] = MembershipDefault.objects.filter(user=user).exclude(
                          status_detail='archive'
                                ).order_by('-id')[:1] or [None]
                if memb:
                    user_display['memb_action'] = 'update'
                    user_display['action'] = 'update'
                else:
                    user_display['memb_action'] = 'insert'
                    user_display['action'] = 'mixed'
            else:
                user_display['user_action'] = 'insert'
                user_display['memb_action'] = 'insert'
                user_display['action'] = 'insert'

            if not self.dry_run:
                if all([
                        user_display['user_action'] == 'insert',
                        user_display['memb_action'] == 'insert'
                        ]):
                    self.summary_d['insert'] += 1
                elif all([
                        user_display['user_action'] == 'update',
                        user_display['memb_action'] == 'update'
                        ]):
                    self.summary_d['update'] += 1
                else:
                    self.summary_d['update_insert'] += 1

                # now do the update or insert
                self.do_import_membership_default(user, memb, user_display)
                return

        user_display.update({
            'first_name': self.memb_data.get('first_name', u''),
            'last_name': self.memb_data.get('last_name', u''),
            'email': self.memb_data.get('email', u''),
            'username': self.memb_data.get('username', u''),
            'member_number': self.memb_data.get('member_number', u''),
            'phone': self.memb_data.get('phone', u''),
            'company': self.memb_data.get('company', u''),
        })

        return user_display

    def do_import_membership_default(self, user, memb, action_info):
        """
        Database import here - insert or update
        """
        # handle user
        if not user:
            user = User()
            username_before_assign = ''
        else:
            username_before_assign = user.username

        # always remove user column
        if 'user' in self.field_names:
            self.field_names.remove('user')

        self.assign_import_values_from_dict(user, action_info['user_action'])

        # clean username
        user.username = re.sub('[^\w+-.@]', u'', user.username)

        # make sure username is unique.
        if action_info['user_action'] == 'insert':
            user.username = make_username_unique(user.username)
        else:
            # it's update but a new username is assigned
            # check if its unique
            if user.username != username_before_assign:
                user.username = make_username_unique(user.username)

        # allow import with override of password
        if 'password' in self.field_names and self.mimport.override and user.password:
            user.set_password(user.password)

        # is_active; unless forced via import
        if 'is_active' not in self.field_names:
            user.is_active = True

        user.save()

        # process profile
        try:  # get or create
            profile = user.get_profile()
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user,
               creator=self.request_user,
               creator_username=self.request_user.username,
               owner=self.request_user,
               owner_username=self.request_user.username,
               **self.private_settings
            )

        self.assign_import_values_from_dict(profile, action_info['user_action'])
        profile.user = user

        if profile.status == None or profile.status == '' or \
            self.memb_data.get('status', '') == '':
            profile.status = True
        if not profile.status_detail:
            profile.status_detail = 'active'
        else:
            profile.status_detail = profile.status_detail.lower()

        profile.save()

        # membership
        if not memb:
            memb = MembershipDefault(
                    user=user,
                    creator=self.request_user,
                    creator_username=self.request_user.username,
                    owner=self.request_user,
                    owner_username=self.request_user.username,
                                     )

        self.assign_import_values_from_dict(memb, action_info['memb_action'])

        if memb.status == None or memb.status == '' or \
            self.memb_data.get('status', '') == '':
            memb.status = True
        if not memb.status_detail:
            memb.status_detail = 'active'
        else:
            memb.status_detail = memb.status_detail.lower()

        # membership type
        if not hasattr(memb, "membership_type") or not memb.membership_type:
            # last resort - pick the first available membership type
            memb.membership_type = MembershipType.objects.all(
                                            ).order_by('id')[0]

        # no join_dt - set one
        if not hasattr(memb, 'join_dt') or not memb.join_dt:
            if memb.status and memb.status_detail == 'active':
                memb.join_dt = datetime.now()

        # no expire_dt - get it via membership_type
        if not hasattr(memb, 'expire_dt') or not memb.expire_dt:
            if memb.membership_type:
                expire_dt = memb.membership_type.get_expiration_dt(
                                            join_dt=memb.join_dt)
                setattr(memb, 'expire_dt', expire_dt)
        memb.save()

        memb.is_active = self.is_active(memb)

        # member_number
        # TODO: create a function to assign a member number
        if not memb.member_number:
            if memb.is_active:
                memb.member_number = 5100 + memb.pk
        if memb.member_number:
            if not profile.member_number:
                profile.member_number = memb.member_number
                profile.save()
            else:
                if profile.member_number != memb.member_number:
                    profile.member_number = memb.member_number
                    profile.save()
        else:
            if profile.member_number:
                profile.member_number = ''
                profile.save()

        # add to group only for the active memberships
        if memb.is_active:
            # group associated to membership type
            params = {'creator_id': self.request_user.pk,
                      'creator_username': self.request_user.username,
                      'owner_id': self.request_user.pk,
                      'owner_username': self.request_user.username}
            memb.membership_type.group.add_user(memb.user, **params)

    def is_active(self, memb):
        return all([memb.status,
                    memb.status_detail == 'active',
                    not memb.expire_dt or memb.expire_dt > datetime.now()
                    ])

    def assign_import_values_from_dict(self, instance, action):
        """
        Assign the import value from a dictionary object
        - self.memb_data.
        """
        if instance.__class__ == User:
            assign_to_fields = self.user_fields
        elif instance.__class__ == Profile:
            assign_to_fields = self.profile_fields
        else:
            assign_to_fields = self.membership_fields
        assign_to_fields_names = assign_to_fields.keys()

        for field_name in self.field_names:
            if field_name in assign_to_fields_names:
                if any([
                        action == 'insert',
                        self.mimport.override,
                        not hasattr(instance, field_name) or \
                        getattr(instance, field_name) == '' or \
                        getattr(instance, field_name) == None
                        ]):
                    value = self.memb_data[field_name]
                    value = self.clean_data(value,
                                            assign_to_fields[field_name])
                    setattr(instance, field_name, value)

        # if insert, set defaults for the fields not in csv.
        for field_name in assign_to_fields_names:
            if field_name not in self.field_names and action == 'insert':
                if field_name not in self.private_settings.keys():
                    value = self.get_default_value(
                                    assign_to_fields[field_name])
                    if value != None:
                        setattr(instance, field_name, value)

    def get_default_value(self, field):
        # if allows null or has default, return None
        if field.null or field.has_default():
            return None

        field_type = field.get_internal_type()

        if field_type == 'BooleanField':
            return False

        if field_type == 'DateField':
            return date

        if field_type == 'DateTimeField':
            return datetime.now()

        if field_type == 'DecimalField':
            return Decimal(0)

        if field_type == 'IntegerField':
            return 0

        if field_type == 'FloatField':
            return 0

        if field_type == 'ForeignKey':
            [value] = field.related.parent_model.objects.all(
                                        )[:1] or [None]
            return value

        return ''

    def clean_data(self, value, field):
        """
        Clean the data based on the field type.
        """
        field_type = field.get_internal_type()
        if field_type in ['CharField', 'EmailField',
                          'URLField', 'SlugField']:
            if not value:
                value = ''
            if len(value) > field.max_length:
                # truncate the value to ensure its length <= max_length
                value = value[:field.max_length]
            if field.name == 'time_zone':
                if value not in pytz.all_timezones:
                    if value in self.t4_timezone_map_keys:
                        value = self.t4_timezone_map[value]
            try:
                value = field.to_python(value)
            except exceptions.ValidationError:
                if field.has_default():
                    value = field.get_default()
                else:
                    value = ''

        elif field_type == 'BooleanField':
            try:
                value = field.to_python(value)
            except exceptions.ValidationError:
                value = False
        elif field_type == 'DateField':
            if value:
                value = dparser.parse(value)
                try:
                    value = field.to_python(value)
                except exceptions.ValidationError:
                    pass

            if not value:
                if not field.null:
                    value = date

        elif field_type == 'DateTimeField':
            if value:
                value = dparser.parse(value)
                try:
                    value = field.to_python(value)
                except exceptions.ValidationError:
                    pass

            if not value:
                if value == '':
                    value = None
                if not field.null:
                    value = datetime.now()
        elif field_type == 'DecimalField':
            try:
                value = field.to_python(value)
            except exceptions.ValidationError:
                value = Decimal(0)
        elif field_type == 'IntegerField':
            try:
                value = int(value)
            except:
                value = 0
        elif field_type == 'FloatField':
            try:
                value = float(value)
            except:
                value = 0
        elif field_type == 'ForeignKey':
            orignal_value = value
            # assume id for foreign key
            try:
                value = int(value)
            except:
                value = None

            if value:
                [value] = field.related.parent_model.objects.filter(
                                            pk=value)[:1] or [None]

            # membership_type - look up by name in case
            # they entered name instead of id
            if not value and field.name == 'membership_type':
                value = get_membership_type_by_name(orignal_value)

            if not value and not field.null:
                # if the field doesn't allow null, grab the first one.
                [value] = field.related.parent_model.objects.all(
                                        ).order_by('id')[:1] or [None]

        return value


def get_membership_type_by_value(value):
    if value and value.isdigit():
        value = int(value)
    if isinstance(value, int):
        return get_membership_type_by_id(value)
    elif isinstance(value, str):
        return get_membership_type_by_name(value)


def get_membership_type_by_id(pk):
    [memb_type] = MembershipType.objects.filter(pk=pk)[:1] or [None]

    return memb_type


def get_membership_type_by_name(name):
    [memb_type] = MembershipType.objects.filter(name=name)[:1] or [None]

    return memb_type
