"""Social auth models"""
from builtins import str
import warnings
from datetime import timedelta

from django.db import models
from django.apps import apps
from django.conf import settings

from tendenci.apps.social_auth.fields import JSONField

# If User class is overridden, it *must* provide the following fields,
# or it won't be playing nicely with django.contrib.auth module:
#   username         = CharField()
#   last_login       = DateTimeField()
#   is_active        = BooleanField()
#   is_authetnicated = BooleanField()
RECOMMENDED_FIELDS = ('username', 'last_login', 'is_active')
RECOMMENDED_METHODS = ('is_authenticated',)

if getattr(settings, 'SOCIAL_AUTH_USER_MODEL', None):
    User = apps.get_model(*settings.SOCIAL_AUTH_USER_MODEL.split('.'))
    missing = (list(set(RECOMMENDED_FIELDS)) -
               [f.name for f in User._meta.get_fields()] +
               [name for name in RECOMMENDED_METHODS
                if not callable(getattr(User, name, None))])
    if missing:
        warnings.warn('Missing recommended attributes or methods '
                      'in custom User model: "%s"' % ', '.join(missing))
else:
    from django.contrib.auth.models import User


class UserSocialAuth(models.Model):
    """Social Auth association model"""
    user = models.ForeignKey(User, related_name='social_auth', on_delete=models.CASCADE)
    provider = models.CharField(max_length=32)
    uid = models.CharField(max_length=255)
    extra_data = JSONField(blank=True)

    class Meta:
        """Meta data"""
        unique_together = ('provider', 'uid')
        app_label = 'social_auth'

    def __str__(self):
        """Return associated user unicode representation"""
        return str(self.user)

    def expiration_delta(self):
        """Return saved session expiration seconds if any. Is retuned in
        the form of a timedelta data type. None is returned if there's no
        value stored or it's malformed.
        """
        if self.extra_data:
            name = getattr(settings, 'SOCIAL_AUTH_EXPIRATION', 'expires')
            try:
                return timedelta(seconds=int(self.extra_data.get(name)))
            except (ValueError, TypeError):
                pass
        return None


class Nonce(models.Model):
    """One use numbers"""
    server_url = models.CharField(max_length=255)
    timestamp = models.IntegerField()
    salt = models.CharField(max_length=40)

    class Meta:
        app_label = 'social_auth'

    def __str__(self):
        """Unicode representation"""
        return self.server_url


class Association(models.Model):
    """OpenId account association"""
    server_url = models.CharField(max_length=255)
    handle = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)  # Stored base64 encoded
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.CharField(max_length=64)

    class Meta:
        app_label = 'social_auth'

    def __str__(self):
        """Unicode representation"""
        return '%s %s' % (self.handle, self.issued)
