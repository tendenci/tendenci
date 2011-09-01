from django.db import models

field_choices = (
    ('int', 'Integer'),
    ('single_line', 'Text (single line)'),
    ('multi_line', 'Text (multi line)'),
    ('wysiwyg', 'Wysiwyg'),
    ('datetime', 'Date/Time'),
)

class Plugin(models.Model):
    single_caps = models.CharField(max_length=50)
    single_lower = models.CharField(max_length=50)
    plural_caps = models.CharField(max_length=50)
    plural_lower = models.CharField(max_length=50)

class PluginField(models.Model):
    plugin = models.ForeignKey(Plugin)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=field_choices)
    default = models.CharField(max_length=50, blank=True, null=True)
    blank = models.BooleanField(default=False)
    help_text = models.CharField(max_length=100, blank=True, null=True)
