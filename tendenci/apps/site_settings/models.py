from urllib.parse import urlparse
from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.management import call_command
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.site_settings.crypt import encrypt, decrypt


INPUT_TYPE_CHOICES = (
    ('text',_('Text')),
    ('textarea', _('Textarea')),
    ('select',_('Select')),
    ('file', _('File')),
)

DATA_TYPE_CHOICES = (
    ('string',_('string')),
    ('boolean',_('boolean')),
    ('integer',_('int')),
    ('file', _('file')),
    ('decimal', _('decimal')),
)

class Setting(models.Model):
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=255)
    description = models.TextField()
    data_type = models.CharField(max_length=10, choices=DATA_TYPE_CHOICES)
    value = models.TextField(blank=True)
    default_value = models.TextField(blank=True)
    input_type = models.CharField(max_length=25, choices=INPUT_TYPE_CHOICES)
    input_value = models.CharField(max_length=1000, blank=True)
    client_editable = models.BooleanField(default=True)
    store = models.BooleanField(default=True)
    update_dt = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True)
    scope = models.CharField(max_length=50)
    scope_category = models.CharField(max_length=50)
    parent_id = models.IntegerField(blank=True, default=0)
    is_secure = models.BooleanField(default=False)

    class Meta:
        app_label = 'site_settings'

    def get_absolute_url(self):
        return reverse("setting.permalink",
                args=[self.scope, self.scope_category, self.name]).replace('%23', '#')

    def __str__(self):
        return "(%s) %s" %(self.name, self.label)

    def set_value(self, value):
        self.value = encrypt(value)
        self.is_secure = True

    def get_value(self):
        try:
            if self.is_secure:
                return decrypt(self.value)
        except AttributeError: #cached setting with no is_secure
            from tendenci.apps.site_settings.utils import (
                delete_setting_cache,
                delete_all_settings_cache)
            # delete the cache for this setting
            # print("clearing cache for setting: %s" % self.name)
            delete_all_settings_cache()
            delete_setting_cache(self.scope, self.scope_category, self.name)

        return self.value

    def save(self, *args, **kwargs):
        """The save method is overwritten because settings are referenced
        in several different ways. This is the central command if we
        want to incorporate a process applicable for all those ways.
        Using signals is also feasible however there is a process order
        that must be followed (e.g. caching new value if not equal to old value)
        so we can leave that for a later time.
        """
        # Django 1.10 and later no longer accept "true" or "false" strings for
        # BooleanField values.  Since these are used in many existing theme
        # settings files, we must still support them.
        if self.client_editable in ('true', 'false'):
            self.client_editable = self.client_editable == 'true'
        if self.store in ('true', 'false'):
            self.store = self.store == 'true'
        if self.is_secure in ('true', 'false'):
            self.is_secure = self.is_secure == 'true'

        try:
            #get the old value as reference for updating the cache
            orig = Setting.objects.get(pk = self.pk)
        except Setting.DoesNotExist:
            orig = None

        #call touch settings if this is the setting theme
        if self.name == 'theme':
            from tendenci.apps.theme.utils import theme_options
            self.input_value = theme_options()
            super(Setting, self).save(*args, **kwargs)
            call_command('clear_theme_cache')
        else:
            super(Setting, self).save(*args, **kwargs)

        #update the cache when value has changed
        if orig and self.value != orig.value:
            from tendenci.apps.site_settings.utils import (delete_setting_cache,
                cache_setting, delete_all_settings_cache)

            # delete the cache for all the settings to reset the context
            delete_all_settings_cache()
            # delete and set cache for single key and save the value in the database
            delete_setting_cache(self.scope, self.scope_category, self.name)
            cache_setting(self.scope, self.scope_category, self.name, self)

    def update_site_domain(self, site_url):
        """
        Update the site domain if site url setting is changed
        """
        if self.name == "siteurl" and self.scope == "site":
            if site_url:
                django_site = Site.objects.get(pk=settings.SITE_ID)
                if urlparse(site_url).scheme == "":
                    # prefix https:// if no scheme
                    site_url = 'https://%s' % site_url
                netloc = urlparse(site_url).netloc
                django_site.domain = netloc
                django_site.name = netloc
                django_site.save()
