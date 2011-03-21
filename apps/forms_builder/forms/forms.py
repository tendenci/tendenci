
from datetime import datetime
from os.path import join
from uuid import uuid4

from django import forms
from django.core.files.storage import FileSystemStorage
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms.models import FormEntry
from forms_builder.forms.settings import FIELD_MAX_LENGTH, UPLOAD_ROOT
from forms_builder.forms.models import Form
from perms.forms import TendenciBaseForm
from perms.utils import is_admin
from captcha.fields import CaptchaField

fs = FileSystemStorage(location=UPLOAD_ROOT)

class FormForForm(forms.ModelForm):

    class Meta:
        model = FormEntry
        exclude = ("form", "entry_time")

    def __init__(self, form, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model 
        instance and its related field model instances.
        """
        self.form = form
        self.form_fields = form.fields.visible()
        super(FormForForm, self).__init__(*args, **kwargs)
        for field in self.form_fields:
            field_key = "field_%s" % field.id
            if "/" in field.field_type:
                field_class, field_widget = field.field_type.split("/")
            else:
                field_class, field_widget = field.field_type, None
            field_class = getattr(forms, field_class)
            field_args = {"label": field.label, "required": field.required}
            arg_names = field_class.__init__.im_func.func_code.co_varnames
            if "max_length" in arg_names:
                field_args["max_length"] = FIELD_MAX_LENGTH
            if "choices" in arg_names:
                choices = field.choices.split(",")
                field_args["choices"] = zip(choices, choices)
            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)
            self.fields[field_key] = field_class(**field_args)
        self.fields['captcha'] = CaptchaField(label=_('Type the code below'))

    def save(self, **kwargs):
        """
        Create a FormEntry instance and related FieldEntry instances for each 
        form field.
        """
        entry = super(FormForForm, self).save(commit=False)
        entry.form = self.form
        entry.entry_time = datetime.now()
        entry.save()
        for field in self.form_fields:
            field_key = "field_%s" % field.id
            value = self.cleaned_data[field_key]
            if value and self.fields[field_key].widget.needs_multipart_form:
                value = fs.save(join("forms", str(uuid4()), value.name), value)
            # if the value is a list convert is to a comma delimited string
            if isinstance(value,list):
                value = ','.join(value)
            if not value: value=''
            entry.fields.create(field_id=field.id, value=value)
        return entry
        
    def email_to(self):
        """
        Return the value entered for the first field of type EmailField.
        """
        for field in self.form_fields:
            field_class = field.field_type.split("/")[0]
            if field_class == "EmailField":
                return self.cleaned_data["field_%s" % field.id]
        return None
        
class FormForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('draft','Draft'),('published','Published'),))

    class Meta:
        model = Form
        fields = ('title',
                  'intro',
                  'response',
                  # 'send_email', removed per ed's request
                  'email_from',
                  'email_copies',
                  'user_perms',
                  'group_perms',
                  'allow_anonymous_view',
                  'status',
                  'status_detail',
                 )

        fieldsets = [('Form Information', {
                      'fields': ['title',
                                 'intro',
                                 'response',
                                 'email_from',
                                 'email_copies',
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]
                
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs) 
        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
