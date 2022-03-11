from collections import OrderedDict
from ast import literal_eval
from urllib.parse import urlparse

from django import forms
from django.conf import settings as django_settings
from django.core.files import File
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django_countries import countries as COUNTRIES
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from tendenci.apps.base.utils import (get_timezone_choices, checklist_update,
    get_languages_with_local_name)
from tendenci.apps.site_settings.utils import (get_form_list,
                                               get_box_list,
                                               get_group_list)


def clean_settings_form(self):
    """
        Cleans data that has been set in the settings form
    """
    for setting in self.settings:
        try:
            field_value = self.cleaned_data[setting.name]
            if setting.data_type == "boolean":
                if field_value != 'true' and field_value != 'false':
                    raise forms.ValidationError(_("'%(l)s' must be true or false" % {'l':setting.label}))
            if setting.data_type == "int":
                if field_value != ' ':
                    if not field_value.isdigit():
                        raise forms.ValidationError(_("'%(l)s' must be a whole number" % {'l':setting.label}))
            if setting.data_type == "file":
                if field_value:
                    if not isinstance(field_value, File):
                        raise forms.ValidationError(_("'%(l)s' must be a file" % {'l':setting.label}))

            if setting.name == "siteurl" and setting.scope == "site":
                field_value = self.cleaned_data["siteurl"]
                if field_value:
                    if field_value[-1:] == "/":
                        field_value = field_value[:-1]
                    self.cleaned_data[setting.name] = field_value
        except KeyError:
            pass

    return self.cleaned_data


def save_settings_form(self):
    """
        Save the updated settings in the database
        Setting's save will trigger a cache update.
        If the field type is 'file' a file entry will be created.
    """
    for setting in self.settings:
        old_value = setting.get_value()
        try:
            field_value = self.cleaned_data[setting.name]
            if setting.input_type == "file":
                if field_value:
                    # save a file object and set the value at that file object's id.
                    from tendenci.apps.files.models import File as TendenciFile
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
                    field_value = setting.get_value()

            # update value if changed and save
            if old_value != field_value:
                setting.set_value(field_value)
                setting.save()  # save updates the cash automatically

            # update the django site value in the contrib backend
            if setting.name == "siteurl" and setting.scope == "site":
                if field_value:
                    setting.update_site_domain(field_value)

            # update checklist for theme logo
            if setting.name == 'logo' and setting.scope_category == 'theme':
                checklist_update('upload-logo')

            # update checklist for contact form
            if setting.name == 'contact_form' and setting.scope == "site":
                checklist_update('update-contact')

        except KeyError:
            pass


def build_settings_form(user, settings):
    """
        Create a set of fields and builds a form class
        returns SettingForm class
    """
    fields = OrderedDict()
    for setting in settings:
        setting_label = mark_safe('{0} <a href="#id_{1}" title="Permalink to this setting"><i class="fa fa-link" aria-hidden="true"></i></a>'.format(
                                    setting.label, setting.name))

        # Do not display standard regform settings
        if setting.scope_category == 'events' and setting.name.startswith('regform_'):
            continue

        try:
            setting_value = force_str(setting.get_value())
        except DjangoUnicodeDecodeError:
            setting_value = ''

        if setting.input_type in ['text', 'textarea']:
            options = {
                'label': setting_label,
                'help_text': setting.description,
                'initial': setting_value,
                'required': False,
                'label_suffix': "",
            }
            if setting.input_type == 'textarea':
                options['widget'] = forms.Textarea(attrs={'rows': 5, 'cols': 30})

            if setting.client_editable:
                fields.update({"%s" % setting.name: forms.CharField(**options)})
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name: forms.CharField(**options)})

        elif setting.input_type in ['select', 'selectmultiple']:
            if setting.input_value == '<form_list>':
                choices = get_form_list(user)
                required = False
            elif setting.input_value == '<box_list>':
                choices = get_box_list(user)
                required = False
            elif setting.input_value == '<group_list>':
                choices, initial = get_group_list(user)
                required = True
                if not setting_value:
                    setting_value = initial
            elif setting.input_value == '<timezone_list>':
                choices = get_timezone_choices()
                required = True
                if not setting_value:
                    setting_value = django_settings.TIME_ZONE
            elif setting.input_value == '<language_list>':
                choices = get_languages_with_local_name()
                required = True
            elif setting.input_value == '<country_list>':
                choices = (('', '-----------'),) + tuple(COUNTRIES)
                required = False
                if setting.get_value() and  setting.name == 'countrylistinitialchoices':
                    setting_value = literal_eval(setting.get_value())
            else:
                # Allow literal_eval in settings in order to pass a list from the setting
                # This is useful if you want different values and labels for the select options
                try:
                    choices = tuple([(k, v)for k, v in literal_eval(setting.input_value)])
                    required = False

                    # By adding #<box_list> on to the end of a setting, this will append the boxes
                    # as select items in the list as well.
                    if '<box_list>' in setting.input_value:
                        box_choices = get_box_list(user)[1:]
                        choices = (('Content', choices), ('Boxes', box_choices))
                except:
                    choices = tuple([(s.strip(), s.strip())for s in setting.input_value.split(',')])
                    required = True

            options = {
                'label': setting_label,
                'help_text': setting.description,
                'initial': setting_value,
                'choices': choices,
                'required': required,
                'label_suffix': "",
            }
            if setting.client_editable or user.is_superuser:
                if setting.input_type == 'selectmultiple':
                    fields.update({"%s" % setting.name: forms.MultipleChoiceField(**options)})
                else:
                    fields.update({"%s" % setting.name: forms.ChoiceField(**options)})

        elif setting.input_type == 'file':
            from tendenci.apps.files.models import File as TendenciFile
            file_display = ''
            try:
                try:
                    val = int(setting_value)
                except ValueError:
                    val = 0

                try:
                    tfile = TendenciFile.objects.get(pk=val)
                except Exception:
                    tfile = None

                if tfile:
                    if tfile.file.name.lower().endswith(('.jpg', '.jpe', '.png', '.gif', '.svg')):
                        tfile_alt = tfile.file.name.lower()[:-4]
                        file_display = '<img src="/files/%s/" alt="%s" title="%s">' % (tfile.pk, tfile_alt, tfile_alt)
                    else:
                        file_display = tfile.file.name
            except TendenciFile.DoesNotExist:
                file_display = "No file"
            options = {
                'label': setting_label,
                'help_text': "%s<br> Current File: %s" % (setting.description, file_display),
                #'initial': tfile and tfile.file, # Removed this so the file doesn't save over and over
                'required': False,
                'label_suffix': "",
            }
            if setting.client_editable:
                fields.update({"%s" % setting.name: forms.FileField(**options)})
            else:
                if user.is_superuser:
                    fields.update({"%s" % setting.name: forms.FileField(**options)})

    attributes = {
        'settings': settings,
        'base_fields': fields,
        'clean': clean_settings_form,
        'save': save_settings_form,
        'user': user,
    }
    return type('SettingForm', (forms.BaseForm,), attributes)
