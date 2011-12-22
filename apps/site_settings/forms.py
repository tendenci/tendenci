from ordereddict import OrderedDict
from ast import literal_eval

from django import forms
from django.core.cache import cache
from django.core.files import File
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from site_settings.utils import (delete_setting_cache, cache_setting,
    delete_all_settings_cache, get_form_list, get_box_list)
from site_settings.cache import SETTING_PRE_KEY

def clean_settings_form(self):
    """
        Cleans data that has been set in the settings form
    """
    for setting in self.settings:
        try:
            field_value = self.cleaned_data[setting.name]
            if setting.data_type == "boolean":
                if field_value != 'true' and field_value != 'false':
                    raise forms.ValidationError("'%s' must be true or false" % setting.label)
            if setting.data_type == "int":
                if field_value != ' ':
                    if not field_value.isdigit():
                        raise forms.ValidationError("'%s' must be a whole number" % setting.label)
            if setting.data_type == "file":
                if field_value:
                    if not isinstance(field_value, File):
                        raise forms.ValidationError("'%s' must be a file" % setting.label)
        except KeyError:
            pass

        if setting.name == "siteurl" and setting.scope == "site":
            field_value = self.cleaned_data["siteurl"] 
            if field_value:
                if field_value[-1:] == "/":
                    field_value = field_value[:-1]
                self.cleaned_data[setting.name] = field_value

    return self.cleaned_data

    
def save_settings_form(self):
    """
        Save the updated settings in the database 
        Setting's save will trigger a cache update.
        If the field type is 'file' a file entry will be created.
    """
    for setting in self.settings:
        try:
            field_value = self.cleaned_data[setting.name]
            if setting.input_type == "file":
                if field_value:
                    # save a file object and set the value at that file object's id.
                    from files.models import File as TendenciFile
                    uploaded_file = TendenciFile()
                    uploaded_file.owner = self.user
                    uploaded_file.owner_username = self.user.username
                    uploaded_file.creator = self.user
                    uploaded_file.creator_username = self.user.username
                    uploaded_file.content_type = ContentType.objects.get(app_label="site_settings", model="setting")
                    uploaded_file.file.save(field_value.name, File(field_value))
                    uploaded_file.save()
                    field_value = uploaded_file.pk
                else:
                    #retain the old file if no file is set
                    field_value = setting.value
            
            if setting.value != field_value:
                #Setting changed. update the db entry.
                #Setting model's save will recache.
                setting.value = field_value
                setting.save()
                cache_setting(setting.scope, setting.scope_category, setting.name,
                  setting)

            if setting.name == "siteurl" and setting.scope == "site":
                if field_value:
                    # Update the django site value in the contrib backend
                    django_site = Site.objects.get(pk=1)
                    django_site.domain = field_value.replace("http://","")
                    django_site.name = field_value.replace("http://","")
                    django_site.save()
        except KeyError:
            pass
            

def build_settings_form(user, settings):
    """
        Create a set of fields and builds a form class
        returns SettingForm class
    """
    fields = OrderedDict()
    for setting in settings:
        if setting.input_type == 'text':
            options = {
                'label': setting.label,
                'help_text': setting.description,
                'initial': setting.value,
                'required': False
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name : forms.CharField(**options) })
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name : forms.CharField(**options) })
                    
        elif setting.input_type == 'select':
            if setting.input_value == '<form_list>':
                choices = get_form_list(user)
                required = False
            elif setting.input_value == '<box_list>':
                choices = get_box_list(user)
                required = False
            else:
                # Allow literal_eval in settings in order to pass a list from the setting
                # This is useful if you want different values and labels for the select options
                try:
                    choices = tuple([(k,v)for k,v in literal_eval(setting.input_value)])
                    required = False

                    # By adding #<box_list> on to the end of a setting, this will append the boxes
                    # as select items in the list as well.
                    if '<box_list>' in setting.input_value:
                        box_choices = get_box_list(user)[1:]
                        choices = (('Content',choices),('Boxes',box_choices))
                except:
                    choices = tuple([(s,s)for s in setting.input_value.split(',')])
                    required = True

            options = {
                'label': setting.label,
                'help_text': setting.description,
                'initial': setting.value,
                'choices': choices,
                'required': required,
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name : forms.ChoiceField(**options) }) 
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name : forms.ChoiceField(**options) })
            
        elif setting.input_type == 'file':
            from files.models import File as TendenciFile
            file_display = ''
            try:
                try: val = int(setting.value)
                except: val = 0
                
                try:
                    tfile = TendenciFile.objects.get(pk=val)
                except:
                    tfile = None

                if tfile:
                    if tfile.file.name.lower().endswith(('.jpg', '.jpe', '.png', '.gif', '.svg')):
                        file_display = '<img src="/files/%s/">' % tfile.pk
                    else:
                        file_display = tfile.file.name
            except TendenciFile.DoesNotExist:
                file_display = "No file"
            options = {
                'label': setting.label,
                'help_text': "%s<br> Current File: %s" % (setting.description, file_display),
                #'initial': tfile and tfile.file, # Removed this so the file doesn't save over and over
                'required': False
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name : forms.FileField(**options) })
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name : forms.FileField(**options) })
       
    attributes = {
        'settings': settings,
        'base_fields': fields,
        'clean': clean_settings_form,
        'save': save_settings_form,
        'user': user,
    }     
    return type('SettingForm', (forms.BaseForm,), attributes)
