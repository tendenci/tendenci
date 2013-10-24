import re
from string import digits
from random import choice

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q

from tendenci.apps.user_groups.models import GroupMembership, Group
from tendenci.addons.memberships.models import Membership, App
from tendenci.core.perms.utils import get_query_filters
from tendenci.core.site_settings.utils import get_setting


def profile_edit_admin_notify(request, old_user, old_profile, profile, **kwargs):
    from django.core.mail.message import EmailMessage
    from django.template.loader import render_to_string
    from django.conf import settings
    from django.template import RequestContext
    
    subject = 'User Account Modification Notice for %s' % get_setting('site', 'global', 'sitedisplayname')
    body = render_to_string('profiles/edit_notice.txt', 
                               {'old_user':old_user,
                                'old_profile': old_profile, 
                                'profile': profile},
                               context_instance=RequestContext(request))
   
    sender = settings.DEFAULT_FROM_EMAIL
    recipients = ['%s<%s>' % (r[0], r[1]) for r in settings.ADMINS]
    msg = EmailMessage(subject, body, sender, recipients)
    msg.content_subtype = 'html'
    try:
        msg.send()
    except:
        pass
    
# return admin auth group as a list    
def get_admin_auth_group(name="Admin"):
    from django.contrib.auth.models import Group as Auth_Group
    
    try:
        auth_group = Auth_Group.objects.get(name=name)
    except Auth_Group.DoesNotExist:
        auth_group = Auth_Group(name=name)
        auth_group.save()
    
    return auth_group

def user_add_remove_admin_auth_group(user, auth_group=None):
    """
    if user is admin and not on admin auth group, add them.
    if user is not admin but on admin auth group, remove them
    """
    if user.is_staff and (not user.is_superuser):   # they are admin
        if not auth_group:
            if hasattr(settings, 'ADMIN_AUTH_GROUP_NAME'):
                auth_group_name = settings.ADMIN_AUTH_GROUP_NAME
            else:
                auth_group_name = 'Admin'
            auth_group = get_admin_auth_group(name=auth_group_name)
            
      
        if not user.id: # new user
            user.groups = [auth_group]
            user.save()
            
        else:           # existing user
            group_updated = False
            user_edit_auth_groups = user.groups.all()
            if user_edit_auth_groups:
                if auth_group not in user_edit_auth_groups:
                    user_edit_auth_groups.append(auth_group)
                    user.groups = user_edit_auth_groups
                    group_updated = True
            else:
                user.groups = [auth_group]
                group_updated = True
                    
            if group_updated:
                user.save()
                    
    else:
        if user.id:
            user.groups = []
            user.save()
        
def get_groups(user, filter=None):
    """
    Returns the groups of a given user.
    if filter is given it will filter the user's groups based on it.
    filter is assumed to be a QuerySet or a SearchQuerySet of Group.
    """
    memberships = GroupMembership.objects.filter(member=user)
    
    if filter:
        pks = [group.pk for group in filter]
        memberships = memberships.filter(group__pk__in = pks)
        
    groups = []
    for member in memberships:
        groups.append(member.group)
        
    return groups
    
def get_memberships(user, filter=None):
    """
    Returns the memberships of a given user.
    if filter is given it will filter the user's memberships based on it.
    filter is assumed to be a QuerySet or a SearchQuerySet of Group.
    """
    memberships = GroupMembership.objects.filter(member=user)
    
    if filter:
        pks = [group.pk for group in filter]
        memberships = memberships.filter(group__pk__in = pks)
        
    return memberships
    
def group_choices(user):
    """
    returns a list of (group.pk, group.label) for groups viewable
    for the given user.
    """

    filters = get_query_filters(user, 'groups.view_group', perms_field=False)
    groups = Group.objects.filter(filters).exclude(type="membership").distinct()

    if not user.profile.is_superuser:
        groups = groups.exclude(allow_self_add=False)

    choices = [(group.pk, "%s (%s)" % (group.label, group.name)) for group in groups]

    return choices


