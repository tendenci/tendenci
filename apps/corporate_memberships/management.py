from django.db.models.signals import post_syncdb
#from django.contrib.contenttypes.models import ContentType
from perms.utils import update_admin_group_perms

# assign permissions to the admin auth group
def assign_permissions(app, created_models, verbosity, **kwargs):
    update_admin_group_perms()

from corporate_memberships import models as corporate_membership
post_syncdb.connect(assign_permissions, sender=corporate_membership)