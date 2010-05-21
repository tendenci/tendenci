from django.db import models

class Setting(models.Model):
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=255)
    description = models.TextField()
    data_type = models.CharField(max_length=10)
    value = models.TextField()
    default_value = models.TextField()
    input_type = models.CharField(max_length=25)
    input_value = models.CharField(max_length=255)
    client_editable = models.BooleanField()
    store = models.BooleanField()
    update_dt = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=50)
    scope = models.CharField(max_length=50)
    scope_category = models.CharField(max_length=50)
    parent_id = models.IntegerField()
    
    def __unicode__(self):
        return "(%s) %s" %(self.name, self.label)
