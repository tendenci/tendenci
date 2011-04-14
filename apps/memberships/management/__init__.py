from django.db.models.signals import post_syncdb
from django.utils.translation import ugettext_noop as _
from perms.utils import update_admin_group_perms
from memberships import models as membership
from notification import models as notification

# assign permissions to the admin auth group
def assign_permissions(app, created_models, verbosity, **kwargs):
    update_admin_group_perms()

post_syncdb.connect(assign_permissions, sender=membership)

def create_notice_types(app, created_models, verbosity, **kwargs):

    notification.create_notice_type(
        'membership_approved_to_admin',
        _('Membership Application Approved'),
        _('Membership Application Approved'))

    notification.create_notice_type(
        'membership_disapproved_to_admin',
        _('Membership Application Disapproved'),
        _('Membership Application Disapproved'))

    notification.create_notice_type(
        'membership_approved_to_member',
        _('Membership Application Approved'),
        _('Membership Application Approved'))

    notification.create_notice_type(
        'membership_disapproved_to_member',
        _('Membership Application Disapproved'),
        _('Membership Application Disapproved'))

post_syncdb.connect(create_notice_types, sender=notification)