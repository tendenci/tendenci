from django.contrib.auth.models import User
from django.contrib.auth.models import Group as Auth_Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from profiles.models import Profile
from perms.object_perms import ObjectPermission

from haystack.query import SearchQuerySet
from haystack.backends import SQ


def set_perm_bits(request, form, instance):
    """
    Sets object-level permissions bits for a model instance
    """
    # owners and creators
    if not instance.pk:
        if request.user.is_authenticated():
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

    # set up user permissions
    if 'user_perms' in form.cleaned_data:
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']
    else:
        instance.allow_user_view, instance.allow_user_edit = False, False

    # set up member permissions
    if 'member_perms' in form.cleaned_data:
        instance.allow_member_view, instance.allow_member_edit = form.cleaned_data['member_perms']
    else:
        instance.allow_member_view, instance.allow_member_edit = False, False

    return instance


def update_perms_and_save(request, form, instance):
    """
    Adds object row-level permissions for a model instance
    """
    # permissions bits
    instance = set_perm_bits(request, form, instance)

    if not request.user.is_anonymous():
        if not instance.pk:
            if hasattr(instance, 'creator'):
                instance.creator = request.user
            if hasattr(instance, 'creator_username'):
                instance.creator_username = request.user.username

        if hasattr(instance, 'owner'):
            instance.owner = request.user
        if hasattr(instance, 'owner_username'):
            instance.owner_username = request.user.username

    # save the instance because we need the primary key
    if instance.pk:
        ObjectPermission.objects.remove_all(instance)
    else:
        instance.save()

    # assign permissions for selected groups
    if 'group_perms' in form.cleaned_data:
        ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], instance)

    # assign creator permissions
    if request.user.is_authenticated():
        ObjectPermission.objects.assign(instance.creator, instance)

    # save again for indexing purposes
    # TODO: find a better solution, saving twice kinda sux
    instance.save()

    return instance


def has_perm(user, perm, obj=None):
    """
        A simple wrapper around the user.has_perm
        functionality.

        It checks for impersonation and has high
        hopes for future checks with friends and
        settings functionalities.
    """
    # check to see if there is impersonation
    if hasattr(user, 'impersonated_user'):
        if isinstance(user.impersonated_user, User):
            # check the logged in users permissions
            logged_in_has_perm = user.has_perm(perm, obj)
            if not logged_in_has_perm:
                return False
            else:
                impersonated_has_perm = user.impersonated_user.has_perm(perm, obj)
                if not impersonated_has_perm:
                    return False
                else:
                    return True
    else:
        return user.has_perm(perm, obj)


def is_member(user):
    """
    Test a user instance to see if they have a membership
    """
    if not user or user.is_anonymous():
        return False

    if hasattr(user, 'is_member'):
        return getattr(user, 'is_member')
    else:
        try:
            membership = user.memberships.get_membership()
            if user.is_active:
                status = membership.status == 1
                active = membership.status_detail.lower() == 'active'
                if all([status, active]):
                    setattr(user, 'is_member', True)
                    return True
        except:
            setattr(user, 'is_member', False)
            return False


def is_admin(user):
    if not user or user.is_anonymous():
        return False

    if hasattr(user, 'impersonated_user'):
        if isinstance(user.impersonated_user, User):
            user = user.impersonated_user
    if hasattr(user, 'is_admin'):
        return getattr(user, 'is_admin')
    else:
        try:
            profile = user.get_profile()
        except Profile.DoesNotExist:
            profile = Profile.objects.create_profile(user=user)
        if user.is_staff and user.is_active and profile.status == 1 \
                and profile.status_detail.lower() == 'active':
            setattr(user, 'is_admin', True)
            return True
        else:
            setattr(user, 'is_admin', False)
            return False


def is_developer(user):
    if not user or user.is_anonymous():
        return False

    if hasattr(user, 'is_developer'):
        return getattr(user, 'is_developer')
    else:
        try:
            profile = user.get_profile()
        except Profile.DoesNotExist:
            profile = Profile.objects.create_profile(user=user)
        if user.is_superuser and user.is_staff and user.is_active \
                and profile.status == 1 \
                and profile.status_detail.lower() == 'active':
            setattr(user, 'is_developer', True)
            return True
        else:
            setattr(user, 'is_developer', False)
            return False


def get_administrators():
    return User.objects.filter(is_active=True, is_staff=True)


# get a list of the admin notice recipients
def get_notice_recipients(scope, scope_category, setting_name):
    from site_settings.utils import get_setting
    from django.core.validators import email_re

    recipients = []
    # global recipients
    g_recipients = (get_setting('site', 'global', 'allnoticerecipients')).split(',')
    g_recipients = [r.strip() for r in g_recipients]

    # module recipients
    m_recipients = (get_setting(scope, scope_category, setting_name)).split(',')
    m_recipients = [r.strip() for r in m_recipients]

    # consolidate [remove duplicate email address]
    for recipient in list(set(g_recipients + m_recipients)):
        if email_re.match(recipient):
            recipients.append(recipient)

    # if the settings for notice recipients are not set up, return admin contact email
    if not recipients:
        admin_contact_email = (get_setting('site', 'global', 'admincontactemail')).strip()
        recipients = admin_contact_email.split(',')

    return recipients


# create Admin auth group if not exists and assign all permisstions (but auth) to it
def update_admin_group_perms():
    if hasattr(settings, 'ADMIN_AUTH_GROUP_NAME'):
        name = settings.ADMIN_AUTH_GROUP_NAME
    else:
        name = 'Admin'

    try:
        auth_group = Auth_Group.objects.get(name=name)
    except Auth_Group.DoesNotExist:
        auth_group = Auth_Group(name=name)
        auth_group.save()

    # assign permission to group, but exclude the auth content
    content_to_exclude = ContentType.objects.filter(app_label='auth')
    permissions = Permission.objects.all().exclude(content_type__in=content_to_exclude)
    auth_group.permissions = permissions
    auth_group.save()


def _specific_view(user, obj):
    """
    determines if a user has specific permissions to view the object.
    note this is based only on:

    (users_can_view contains user)
    +
    (groups_can_view contains one of user's groups)
    """
    sqs = SearchQuerySet()
    sqs = sqs.models(obj.__class__)

    groups = [g.pk for g in user.group_set.all()]

    q_primary_key = SQ(primary_key=obj.pk)
    q_groups = SQ(groups_can_view__in=groups)
    q_users = SQ(users_can_view__in=[user.pk])

    if groups:
        sqs = sqs.filter(q_primary_key & (q_groups | q_users))
    else:
        sqs = sqs.filter(q_primary_key & q_users)

    if sqs:
        return True

    return False


def can_view(user, obj):
    """
    Checks for tendenci specific permissions to viewing objects
    through the search index
    """
    return _specific_view(user, obj)
