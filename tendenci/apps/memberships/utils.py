from builtins import str
import os
import csv
import re
from decimal import Decimal
from datetime import datetime, date, timedelta, time
import dateutil.parser as dparser
import pytz
import time as ttime
import subprocess
from dateutil.relativedelta import relativedelta

from django.http import HttpResponseServerError
from django.conf import settings
import simplejson
from django.contrib.auth.models import User
from django.template import loader
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core import exceptions
from django.utils.encoding import smart_str
from django.db.models.fields import AutoField
from django.db.models import ForeignKey, OneToOneField
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile

from tendenci.libs.utils import python_executable
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.memberships.models import (MembershipType,
                                                MembershipDefault,
                                                MembershipDemographic,
                                                MembershipApp,
                                                MembershipAppField,
                                                MembershipFile,
                                                VALID_MEMBERSHIP_STATUS_DETAIL)
from tendenci.apps.base.utils import normalize_newline, UnicodeWriter
from tendenci.apps.profiles.models import Profile
from tendenci.apps.profiles.utils import make_username_unique, spawn_username
from tendenci.apps.emails.models import Email
from tendenci.apps.educations.models import Education


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


def get_corporate_membership_choices(active_only=True):
    cm_list = [(0, 'SELECT ONE')]
    from tendenci.apps.corporate_memberships.models import CorpMembership

    corp_membs = CorpMembership.objects.exclude(status_detail='archive')
    if active_only:
        corp_membs = corp_membs.filter(status_detail='active')
    corp_membs = corp_membs.order_by('corp_profile__name')

    for corp_memb in corp_membs:
        if corp_memb.status_detail == 'active':
            cm_list.append((corp_memb.id, corp_memb.corp_profile.name))
        else:
            cm_list.append((corp_memb.id, '%s (%s)' % (corp_memb.corp_profile.name, corp_memb.status_detail)))

    return cm_list


def get_membership_type_choices(request_user, customer, membership_app, corp_membership=None):
    """
    Get membership type choices available in this application and to this user.

    If corporate memberships:
        Only show membership types available to this corporation.
    """

    mt_list = []
    # assume not superuser; get superuser status
    is_superuser = False

    if hasattr(request_user, 'profile'):
        is_superuser = request_user.profile.is_superuser

    if corp_membership:
        membership_types = [corp_membership.corporate_membership_type.membership_type]
    else:
        membership_types = membership_app.membership_types.all()

        # filter memberships types based on request_user superuser status
        if not is_superuser:
            membership_types = membership_types.filter(admin_only=False)

        membership_types = membership_types.order_by('position')

    for mt in membership_types:
        mt_list.append((mt.id, mt.get_price_display(customer)))

    return mt_list


