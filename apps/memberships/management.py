from django.db.models.signals import post_syncdb
#from django.contrib.contenttypes.models import ContentType
from perms.utils import update_admin_group_perms

# assign permissions to the admin auth group
def assign_permissions(app, created_models, verbosity, **kwargs):
    update_admin_group_perms()

from memberships import models as membership
post_syncdb.connect(assign_permissions, sender=membership)
