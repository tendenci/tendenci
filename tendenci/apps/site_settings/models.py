from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.conf import settings
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
        return ("setting.permalink",
                [self.scope, self.scope_category, "%s%s" % ('#id_', self.name)])
    get_absolute_url = models.permalink(get_absolute_url)

    def __unicode__(self):
        return "(%s) %s" %(self.name, self.label)

    def set_value(self, value):
        self.value = encrypt(value)
        self.is_secure = True

    def get_value(self):
        try:
            if self.is_secure:
                try:
                    return decrypt(self.value).decode('utf-8')
                except UnicodeDecodeError:
                    return decrypt(self.value)
        except AttributeError: #cached setting with no is_secure
            from tendenci.apps.site_settings.utils import (
                delete_setting_cache,
                delete_all_settings_cache)
            # delete the cache for this setting
            # print "clearing cache for setting: %s" % self.name
            delete_all_settings_cache()
            delete_setting_cache(self.scope, self.scope_category, self.name)

        return self.value

    def save(self, *args, **kwargs):
        """The save method is overwritten because settings are referenced
        in several different ways. This is the cental command if we
        want to incorporate a process applicable for all those ways.
        Using signals is also feasable however there is a process order
        that must be followed (e.g. caching new value if not equal to old value)
        so we can leave that for a later time.
        """
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
            from tendenci.apps.site_settings.cache import SETTING_PRE_KEY

            # delete the cache for all the settings to reset the context
            delete_all_settings_cache()
            # delete and set cache for single key and save the value in the database
            delete_setting_cache(self.scope, self.scope_category, self.name)
            cache_setting(self.scope, self.scope_category, self.name, self)
