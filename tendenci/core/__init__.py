from django.db.models import signals
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app
from django.contrib.auth.models import User

def create_initial_superuser(sender, **kwargs):
    users = User.objects.all()
    if not users:
        u = User()
        u.username = 'admin'
        u.email = ''
        u.is_active = False
        u.is_staff = False
        u.is_superuser = False
        u.set_unusable_password()
        u.save()

signals.post_syncdb.disconnect(
    create_superuser,
    sender=auth_app,
    dispatch_uid = "django.contrib.auth.management.create_superuser")

signals.post_syncdb.connect(
    create_initial_superuser,
    sender=auth_app,
    weak=False)
