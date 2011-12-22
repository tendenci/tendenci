from django.db import models

# format is ModelField/FormField/SearchIndexField
field_choices = (
    ('IntegerField/IntegerField/IntegerField', 'Integer'),
    ('BooleanField/BooleanField/BooleanField', 'Boolean'),
    ('CharField/CharField/CharField', 'Text (single line)'),
    ('TextField/TextField/CharField', 'Text (multi line)'),
    ('TextField/Wysiwyg/CharField', 'Wysiwyg'),
    ('DateTimeField/DateTimeField/DateTimeField', 'Date/Time'),
)

class Plugin(models.Model):
    single_caps = models.CharField(max_length=50)
    single_lower = models.CharField(max_length=50)
    plural_caps = models.CharField(max_length=50)
    plural_lower = models.CharField(max_length=50)
    event_id = models.IntegerField()
    
    def __unicode__(self):
        return self.plural_lower

class PluginField(models.Model):
    class Meta:
        unique_together = (('plugin', 'name'),)
    plugin = models.ForeignKey(Plugin, related_name='fields')
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=field_choices)
    default = models.CharField(max_length=50, blank=True, null=True)
    required = models.BooleanField(default=True)
    help_text = models.CharField(max_length=100, blank=True, null=True)
    kwargs = models.CharField(max_length=100, help_text="Extra keyword arguments.", blank=True, null=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.plugin, self.name)