def update_user(user, **kwargs):
    for k, v in kwargs.iteritems():
        if hasattr(user, k):
            setattr(user, k, v)
    user.save()


def make_username_unique(un):
    """
    Requires a string parameter.
    Returns a unique username by appending
    a digit to the end of the username.
    """
    others = []  # find similiar usernames
    for u in User.objects.filter(username__startswith=un):
        if u.username.replace(un, '0').isdigit():
            others.append(int(u.username.replace(un, '0')))

    if others and 0 in others:
        # the appended digit will compromise the username length
        un = '%s%s' % (un, unicode(max(others) + 1))

    return un


def spawn_username(fn=u'', ln=u'', em=u''):
    """
    Uses a first name, last name and email to
    spawn a typical username.  All usernames are
    lowercase.  All usernames are unique.

    Usernames generated via first or last name will only
    contain letters, digits, and periods.

    Usernames generated via the email address may contain
    letters, digits, underscores, hypens, periods and at-symbols

    Usernames that 100% auto-generated start with 'user.' and end
    with 10 digits which can later be replaced by the user primary key.
    Example user.3482938481
    """

    django_max_un_length = 30
    max_length = django_max_un_length - 3  # to account for appended numbers

    # only letters and digits
    fn = re.sub('[^A-Za-z0-9]', u'', fn)
    ln = re.sub('[^A-Za-z0-9]', u'', ln)

    # only letters digits underscores dashes @ + .
    em = re.sub('[^\w@+.-]', u'', em)

    if fn and ln:
        un = '%s.%s' % (fn, ln)
        return make_username_unique(un[:max_length].lower())

    if fn:
        return make_username_unique(fn[:max_length].lower())

    if ln:
        return make_username_unique(ln[:max_length].lower())

    if em:
        return make_username_unique(em.split('@')[0][:max_length].lower())

    int_string = ''.join([choice(digits) for x in xrange(10)])
    return 'user.%s' % int_string


def get_member_reminders(user):
    active_qs = Q(status_detail__iexact='active')
    expired_qs = Q(status_detail__iexact='expired')

    memberships = user.membershipdefault_set.filter(
        status=True) & user.membershipdefault_set.filter(
            active_qs | expired_qs).order_by('expire_dt')

    reminders = ()
    for membership in memberships:

        renew_link = u''
        if hasattr(membership, 'app') and membership.app:
            renew_link = '%s%s?username=%s&membership_type_id=%s' % (
                get_setting('site', 'global', 'siteurl'),
                reverse('membership_default.add',
                        kwargs={'slug': membership.app.slug}),
                membership.user.username,
                membership.membership_type.pk)

        if membership.in_grace_period() or membership.is_expired():
            if membership.can_renew():
                # expired but can renew
                message = 'Your membership for %s has expired. Renewal is available until %s.' % (
                    membership.membership_type.name,
                    membership.get_renewal_period_end_dt().strftime('%d-%b-%Y %I:%M %p'))
                reminders += ((message, renew_link, 'Renew your membership now'),)
            else:
                # expired and out of renewal period
                message = 'Your membership for %s has expired.' % (
                    membership.membership_type.name)
                reminders += ((message, renew_link, 'Re-register as a member here'),)
        else:
            # not expired, but in renewal period
            if membership.can_renew():
                message = 'Your membership for %s will expire on %s. Renewal is available until %s.' % (
                    membership.membership_type.name,
                    membership.expire_dt.strftime('%d-%b-%Y'),
                    membership.get_renewal_period_end_dt().strftime('%d-%b-%Y %I:%M %p')
                )
                reminders += ((message, renew_link, 'Renew your membership here'),)

    return reminders


def clean_username(username):
    """
    Removes improper characters from a username
    """
    bad_characters = " !#$%^&*()[]'\""

    for char in bad_characters:
        if char in username:
            username = username.replace(char, '')

    return username
