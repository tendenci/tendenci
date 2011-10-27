from django.db import models
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
        if self.name == 'theme':
            from theme.utils import theme_options
            self.input_value = theme_options()
            super(Setting, self).save(*args, **kwargs)
            call_command('touch_settings')
        else:
            super(Setting, self).save(*args, **kwargs)