def get_selected_demographic_fields(membership_app, forms):
    """
    Get the selected demographic fields for the app.
    """
    demographic_field_dict = dict([(field.name, field)
                        for field in MembershipDemographic._meta.fields
                        if field.get_internal_type() != 'AutoField'])
    app_fields = MembershipAppField.objects.filter(
                                membership_app=membership_app,
                                display=True
                                ).values(
                        'label', 'field_name', 'required')
    selected_fields = []
    for app_field in app_fields:
        if app_field['field_name'] in demographic_field_dict:
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
    demographic_field_names = [field.name
                        for field in MembershipDemographic._meta.fields
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


def get_ud_file_instance(demographics, field_name):
    data = getattr(demographics, field_name, '')
    if not data:
        return None

    try:
        pk = eval(data).get('pk')
    except Exception:
        pk = 0

    file_id = 0
    if pk:
        try:
            file_id = int(pk)
        except Exception:
            file_id = 0

    try:
        file_instance = MembershipFile.objects.get(pk=file_id)
    except MembershipFile.DoesNotExist:
        file_instance = None

    return file_instance


def run_membership_export(request,
        identifier='',
        export_fields='all_fields',
        export_type='all',
        export_status_detail='active',
        user_id=0, cp_id=0, ids=''):
    if not identifier:
        identifier = int(ttime.time())
    temp_file_path = 'export/memberships/{0}_{1}_temp.csv'.format(identifier, cp_id)
    default_storage.save(temp_file_path, ContentFile(''))
    
    # start the process
    subprocess.Popen([python_executable(), "manage.py",
                  "membership_export_process",
                  '--export_fields=%s' % export_fields,
                  '--export_type=%s' % export_type,
                  '--export_status_detail=%s' % export_status_detail,
                  '--identifier=%s' % identifier,
                  '--user=%s' % request.user.id,
                  '--cp_id=%d' % cp_id,
                  '--ids=%s' % ids,])


def get_membership_rows(
        user_field_list,
        profile_field_list,
        education_field_list,
        demographic_field_list,
        membership_field_list,
        invoice_field_list,
        foreign_keys,
        export_type=u'all',
        export_status_detail=u'',
        cp_id=0,
        ids=''):

    if ids:
        ids = ids.split(',')
        memberships = MembershipDefault.objects.filter(id__in=ids)
    else:
        # grab all except the archived
        memberships = MembershipDefault.objects.filter(
            status=True).exclude(status_detail='archive')

        if export_status_detail:
            if export_status_detail == 'pending':
                memberships = memberships.filter(
                    status_detail__icontains='pending')
            else:
                memberships = memberships.filter(
                    status_detail=export_status_detail)

    if not export_type == 'all':
        memberships = memberships.filter(membership_type=export_type)

    if cp_id:
        memberships = memberships.filter(corp_profile_id=cp_id)

    for membership in memberships:
        row_dict = {}

        user = membership.user
        invoice = membership.get_invoice()

        [profile] = Profile.objects.filter(user=user)[:1] or [None]
        education_list = user.educations.all().order_by('pk')[0:4]
        [demographic] = MembershipDemographic.objects.filter(user=user)[:1] or [None]

        for field_name in user_field_list:
            row_dict[field_name] = get_obj_field_value(field_name, user)

        if profile:
            for field_name in profile_field_list:
                orig_field_name = field_name
                if field_name == 'profile_status_detail':
                    field_name = 'status_detail'
                elif field_name == 'profile_status':
                    field_name = 'status'
                row_dict[orig_field_name] = get_obj_field_value(
                    field_name, profile, field_name in foreign_keys)

        if education_list:
            cnt = 0
            for education in education_list:
                row_dict[education_field_list[cnt]] = education.school
                row_dict[education_field_list[cnt+1]] = education.major
                row_dict[education_field_list[cnt+2]] = education.degree
                row_dict[education_field_list[cnt+3]] = education.graduation_year
                cnt += 4

        if demographic:
            for field_name in demographic_field_list:
                row_dict[field_name] = get_obj_field_value(
                    field_name, demographic, field_name in foreign_keys)

        for field_name in membership_field_list:
            row_dict[field_name] = get_obj_field_value(
                field_name, membership, field_name in foreign_keys)

        if invoice:
            for field_name in invoice_field_list:
                row_dict[field_name] = get_obj_field_value(
                    field_name, invoice, field_name in foreign_keys)

        yield row_dict


def get_obj_field_value(field_name, obj, is_foreign_key=False):
    value = getattr(obj, field_name)
    if value and is_foreign_key:
        value = value.id
    return value


def process_export(
        export_fields='all_fields',
        export_type='all',
        export_status_detail='active',
        identifier=u'', user_id=0, cp_id=0, ids=''):
    from tendenci.apps.perms.models import TendenciBaseModel

    if export_fields == 'main_fields':

        base_field_list = []

        user_field_list = [
            'first_name',
            'last_name',
            'username',
            'email',
            'is_active',
            'is_staff',
            'is_superuser']

        profile_field_list = [
            'member_number',
            'company',
            'phone',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'country',
            'address_2',
            'address2_2',
            'city_2',
            'state_2',
            'zipcode_2',
            'country_2']

        demographic_field_list = []

        membership_field_list = [
            'app',
            'membership_type',
            'corp_profile_id',
            'corporate_membership_id',
            'join_dt',
            'expire_dt',
            'renewal',
            'renew_dt',
            'status',
            'status_detail']

        invoice_field_list = []

    else:

        # base ------------
        base_field_list = [
            smart_str(field.name) for field in TendenciBaseModel._meta.fields
            if not field.__class__ == AutoField]

        # user ------------
        user_field_list = [
            smart_str(field.name) for field in User._meta.fields
            if not field.__class__ == AutoField]
        user_field_list.remove('password')

        # profile ---------
        profile_field_list = [
            smart_str(field.name) for field in Profile._meta.fields
            if not field.__class__ == AutoField]
        profile_field_list = [
            name for name in profile_field_list
            if name not in base_field_list]
        profile_field_list.remove('guid')
        profile_field_list.remove('user')
        if 'status' in profile_field_list:
            profile_field_list.remove('status')
        if 'status_detail' in profile_field_list:
            profile_field_list.remove('status_detail')

        # demographic -----
        demographic_field_list = [
            smart_str(field.name) for field in MembershipDemographic._meta.fields
            if not field.__class__ == AutoField]
        demographic_field_list.remove('user')

        # membership ------
        membership_field_list = [
            smart_str(field.name) for field in MembershipDefault._meta.fields
            if not field.__class__ == AutoField]
        membership_field_list.remove('user')

        # invoice ---------
        invoice_field_list = ['total', 'balance']

    education_field_list = [
        'school1',
        'major1',
        'degree1',
        'graduation_dt1',
        'school2',
        'major2',
        'degree2',
        'graduation_dt2',
        'school3',
        'major3',
        'degree3',
        'graduation_dt3',
        'school4',
        'major4',
        'degree4',
        'graduation_dt4',
    ]

    profile_field_list.extend(['profile_status', 'profile_status_detail'])

    title_list = (
        user_field_list +
        profile_field_list +
        education_field_list +
        membership_field_list +
        invoice_field_list +
        demographic_field_list)

    # list of foreignkey fields
    if export_fields == 'main_fields':
        fks = ['membership_type', 'app']
    else:

        user_fks = [
            field.name for field in User._meta.fields
            if isinstance(field, (ForeignKey, OneToOneField))]

        profile_fks = [
            field.name for field in Profile._meta.fields
            if isinstance(field, (ForeignKey, OneToOneField))]

        demographic_fks = [
            field.name for field in MembershipDemographic._meta.fields
            if isinstance(field, (ForeignKey, OneToOneField))]

        membership_fks = [
            field.name for field in MembershipDefault._meta.fields
            if isinstance(field, (ForeignKey, OneToOneField))]

        fks = set(user_fks + profile_fks + demographic_fks + membership_fks)

    membership_ids_dict = dict(MembershipType.objects.all().values_list('id', 'name').union(
                               MembershipType.objects.all_inactive().values_list('id', 'name')))
    app_ids_dict = dict(MembershipApp.objects.all().values_list('id', 'name'))

    identifier = identifier or int(ttime.time())
    file_name_temp = 'export/memberships/%s_%d_temp.csv' % (identifier, cp_id)

    with default_storage.open(file_name_temp, 'w') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=title_list)
        csv_writer.writeheader()

        membership_rows = get_membership_rows(
            user_field_list,
            profile_field_list,
            education_field_list,
            demographic_field_list,
            membership_field_list,
            invoice_field_list,
            fks,
            export_type,
            export_status_detail,
            cp_id,
            ids=ids)

        for row_dict in membership_rows:

            items_dict = {}
            for field_name in title_list:
                item = row_dict.get(field_name)
                if item is None:
                    item = ''
                if item:
                    if isinstance(item, datetime):
                        # strftime will throw an error if year is before 1900
                        if item.year < 1900:
                            item = '1900-1-1 00:00:00'
                        else:
                            item = item.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(item, date):
                        item = item.strftime('%Y-%m-%d')
                    elif isinstance(item, time):
                        item = item.strftime('%H:%M:%S')
                    elif field_name == 'membership_type' and item in membership_ids_dict:
                        # display membership type name instead of id
                        item = membership_ids_dict[item]
                    elif field_name == 'app':
                        # display membership type name instead of id
                        item = app_ids_dict[item]
                items_dict[field_name] = item
            csv_writer.writerow(items_dict)

    # rename the file name
    file_name = 'export/memberships/%s_%d.csv' % (identifier, cp_id)
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))

    # delete the temp file
    default_storage.delete(file_name_temp)

    # notify user that export is ready to download
    [user] = User.objects.filter(id=user_id)[:1] or [None]
    if user and user.email:
        corp_profile = None
        if cp_id:
            from tendenci.apps.corporate_memberships.models import CorpProfile
            [corp_profile] = CorpProfile.objects.filter(pk=cp_id)[:1] or [None]
        download_url = reverse('memberships.default_export_download', args=[identifier])

        if cp_id:
            download_url = '%s?cp_id=%s' % (download_url, cp_id)
        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name,
            'export_status_detail': export_status_detail,
            'export_fields': export_fields,
            'corp_profile': corp_profile}

        subject = render_to_string(
            template_name='memberships/notices/export_ready_subject.html', context=parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            template_name='memberships/notices/export_ready_body.html', context=parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)

        email.send()


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
    colnames = next(csv_file)  # row 1;

    if machine_name:
        colnames = [slugify(c).replace('-', '') for c in colnames]

    cols = range(len(colnames))
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
        errs.append(_("Pleaes make sure you're importing a .csv file."))
        return False, errs

    if has_null_byte(file_path):
        errs.append(_('This .csv file has null characters, try re-saving it.'))
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
        return False, [_('Please make sure there is a membership type column.')]


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
    time_ranges = [
        ("Last Month", months_back(1)),
        ("Last 3 Months", months_back(3)),
        ("Last 6 Months", months_back(6)),
        ("Last 9 Months", months_back(9)),
        ("Last 12 Months", months_back(12)),
        ("Year to Date", year),
    ]

    stats = []
    for time_range in time_ranges:
        start_dt = time_range[1]
        d = {}
        active_mems = MembershipDefault.objects.filter(
                        status=True,
                        status_detail__in=['active', 'archive']
            ).filter(application_approved_dt__gte=start_dt
                     ).distinct('user__id', 'membership_type__id')
        d['new'] = active_mems.filter(renewal=False).count()
        d['renewing'] = active_mems.filter(renewal=True).count()
        d['time'] = time_range[0]
        d['start_dt'] = start_dt
        stats.append(d)

    return stats


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
                ).order_by('position')

            help_text += "<ul>"
            for field in fields:
                help_text += '<li>{{ %s }} - (for %s)</li>' % (field.field_name, field.label)
            help_text += "</ul>"
    else:
        help_text += '<div>No field tokens because there is no ' + \
                    'applications.</div>'

    other_labels = ['member_number',
                    'membership_type',
                    'membership_price',
                    'donation_amount',
                    'total_amount',
                    'referer_url',
                    'membership_link',
                    'view_link',
                    'invoice_link',
                    'renew_link',
                    'expire_dt',]
    if get_setting('module', 'recurring_payments', 'enabled') and get_setting('module', 'memberships', 'autorenew'):
        other_labels += ['link_to_setup_auto_renew']
    other_labels += ['site_contact_name',
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
                    (function($) {
                        $(document).ready(function() {
                            $('#notice_token_list').hide();
                                 $('#toggle_token_view').click(function () {
                                $('#notice_token_list').toggle();
                            });
                        });
                    }(jQuery));
                </script>
                """

    return help_text


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

    total_dict = {
        'active': total_active,
        'pending': total_pending,
        'expired': total_expired,
        'total': total_total,
    }

    return (sorted(summary, key=lambda x: x['type'].name), total_dict)


class NoMembershipTypes(Exception):
    pass


def render_to_max_types(*args, **kwargs):
    if not isinstance(args,list):
        args = []
        args.append('memberships/max_types.html')

    httpresponse_kwargs = {'content_type': kwargs.pop('mimetype', None)}

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
    with default_storage.open(mimport.upload_file.name, "rt") as csvfile:
        csv_reader = csv.reader(csvfile)
        fieldnames = next(csv_reader)
        fieldnames = normalize_field_names(fieldnames)
    
        data_list = []
    
        for row in csv_reader:
            data_list.append(dict(zip(fieldnames, row)))
    
        return fieldnames, data_list


def check_missing_fields(memb_data, key, **kwargs):
    """
    Check if we have enough data to process for this row.
    """
    missing_field_msg = ''
    is_valid = True
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
    elif key == 'username':
        if not memb_data['username']:
            missing_field_msg = "Missing key 'username'"
    else:  # email
        if not memb_data['email']:
            missing_field_msg = "Missing key 'email'"

    if missing_field_msg:
        is_valid = False

    return is_valid, missing_field_msg


def get_user_by_email(email):
    """
    Get user by email address.
    """
    if not email:
        return None

    users = User.objects.filter(email__iexact=email).order_by(
                    '-is_active', '-is_superuser', '-is_staff'
                        )
    return users


def get_user_by_username(username):
    """
    Get user by username.
    """
    if not username:
        return None

    return User.objects.filter(username=username)


def get_user_by_member_number(member_number):
    """
    Get user by member number.
    """
    if not member_number:
        return None

    profiles = Profile.objects.filter(
                member_number=member_number).order_by(
                    '-user__is_active',
                    '-user__is_superuser',
                    '-user__is_staff'
                        )
    if profiles:
        return [profile.user for profile in profiles]
    return None


def get_user_by_fn_ln_phone(first_name, last_name, phone):
    """
    Get user by first name, last name and phone.
    """
    if not first_name or last_name or phone:
        return None

    profiles = Profile.objects.filter(
                user__first_name=first_name,
                user__last_name=last_name,
                phone=phone).order_by(
                    '-user__is_active',
                    '-user__is_superuser',
                    '-user__is_staff'
                        )
    if profiles:
        return [profile.user for profile in profiles]
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
        self.user_fields = dict([(field.name, field)
                            for field in User._meta.fields
                            if field.get_internal_type() != 'AutoField'])
        self.profile_fields = dict([(field.name, field)
                            for field in Profile._meta.fields
                            if field.get_internal_type() != 'AutoField' and
                            field.name not in ['user', 'guid']])
        self.membershipdemographic_fields = dict([(field.name, field)
                            for field in MembershipDemographic._meta.fields
                            if field.get_internal_type() != 'AutoField' and
                            field.name not in ['user']])
        self.education_fields = ['school1', 'major1', 'degree1', 'graduation_year1',
                                  'school2', 'major2', 'degree2', 'graduation_year2',
                                  'school3', 'major3', 'degree3', 'graduation_year3',
                                  'school4', 'major4', 'degree4', 'graduation_year4',]
        self.should_handle_demographic = False
        self.should_handle_education = False
        self.membership_fields = dict([(field.name, field)
                            for field in MembershipDefault._meta.fields
                            if field.get_internal_type() != 'AutoField' and
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
        # all membership types
        self.all_membership_type_ids = MembershipType.objects.values_list(
                                        'id', flat=True)
        self.all_membership_type_names = MembershipType.objects.values_list(
                                        'name', flat=True)
        # membership types associated membership apps
        self.membership_type_ids = [mt.id for mt in MembershipType.objects.all(
                                    )
                                    if mt.membershipapp_set.all().exists()
                                    ]
        self.membership_apps = MembershipApp.objects.all()
        self.membership_app_ids_dict = dict([(app.id, app
                                    ) for app in self.membership_apps])
        self.membership_app_names_dict = dict([(app.name, app
                                    ) for app in self.membership_apps])
        # membership_type to app map
        # the two lists are: apps and apps for corp individuals
        self.membership_types_to_apps_map = dict([(mt_id, ([], [])
                                    ) for mt_id in self.membership_type_ids])
        for app in self.membership_apps:
            mt_ids = app.membership_types.all().values_list('id', flat=True)
            for mt_id in self.membership_type_ids:
                if mt_id in mt_ids:
                    if app.use_for_corp:
                        self.membership_types_to_apps_map[
                                    mt_id][1].append(app.id)
                    else:
                        self.membership_types_to_apps_map[
                                    mt_id][0].append(app.id)
        [self.default_membership_type_id] = [key for key in
                    self.membership_types_to_apps_map
            if self.membership_types_to_apps_map[key][0] != []][:1] or [None]
        [self.default_membership_type_id_for_corp_indiv] = [key for key in
                    self.membership_types_to_apps_map
            if self.membership_types_to_apps_map[key][1] != []][:1] or [None]

        apps = MembershipApp.objects.filter(
                                    status=True,
                                    status_detail__in=['active',
                                                        'published']
                                    ).order_by('id')
        [self.default_app_id] = apps.filter(
                                    use_for_corp=False
                                    ).values_list('id',
                                                  flat=True
                                    )[:1] or [None]
        [self.default_app_id_for_corp_indiv] = apps.filter(
                                    use_for_corp=True
                                    ).values_list('id',
                                                  flat=True
                                    )[:1] or [None]

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

    def clean_membership_type(self, memb_data, **kwargs):
        """
        Ensure we have a valid membership type.
        """
        is_valid = True
        error_msg = ''

        if 'membership_type' in memb_data and memb_data['membership_type']:
            value = memb_data['membership_type']

            if str(value).isdigit():
                value = int(value)
                if value not in self.all_membership_type_ids:
                    is_valid = False
                    error_msg = 'Invalid membership type "%d"' % value
                else:
                    memb_data['membership_type'] = value
            else:
                if not MembershipType.objects.filter(
                                            name=value).exists():
                    is_valid = False
                    error_msg = 'Invalid membership type "%s"' % value
                else:
                    memb_data['membership_type'] = MembershipType.objects.filter(
                                            name=value
                                            ).values_list(
                                            'id', flat=True)[0]
        else:
            # the spread sheet doesn't have the membership_type field,
            # assign the default one
            if memb_data.get('corporate_membership_id'):
                if self.default_membership_type_id_for_corp_indiv:
                    memb_data['membership_type'] = self.default_membership_type_id_for_corp_indiv
                else:
                    is_valid = False
                    error_msg = 'Membership type for corp. individuals not available.'
            else:
                if self.default_membership_type_id:
                    memb_data['membership_type'] = self.default_membership_type_id
                else:
                    is_valid = False
                    error_msg = 'No membership type. Please add one to the site.'

        return is_valid, _(error_msg)

    def clean_app(self, memb_data):
        """
        Ensure the app field has the right data.
        """
        is_valid = True
        error_msg = ''

        if 'app' in memb_data and memb_data['app'] and memb_data['app']:
            value = memb_data['app']

            if str(value).isdigit():
                value = int(value)
                if value not in self.membership_app_ids_dict:
                    is_valid = False
                    error_msg = 'Invalid app "%d"' % value
                else:
                    memb_data['app'] = value
            else:
                # check for app name
                if value not in self.membership_app_names_dict:
                    is_valid = False
                    error_msg = 'Invalid app "%s"' % value
                else:
                    app = self.membership_app_names_dict[value]
                    memb_data['app'] = app.id
        else:
            # no app specified, assign the default one
            membership_type_id = memb_data['membership_type']

            app_id = None
            if self.membership_types_to_apps_map and \
                membership_type_id in self.membership_types_to_apps_map:
                if memb_data.get('corporate_membership_id'):
                    [app_id] = self.membership_types_to_apps_map[
                                        membership_type_id][1][:1] or [None]
                    if not app_id:
                        app_id = self.default_app_id_for_corp_indiv
                        if not app_id:
                            app_id = self.default_app_id
                else:
                    [app_id] = self.membership_types_to_apps_map[
                                        membership_type_id][0][:1] or [None]

            if app_id:
                memb_data['app'] = app_id
            else:
                if self.default_app_id:
                    memb_data['app'] = self.default_app_id
                else:
                    is_valid = False
                    error_msg = 'No membership app. Please add one to the site.'

        return is_valid, _(error_msg)

    def clean_corporate_membership(self, memb_data):
        if 'corporate_membership_id' in memb_data:
            try:
                memb_data['corporate_membership_id'] = int(memb_data['corporate_membership_id'])
            except:
                memb_data['corporate_membership_id'] = 0

        if 'corp_profile_id' in memb_data:
            try:
                memb_data['corp_profile_id'] = int(memb_data['corp_profile_id'])
            except:
                memb_data['corp_profile_id'] = 0

    def has_demographic_fields(self, field_names):
        """
        Check if import has demographic fields.
        """
        for field_name in self.membershipdemographic_fields:
            if field_name in field_names:
                return True

        return False

    def has_education_fields(self, field_names):
        """
        Check if import has education fields.
        """
        for field_name in self.education_fields:
            if field_name in field_names:
                return True

        return False

    def clean_username(self, memb_data):
        if 'username' in memb_data:
            memb_data['username'] = memb_data['username'][:30]

    def process_default_membership(self, idata, **kwargs):
        """
        Check if it's insert or update. If dry_run is False,
        do the import to the membership_default.

        :param memb_data: a dictionary that includes the info of a membership
        """
        self.memb_data = idata.row_data
        user = None
        memb = None
        user_display = {
            'error': u'',
            'user': None,
            'action': ''
        }

        is_valid, error_msg = check_missing_fields(self.memb_data,
                                                  self.key)
        if is_valid:
            self.clean_corporate_membership(self.memb_data)
            is_valid, error_msg = self.clean_membership_type(
                                                self.memb_data)
            if is_valid:
                is_valid, error_msg = self.clean_app(self.memb_data)

        # don't process if we have missing value of required fields
        if not is_valid:
            user_display['error'] = error_msg
            user_display['action'] = 'skip'
            if not self.dry_run:
                self.summary_d['invalid'] += 1
                idata.action_taken = 'skipped'
                idata.error = user_display['error']
                idata.save()
        else:
            self.clean_username(self.memb_data)
            if self.key == 'member_number/email/fn_ln_phone':
                users = get_user_by_member_number(
                                    self.memb_data['member_number'])
                if not users:
                    users = get_user_by_email(self.memb_data['email'])
                    if not users:
                        users = get_user_by_fn_ln_phone(
                                           self.memb_data['first_name'],
                                           self.memb_data['last_name'],
                                           self.memb_data['phone']
                                           )
            elif self.key == 'email/member_number/fn_ln_phone':
                users = get_user_by_email(self.memb_data['email'])
                if not users:
                    users = get_user_by_member_number(
                                self.memb_data['member_number'])
                    if not users:
                        users = get_user_by_fn_ln_phone(
                                           self.memb_data['first_name'],
                                           self.memb_data['last_name'],
                                           self.memb_data['phone'])
            elif self.key == 'member_number/email':
                users = get_user_by_member_number(
                                self.memb_data['member_number'])
                if not users:
                    users = get_user_by_email(self.memb_data['email'])
            elif self.key == 'email/member_number':
                users = get_user_by_email(self.memb_data['email'])
                if not users:
                    users = get_user_by_member_number(
                                self.memb_data['member_number'])
            elif self.key == 'member_number':
                users = get_user_by_member_number(
                                self.memb_data['member_number'])
            elif self.key == 'username':
                users = get_user_by_username(self.memb_data['username'])
            else:  # email
                users = get_user_by_email(self.memb_data['email'])

            if users:
                user_display['user_action'] = 'update'

                # pick the most recent one
                memb = None
                for user in users:
                    memberships = MembershipDefault.objects.filter(
                                    user=user,
                                    membership_type__id=self.memb_data['membership_type']
                                                      ).exclude(
                                      status_detail='archive')
                    if memberships.exists():

                        [memb] = memberships.order_by('-id')[:1] or [None]
                        user_display['user'] = user
                        break

                if not memb:
                    user_display['user'] = users[0]
                    user_display['memb_action'] = 'insert'
                    user_display['action'] = 'mixed'
                else:
                    user_display['memb_action'] = 'update'
                    user_display['action'] = 'update'
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
                    idata.action_taken = 'insert'
                elif all([
                        user_display['user_action'] == 'update',
                        user_display['memb_action'] == 'update'
                        ]):
                    self.summary_d['update'] += 1
                    idata.action_taken = 'update'
                else:
                    self.summary_d['update_insert'] += 1
                    idata.action_taken = 'update_insert'

                self.field_names = self.memb_data
                # now do the update or insert
                self.do_import_membership_default(user, self.memb_data, memb, user_display)
                idata.save()
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

    def do_import_membership_default(self, user, memb_data, memb, action_info):
        """
        Database import here - insert or update
        """
        from tendenci.apps.corporate_memberships.models import CorpMembership

        user = user or User()
        username_before_assign = user.username

        # always remove user column
        if 'user' in self.field_names:
            self.field_names.remove('user')

        self.assign_import_values_from_dict(user, action_info['user_action'])

        user.username = user.username or spawn_username(
            fn=memb_data.get('first_name', u''),
            ln=memb_data.get('last_name', u''),
            em=memb_data.get('email', u''))

        # clean username
        user.username = re.sub(r'[^\w+-.@]', u'', user.username)

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
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(
                user=user,
                creator=self.request_user,
                creator_username=self.request_user.username,
                owner=self.request_user,
                owner_username=self.request_user.username,
                **self.private_settings)

        self.assign_import_values_from_dict(profile, action_info['user_action'])
        profile.user = user

        profile.status = True

        if not profile.status_detail:
            profile.status_detail = 'active'
        else:
            profile.status_detail = profile.status_detail.lower()

        # this is membership import - the 'expired' status_detail shouldn't be assigned to profile
        if profile.status_detail == 'expired':
            profile.status_detail = 'active'

        if profile.status_detail == 'active' and not profile.status:
            profile.status = True

        profile.save()

        # membership_demographic
        if self.mimport.num_processed == 0:
            self.should_handle_demographic = self.has_demographic_fields(
                                        self.memb_data)
            self.should_handle_education = self.has_education_fields(
                                        self.memb_data)

        if self.should_handle_demographic:
            # process only if we have demographic fields in the import.
            demographic = MembershipDemographic.objects.get_or_create(
                                    user=user)[0]
            self.assign_import_values_from_dict(demographic,
                                                action_info['user_action'])
            demographic.save()

        if self.should_handle_education:
            educations = user.educations.all().order_by('pk')[0:4]
            for x in range(1, 5):
                school = memb_data.get('school%s' % x, '')
                major = memb_data.get('major%s' % x, '')
                degree = memb_data.get('degree%s' % x, '')
                graduation_year = memb_data.get('graduation_year%s' % x, 0)
                try:
                    graduation_year = int(graduation_year)
                except ValueError:
                    graduation_year = 0
                if any([school, major, degree, graduation_year]):
                    try:
                        education = educations[x-1]
                    except IndexError:
                        education = Education(user=user)
                    education.school =school
                    education.major = major
                    education.degree = degree
                    education.graduation_year = graduation_year
                    education.save()

        # membership
        if not memb:
            memb = MembershipDefault(
                    user=user)

        self.assign_import_values_from_dict(memb, action_info['memb_action'])
        if not memb.creator:
            memb.creator = self.request_user
        if not memb.creator_username:
            memb.creator_username = self.request_user.username
        if not memb.owner:
            memb.owner = self.request_user
        if not memb.owner_username:
            memb.owner_username = self.request_user.username
        if not memb.entity:
            memb.entity_id = 1
        if not memb.lang:
            memb.lang = 'eng'

        # Set status to True
        # The False status means DELETED - It would defeat the purpose of import
        memb.status = True

        if not memb.status_detail:
            memb.status_detail = 'active'
        else:
            memb.status_detail = memb.status_detail.lower()
            if memb.status_detail not in VALID_MEMBERSHIP_STATUS_DETAIL:
                memb.status_detail = 'active'

        # membership type
        if not hasattr(memb, "membership_type") or not memb.membership_type:
            # last resort - pick the first available membership type
            memb.membership_type = MembershipType.objects.all(
                                            ).order_by('id')[0]

        # no join_dt - set one
        if not hasattr(memb, 'join_dt') or not memb.join_dt:
            if memb.status and memb.status_detail == 'active':
                memb.join_dt = datetime.now()

        # no application_approved_dt - set one
        if not hasattr(memb, 'application_approved_dt') or not memb.application_approved_dt:
            if memb.status and memb.status_detail == 'active':
                memb.application_approved = True
                memb.application_approved_dt = memb.join_dt
                memb.application_approved_denied_dt = memb.join_dt

        # no expire_dt - get it via membership_type
        if not hasattr(memb, 'expire_dt') or not memb.expire_dt:
            if memb.membership_type:
                expire_dt = memb.membership_type.get_expiration_dt(
                                            join_dt=memb.join_dt)
                setattr(memb, 'expire_dt', expire_dt)

        # check corp_profile_id
        if memb.corporate_membership_id:
            if not memb.corp_profile_id:
                [corp_profile_id] = CorpMembership.objects.filter(
                                    id=memb.corporate_membership_id
                                    ).values_list(
                                'corp_profile_id',
                                flat=True)[:1] or [None]
                if corp_profile_id:
                    memb.corp_profile_id = corp_profile_id

        memb.save()

        memb.is_active = self.is_active(memb)

        # member_number
        if not memb.member_number:
            if memb.is_active:
                memb.member_number = memb.set_member_number()
                memb.save()
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
        elif instance.__class__ == MembershipDemographic:
            assign_to_fields =self.membershipdemographic_fields
        else:
            assign_to_fields = self.membership_fields

        for field_name in self.field_names:
            if field_name in assign_to_fields:
                if any([
                        action == 'insert',
                        self.mimport.override,
                        not hasattr(instance, field_name) or
                        getattr(instance, field_name) == '' or
                        getattr(instance, field_name) is None
                        ]):
                    value = self.memb_data[field_name]
                    value = self.clean_data(value, assign_to_fields[field_name])

                    setattr(instance, field_name, value)

        # if insert, set defaults for the fields not in csv.
        for field_name in assign_to_fields:
            if field_name not in self.field_names and action == 'insert':
                if field_name not in self.private_settings:
                    value = self.get_default_value(assign_to_fields[field_name])

                    if value is not None:
                        setattr(instance, field_name, getattr(instance, field_name) or value)

    def get_default_value(self, field):
        # if allows null or has default, return None
        if field.null or field.has_default():
            return None

        field_type = field.get_internal_type()

        if field_type in ['BooleanField', 'NullBooleanField']:
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
            try:
                model = field.remote_field.parent_model()
            except AttributeError:
                model = field.remote_field.model
            [value] = model.objects.all()[:1] or [None]
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
                    if value in self.t4_timezone_map:
                        value = self.t4_timezone_map[value]
            try:
                value = field.to_python(value)
            except exceptions.ValidationError:
                if field.has_default():
                    value = field.get_default()
                else:
                    value = ''

        elif field_type in ['BooleanField', 'NullBooleanField']:
            try:
                if value in [True, 1, 'TRUE']:
                    value = True
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
                try:
                    model = field.remote_field.parent_model()
                except AttributeError:
                    model = field.remote_field.model
                [value] = model.objects.filter(pk=value)[:1] or [None]

            # membership_type - look up by name in case
            # they entered name instead of id
            if not value and field.name == 'membership_type':
                value = get_membership_type_by_name(orignal_value)

            if not value and not field.null:
                # if the field doesn't allow null, grab the first one.
                try:
                    model = field.remote_field.parent_model()
                except AttributeError:
                    model = field.remote_field.model
                [value] = model.objects.all().order_by('id')[:1] or [None]

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

def get_membership_app(membership):
    """
    Get app for membership if it is not associated with any app.
    """
    if not membership.app:
        apps = MembershipApp.objects.filter(status=True,
                                            status_detail__in=['active', 'published'])
        if membership.corporate_membership_id:
            apps = apps.filter(use_for_corp=True)

        for app in apps:
            mt_ids = app.membership_types.all().values_list('id', flat=True)
            if membership.membership_type_id in mt_ids:
                return app

    return None


def get_membership_summary_data():
    summary = []
    memb_types = MembershipType.objects.all()
    total_active = 0
    total_pending = 0
    total_expired = 0
    total_in_grace_period = 0
    total_total = 0
    now = datetime.now()
    for membership_type in memb_types:
        grace_period = membership_type.expiration_grace_period
        date_to_expire = now - relativedelta(days=grace_period)
        mems = MembershipDefault.objects.filter(
                    membership_type=membership_type)
        active = mems.filter(status=True, status_detail='active')
        expired = mems.filter(status=True,
                              status_detail='expired')
        in_grace_period = mems.filter(status=True,
                              status_detail='active',
                              expire_dt__lte=now,
                              expire_dt__gt=date_to_expire)
        pending = mems.filter(status=True, status_detail__contains='ending')

        active_count = active.count()
        pend_count = pending.count()
        expired_count = expired.count()
        in_grace_period_count = in_grace_period.count()
        type_total = sum([active_count,
                          pend_count,
                          expired_count])

        total_active += active_count
        total_pending += pend_count
        total_expired += expired_count
        total_in_grace_period += in_grace_period_count
        total_total += type_total
        summary.append({
            'type': membership_type,
            'active': active_count,
            'pending': pend_count,
            'expired': expired_count,
            'in_grace_period': in_grace_period_count,
            'total': type_total,
        })

    return (sorted(summary, key=lambda x: x['type'].name),
        {'total_active': total_active,
         'total_pending': total_pending,
         'total_expired': total_expired,
         'total_in_grace_period': total_in_grace_period,
         'total_total': total_total})
