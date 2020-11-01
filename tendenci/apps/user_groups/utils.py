from builtins import str
from collections import OrderedDict
import time
from datetime import datetime, date
import csv

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
from django.urls import reverse
from django.template.loader import render_to_string

from tendenci.apps.user_groups.models import Group
from tendenci.apps.profiles.models import Profile
#from tendenci.apps.base.utils import UnicodeWriter
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.emails.models import Email
from tendenci.apps.base.utils import escape_csv

def member_choices(group, member_label):
    """
    Creates a list of 2 tuples of a user's pk and the selected
    member label. This is used for generating choices for a form.
    choices for member label are: email, full name and username.
    """
    members = User.objects.all().order_by('username')
    if member_label == 'email':
        def label(x):
            return x.email
    elif member_label == 'full_name':
        def label(x):
            return x.get_full_name()
    else:
        def label(x):
            return x.username
    choices = []
    for member in members:
        choices.append((member.pk, label(member)))
    return choices


def get_default_group():
    """
    Get the ID of the default group specified in the global setting
    """
    return Group.objects.get_initial_group_id()


def process_export(
        group_id,
        export_target='all',
        identifier=u'', user_id=0):
    """
    Process export for group members and/or group subscribers.
    """

    [group] = Group.objects.filter(id=group_id)[:1] or [None]
    if not group:
        return

    # pull 100 rows per query
    # be careful of the memory usage
    rows_per_batch = 100

    identifier = identifier or str(time.time())
    file_dir = 'export/groups/'

    file_path_temp = '%sgroup_%d_%s_%s_temp.csv' % (file_dir,
                                                 group.id,
                                                 export_target,
                                                identifier)

    # labels
    user_fields = ['id',
                   'first_name',
                   'last_name',
                   'email',
                   'username',
                   'is_active',
                   'is_staff',
                   'is_superuser']
    profile_fields = ['direct_mail',
                      'company',
                      'department',
                      'position_title',
                      'address',
                      'address2',
                      'city',
                      'state',
                      'zipcode',
                      'country',
                      'region',
                      'phone',
                      'notes',
                      'referral_source',
                      'create_dt']
    labels = user_fields + profile_fields

    field_dict = OrderedDict([(label.lower().replace(" ", "_"), ''
                               ) for label in labels])

    with default_storage.open(file_path_temp, 'w') as csvfile:        
        csv_writer = csv.DictWriter(csvfile, fieldnames=list(field_dict.keys()))
        csv_writer.writeheader()

        # process regular group members
        count_members = group.members.filter(
            group_member__status=True,
            group_member__status_detail='active').count()
        num_rows_processed = 0
        while num_rows_processed < count_members:
            users = group.members.filter(
                group_member__status=True,
                group_member__status_detail='active'
                ).select_related('profile'
                ).order_by('group_member__member_id')[num_rows_processed:(num_rows_processed + rows_per_batch)]
            num_rows_processed += rows_per_batch
            row_dict = field_dict.copy()
            for user in users:
                if hasattr(user, 'profile'):
                    profile = user.profile
                else:
                    profile = Profile.objects.create_profile(user)
                for field_name in user_fields:
                    if hasattr(user, field_name):
                        row_dict[field_name] = getattr(user, field_name)
                for field_name in profile_fields:
                    if hasattr(profile, field_name):
                        row_dict[field_name] = getattr(profile, field_name)
                for k, v in row_dict.items():
                    if not isinstance(v, str):
                        if isinstance(v, datetime):
                            row_dict[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                        elif isinstance(v, date):
                            row_dict[k] = v.strftime('%Y-%m-%d')
                        else:
                            row_dict[k] = smart_str(v)
                    else:
                        row_dict[k] = escape_csv(v)

                csv_writer.writerow(row_dict)

    # rename the file name
    file_path = '%sgroup_%d_%s_%s.csv' % (file_dir,
                                          group.id,
                                          export_target,
                                          identifier)
    default_storage.save(file_path, default_storage.open(file_path_temp, 'rb'))

    # delete the temp file
    default_storage.delete(file_path_temp)

    # notify user that export is ready to download
    [user] = User.objects.filter(id=user_id)[:1] or [None]
    if user and user.email:
        download_url = reverse('group.members_export_download',
                               args=[group.slug, export_target, identifier])
        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'group': group,
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name}

        subject = render_to_string(
            template_name='user_groups/exports/export_ready_subject.html', context=parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            template_name='user_groups/exports/export_ready_body.html', context=parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)

        email.send()
