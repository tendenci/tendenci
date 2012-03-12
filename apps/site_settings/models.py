from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command

INPUT_TYPE_CHOICES = (
    ('text','Text'),
    ('select','Select'),         
    ('file', 'File'),
)

DATA_TYPE_CHOICES = (
    ('string','string'),
    ('boolean','boolean'),
    ('integer','int'),         
    ('file', 'file'),
)


class Setting(models.Model):
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=255)
    description = models.TextField()
    data_type = models.CharField(max_length=10, choices=DATA_TYPE_CHOICES)
    value = models.TextField(blank=True)
    default_value = models.TextField(blank=True)
    input_type = models.CharField(max_length=25, choices=INPUT_TYPE_CHOICES)
    input_value = models.CharField(max_length=255, blank=True)
    client_editable = models.BooleanField(default=True)
    store = models.BooleanField(default=True)
    update_dt = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True)
    scope = models.CharField(max_length=50)
    scope_category = models.CharField(max_length=50)
    parent_id = models.IntegerField(blank=True, default=0)

    def get_absolute_url(self):
        return ("setting.permalink", 
                [self.scope, self.scope_category, "%s%s" % ('#id_', self.name)])
    get_absolute_url = models.permalink(get_absolute_url)

    def __unicode__(self):
        return "(%s) %s" %(self.name, self.label)
        
    def save(self, *args, **kwargs):
        try:
            #get the old value as reference for updating the cache
            orig = Setting.objects.get(pk = self.pk)
        except Setting.DoesNotExist:
            orig = None
            
        if self.name == 'theme':
            from theme.utils import theme_options
            self.input_value = theme_options()
            super(Setting, self).save(*args, **kwargs)
            call_command('touch_settings')
        else:
            super(Setting, self).save(*args, **kwargs)
        
        #update the cache when value has changed
        if orig and self.value != orig.value:
            from site_settings.utils import (delete_setting_cache,
                cache_setting, delete_all_settings_cache)
            from site_settings.cache import SETTING_PRE_KEY
            # delete the cache for all the settings to reset the context
            delete_all_settings_cache()
            # delete and set cache for single key and save the value in the database
            delete_setting_cache(self.scope, self.scope_category, self.name)
            cache_setting(self.scope, self.scope_category, self.name, self)
