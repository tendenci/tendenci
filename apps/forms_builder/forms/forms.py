
from datetime import datetime
from os.path import join
from uuid import uuid4
from decimal import Decimal

from django import forms
from django.core.files.storage import FileSystemStorage
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from site_settings.utils import get_setting
from payments.models import PaymentMethod
from tinymce.widgets import TinyMCE
from perms.forms import TendenciBaseForm
from perms.utils import is_admin, is_developer
from captcha.fields import CaptchaField
from user_groups.models import Group


from forms_builder.forms.models import FormEntry, FieldEntry, Field, Form, Pricing
from forms_builder.forms.settings import FIELD_MAX_LENGTH, UPLOAD_ROOT

fs = FileSystemStorage(location=UPLOAD_ROOT)

class FormForForm(forms.ModelForm):

    class Meta:
        model = FormEntry
        exclude = ("form", "entry_time", "entry_path", "payment_method", "pricing")
    
    def __init__(self, form, user, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model 
        instance and its related field model instances.
        """
        self.user = user
        self.form = form
        self.form_fields = form.fields.visible().order_by('position')
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
            if "initial" in arg_names:
                default = field.default.lower()
                if field_class == "BooleanField":
                    if default == "checked" or default == "true" or \
                        default == "on" or default == "1":
                            default = True
                    else:
                        default = False
                field_args["initial"] = field.default

            if field_widget is not None:
                module, widget = field_widget.rsplit(".", 1)
                field_args["widget"] = getattr(import_module(module), widget)

            self.fields[field_key] = field_class(**field_args)

            self.fields[field_key].widget.attrs['title'] = field.label

        # include pricing options if any
        if self.form.custom_payment and self.form.pricing_set.all():

            currency_symbol = get_setting('site', 'global', 'currencysymbol')

            pricing_options = []
            for pricing in self.form.pricing_set.all():

                if pricing.price == None:
                    pricing_options.append(
                        (pricing.pk, mark_safe(
                            '<input type="text" class="custom-price" name="custom_price_%s" value="%s"/> %s' % 
                            (pricing.pk, self.data.get('custom_price_%s' %pricing.pk, unicode()), pricing.label)))
                    )
                else:
                    pricing_options.append(
                        (pricing.pk, '%s%s %s' % (currency_symbol, pricing.price, pricing.label))
                    )

            self.fields['pricing_option'] = forms.ChoiceField(
                label=_('Pricing'),
                choices = pricing_options,
                widget=forms.RadioSelect
            )

            self.fields['payment_option'] = forms.ModelChoiceField(
                    label=_('Payment Method'),
                    empty_label=None,
                    queryset=self.form.payment_methods.all(),
                    widget=forms.RadioSelect,
                    initial=1,
                )

        if not self.user.is_authenticated(): # add captcha if not logged in
            self.fields['captcha'] = CaptchaField(label=_('Type the code below'))


    def clean_pricing_option(self):
        pricing_pk = int(self.cleaned_data['pricing_option'])
        pricing_option = self.form.pricing_set.get(pk=pricing_pk)
        custom_price = self.data.get('custom_price_%s' % pricing_pk)

        # if not price set
        if not pricing_option.price:
            # then price is custom

            if not custom_price:  # custom price has a value
                raise forms.ValidationError("Please set your price.")

            try:  # custom price is valid amount
                custom_price = Decimal(custom_price)
            except ValueError:
                raise forms.ValidationError("Price must be a valid amount")
        
        self.cleaned_data['custom_price'] = custom_price
        return pricing_option

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
            field_entry = FieldEntry(field_id = field.id, entry=entry, value = value)
            if self.user.is_authenticated():
                field_entry.save(user = self.user)
            else:
                field_entry.save()

        # save selected pricing and payment method if any
        if self.form.custom_payment and self.form.pricing_set.all():
            entry.payment_method = self.cleaned_data['payment_option']
            entry.pricing = self.cleaned_data['pricing_option']
            entry.save()
            
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
        
        
class FormAdminForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('draft','Draft'),('published','Published'),))

    intro = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Form._meta.app_label, 
        'storme_model':Form._meta.module_name.lower()}))

    response = forms.CharField(required=False, label='Confirmation Text', 
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Form._meta.app_label, 
        'storme_model':Form._meta.module_name.lower()}))

    class Meta:
        model = Form
        fields = ('title',
                  'slug',
                  'intro',
                  'response',
                  'send_email', # removed per ed's request, added back per Aaron's request 2011-10-14
                  'email_text',
                  'subject_template',
                  'completion_url',
                  'email_from',
                  'email_copies',
                  'user_perms',
                  'member_perms',
                  'group_perms',
                  'allow_anonymous_view',
                  'status',
                  'status_detail',
                 )

    def __init__(self, *args, **kwargs): 
        super(FormAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['intro'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['response'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['intro'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['response'].widget.mce_attrs['app_instance_id'] = 0


    def clean_slug(self):
        slug = slugify(self.cleaned_data['slug'])
        i = 0
        while True:
            if i > 0:
                if i > 1:
                    slug = slug.rsplit("-", 1)[0]
                slug = "%s-%s" % (slug, i)
            match = Form.objects.filter(slug=slug)
            if self.instance:
                match = match.exclude(pk=self.instance.pk)
            if not match:
                break
            i += 1
        return slug
        
class FormForm(TendenciBaseForm):
    # from django.utils.safestring import mark_safe

    status_detail = forms.ChoiceField(
        choices=(('draft','Draft'),('published','Published'),))
    custom_payment = forms.BooleanField(label=_('Take Payment'), required=False)

    # payment_method_choices = list(PaymentMethod.objects.values_list('id','human_name'))
    # payment_method_choices.append((0, mark_safe('<input type="text" name="custom-payment-method" />')))
    # payment_methods = forms.MultipleChoiceField(
    #     choices=payment_method_choices,
    #     widget=forms.CheckboxSelectMultiple(),
    #     required=False
    # )

    payment_methods = forms.ModelMultipleChoiceField(
            queryset=PaymentMethod.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
            initial=[1,2,3]
        )
    
    class Meta:
        model = Form
        fields = ('title',
                  'slug',
                  'intro',
                  'response',
                  'send_email', # removed per ed's request, added back per Aaron's request 2011-10-14
                  'email_text',
                  'completion_url',
                  'subject_template',
                  'email_from',
                  'email_copies',
                  'custom_payment',
                  'payment_methods',
                  'user_perms',
                  'member_perms',
                  'group_perms',
                  'allow_anonymous_view',
                  'status',
                  'status_detail',
                 )
        fieldsets = [('Form Information', {
                        'fields': [ 'title',
                                    'slug',
                                    'intro',
                                    'response',
                                    'completion_url',
                                    'subject_template',
                                    'email_from',
                                    'email_copies',
                                    'send_email',
                                    'email_text',
                                    ],
                        'legend': ''
                        }),
                    ('Permissions', {
                        'fields': [ 'allow_anonymous_view',
                                    'user_perms',
                                    'member_perms',
                                    'group_perms',
                                    ],
                        'classes': ['permissions'],
                        }),
                    ('Administrator Only', {
                        'fields': ['status',
                                    'status_detail'], 
                        'classes': ['admin-only'],
                    }),
                    ('Payments', {
                        'fields':['custom_payment', 'payment_methods'],
                        'legend':''
                    }),]
                
    def __init__(self, *args, **kwargs):
        super(FormForm, self).__init__(*args, **kwargs)

        if not is_admin(self.user):
            if 'status' in self.fields:
                self.fields.pop('status')
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')

        if not is_developer(self.user):
            if 'status' in self.fields: self.fields.pop('status')

    def clean_slug(self):
        slug = slugify(self.cleaned_data['slug'])
        i = 0
        while True:
            if i > 0:
                if i > 1:
                    slug = slug.rsplit("-", 1)[0]
                slug = "%s-%s" % (slug, i)
            match = Form.objects.filter(slug=slug)
            if self.instance:
                match = match.exclude(pk=self.instance.pk)
            if not match:
                break
            i += 1
        return slug

class FormForField(forms.ModelForm):
    class Meta:
        model = Field
        exclude = ["position"]
    
    def clean_function_params(self):
        function_params = self.cleaned_data['function_params']
        clean_params = ''
        for val in function_params.split(','):
            clean_params = val.strip() + ',' + clean_params
        return clean_params[0:len(clean_params)-1]
        
    def clean(self):
        cleaned_data = self.cleaned_data
        field_function = cleaned_data.get("field_function")
        function_params = cleaned_data.get("function_params")
        field_type = cleaned_data.get("field_type")
        required = cleaned_data.get("required")
        
        if field_function == "GroupSubscription":
            if field_type != "BooleanField":
                raise forms.ValidationError("This field's function requires Checkbox as a field type")
            if not function_params:
                raise forms.ValidationError("This field's function requires at least 1 group specified.")
            else:
                for val in function_params.split(','):
                    try:
                        Group.objects.get(name=val)
                    except Group.DoesNotExist:
                        raise forms.ValidationError("The group \"%s\" does not exist" % (val))
                    
        if field_function != None and field_function.startswith("Email"):
            if field_type != "CharField":
                raise forms.ValidationError("This field's function requires Text as a field type")
        
        #unrequire the display only fields
        if field_type == "CharField/forms_builder.forms.widgets.Description":
            cleaned_data['required'] = False
        elif field_type == "CharField/forms_builder.forms.widgets.Header":
            cleaned_data['required'] = False
            
        return cleaned_data

class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        
class BillingForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    company = forms.CharField(required=False)
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.CharField(required=False)
    zip_code = forms.CharField(required=False)
    country = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
