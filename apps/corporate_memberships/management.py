from django.db.models.signals import post_syncdb
#from django.contrib.contenttypes.models import ContentType
from perms.utils import update_admin_group_perms

# assign permissions to the admin auth group
def assign_permissions(app, created_models, verbosity, **kwargs):
    update_admin_group_perms()

from corporate_memberships import models as corporate_membership
post_syncdb.connect(assign_permissions, sender=corporate_membership)


from django.conf import settings
from django.utils.translation import ugettext_noop as _

#renewal notifications:
#    on renewal: 
#        send email to dues reps (corp_memb_renewed_user)
#        send email to admin (corp_memb_renewed)
#
#    on approval:
#        send email to dues reps (corp_memb_renewal_approved)
#
#    after being paid - credit card payment:
#        send email to admin (corp_memb_paid)

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("corp_memb_added", _("Corporate Membership Added"), 
                                        _("A corporate membership has been added."))
        notification.create_notice_type("corp_memb_added_user", _("Corporate Membership Added User Notice"), 
                                        _("A corporate membership has been added - notice to user."))
        notification.create_notice_type("corp_memb_edited", _("Corporate Membership Edited"), 
                                        _("A corporate membership  has been edited."))
        notification.create_notice_type("corp_memb_renewed", _("Corporate Membership Renewed"), 
                                        _("A corporate membership has been renewed."))
        notification.create_notice_type("corp_memb_renewed_user", _("Corporate Membership Renewal User Notice"), 
                                        _("A corporate membership has been renewed - notice to user."))
        notification.create_notice_type("corp_memb_join_approved", _("Corporate Membership Approved"), 
                                        _("A new corporate membership has been approved."))
        notification.create_notice_type("corp_memb_renewal_approved", _("Corporate Membership Renewal Approved"), 
                                        _("The corporate membership renewal has been approved."))
        notification.create_notice_type("corp_memb_paid", _("Payment Received for Corporate Membership"), 
                                        _("Payment for a corporate membership has been received."))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"