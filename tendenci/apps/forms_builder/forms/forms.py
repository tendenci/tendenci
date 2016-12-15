from datetime import datetime
from os.path import join
from uuid import uuid4

from django import forms
from importlib import import_module
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.core.files.storage import default_storage
from tendenci.apps.base.utils import validate_email

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.payments.models import PaymentMethod
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.perms.forms import TendenciBaseForm
from captcha.fields import CaptchaField
from tendenci.apps.user_groups.models import Group
from tendenci.apps.base.utils import get_template_list, tcurrency
from tendenci.apps.base.fields import EmailVerificationField, PriceField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.base.utils import currency_check
from tendenci.apps.payments.fields import PaymentMethodModelMultipleChoiceField
from tendenci.apps.recurring_payments.fields import BillingCycleField
from tendenci.apps.recurring_payments.widgets import BillingCycleWidget, BillingDateSelectWidget
from tendenci.apps.forms_builder.forms.models import FormEntry, FieldEntry, Field, Form, Pricing
from tendenci.apps.forms_builder.forms.settings import FIELD_MAX_LENGTH
from tendenci.apps.files.validators import FileValidator


template_choices = [
    ('', _('None')),
    ('default.html', _('Default')),
    ('forms/base.html', _('Forms Base'))
]
template_choices += get_template_list()

#fs = FileSystemStorage(location=UPLOAD_ROOT)

FIELD_FNAME_LENGTH = 30
FIELD_LNAME_LENGTH = 30
FIELD_NAME_LENGTH = 50
FIELD_PHONE_LENGTH = 50
THIS_YEAR = datetime.today().year


class FormForForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = FormEntry
        exclude = ("form", "entry_time", "entry_path", "payment_method", "pricing", 'custom_price',  "creator")

    def __init__(self, form, user, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model
        instance and its related field model instances.
        """
        self.user = user
        self.form = form
        self.form_fields = form.fields.visible().order_by('position')
        self.auto_fields = form.fields.auto_fields().order_by('position')
        super(FormForForm, self).__init__(*args, **kwargs)

        def add_fields(form, form_fields):
            for field in form_fields:
                field_key = "field_%s" % field.id
                if "/" in field.field_type:
                    field_class, field_widget = field.field_type.split("/")
                else:
                    field_class, field_widget = field.field_type, None

                if field.field_type == 'EmailVerificationField':
                    one_email = get_setting('module', 'forms', 'one_email')
                    if one_email:
                        field_class = forms.EmailField
                    else:
                        field_class = EmailVerificationField

                elif field.field_type == 'BooleanField' and len(field.choices) > 0:
                    field_class = forms.MultipleChoiceField
                    field_widget = 'django.forms.CheckboxSelectMultiple'

                elif field.field_type == 'CountryField' or field.field_type == 'StateProvinceField':
                    field_class = getattr(forms, 'ChoiceField')
                else:
                    field_class = getattr(forms, field_class)
                field_args = {"label": mark_safe(field.label), "required": field.required}
                arg_names = field_class.__init__.im_func.func_code.co_varnames
                if "max_length" in arg_names:
                    field_args["max_length"] = FIELD_MAX_LENGTH
                if "choices" in arg_names:
                    field_args["choices"] = field.get_choices()
                    #field_args["choices"] = zip(choices, choices)
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

                if field.field_function == 'EmailFirstName':
                    field_args["max_length"] = FIELD_FNAME_LENGTH
                elif field.field_function == 'EmailLastName':
                    field_args["max_length"] = FIELD_LNAME_LENGTH
                elif field.field_function == 'EmailFullName':
                    field_args["max_length"] = FIELD_NAME_LENGTH
                elif field.field_function == 'EmailPhoneNumber':
                    field_args["max_length"] = FIELD_PHONE_LENGTH
                elif field.field_type == 'FileField':
                    field_args["validators"] = [FileValidator()]

                form.fields[field_key] = field_class(**field_args)

                if not field_class == EmailVerificationField:
                    form.fields[field_key].widget.attrs['title'] = field.label
                    form.fields[field_key].widget.attrs['class'] = 'formforform-field'
                else:
                    form.fields[field_key].widget.widgets[0].attrs['class'] += ' formforform-field'
                    form.fields[field_key].widget.widgets[1].attrs['class'] += ' formforform-field'

                if form.fields[field_key].widget.__class__.__name__.lower() == 'selectdatewidget':
                    form.fields[field_key].widget.years = range(1920, THIS_YEAR + 10)

        def add_pricing_fields(form, formforform):
            # include pricing options if any
            if (formforform.custom_payment or formforform.recurring_payment) and formforform.pricing_set.all():

                currency_symbol = get_setting('site', 'global', 'currencysymbol')

                pricing_options = []
                for pricing in formforform.pricing_set.all():

                    if pricing.price == None:
                        pricing_options.append(
                            (pricing.pk, mark_safe(
                                '<input type="text" class="custom-price" name="custom_price_%s" value="%s"/> <strong>%s</strong><br>%s' %
                                (pricing.pk, form.data.get('custom_price_%s' %pricing.pk, unicode()), pricing.label, pricing.description)))
                        )
                    else:
                        if formforform.recurring_payment:
                            pricing_options.append(
                                (pricing.pk, mark_safe('<strong>%s per %s %s - %s</strong><br>%s' %
                                                        (tcurrency(pricing.price),
                                                         pricing.billing_frequency, pricing.billing_period,
                                                         pricing.label, pricing.description)))
                            )
                        else:
                            pricing_options.append(
                                (pricing.pk, mark_safe('<strong>%s %s</strong><br>%s' %
                                                       (tcurrency(pricing.price),
                                                        pricing.label, pricing.description)))
                            )

                form.fields['pricing_option'] = forms.ChoiceField(
                    label=_('Pricing'),
                    choices = pricing_options,
                    widget=forms.RadioSelect(attrs={'class': 'pricing-field'})
                )

                form.fields['payment_option'] = forms.ModelChoiceField(
                        label=_('Payment Method'),
                        empty_label=None,
                        queryset=formforform.payment_methods.all(),
                        widget=forms.RadioSelect(attrs={'class': 'payment-field'}),
                        initial=1,
                    )

        if self.form.pricing_position < self.form.fields_position:
            add_pricing_fields(self, self.form)
            add_fields(self, self.form_fields)
        else:
            add_fields(self, self.form_fields)
            add_pricing_fields(self, self.form)

        if not self.user.is_authenticated() and get_setting('site', 'global', 'captcha'): # add captcha if not logged in
            self.fields['captcha'] = CaptchaField(label=_('Type the code below'))

        self.add_form_control_class()


    def clean_pricing_option(self):
        pricing_pk = int(self.cleaned_data['pricing_option'])
        pricing_option = self.form.pricing_set.get(pk=pricing_pk)
        custom_price = self.data.get('custom_price_%s' % pricing_pk)

        # if not price set
        if not pricing_option.price:
            # then price is custom

            if not custom_price:  # custom price has a value
                raise forms.ValidationError(_("Please set your price."))

            try:  # custom price is valid amount
                custom_price = currency_check(custom_price)
            except:
                raise forms.ValidationError(_("Price must be a valid amount"))

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
                value = default_storage.save(join("forms", str(uuid4()), value.name), value)
            # if the value is a list convert is to a comma delimited string
            if isinstance(value,list):
                value = ','.join(value)
            if not value: value=''
            field_entry = FieldEntry(field_id = field.id, entry=entry, value = value)
            field_entry.save()

        for field in self.auto_fields:
            value = field.choices
            field_entry = FieldEntry(field_id = field.id, entry=entry, value=value)
            field_entry.save()

        # save selected pricing and payment method if any
        if (self.form.custom_payment or self.form.recurring_payment) and self.form.pricing_set.all():
            entry.payment_method = self.cleaned_data['payment_option']
            entry.pricing = self.cleaned_data['pricing_option']
            custom_price = self.data.get('custom_price_%s' % entry.pricing.id)
            if custom_price:
                entry.custom_price = custom_price
            entry.save()

        return entry

    def email_to(self):
        """
        Return the value entered for the first field of type EmailField.
        """
        for field in self.form_fields:
            field_class = field.field_type.split("/")[0]
            if field_class == "EmailVerificationField":
                return self.cleaned_data["field_%s" % field.id]
        return None


class FormAdminForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('draft',_('Draft')),('published',_('Published')),))

    intro = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Form._meta.app_label,
        'storme_model':Form._meta.model_name.lower()}))

    response = forms.CharField(required=False, label=_('Confirmation Text'),
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Form._meta.app_label,
        'storme_model':Form._meta.model_name.lower()}))
    
    email_text = forms.CharField(required=False, label=_('Confirmation Text'),
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Form._meta.app_label,
        'storme_model':Form._meta.model_name.lower()}))

    template = forms.ChoiceField(choices=template_choices, required=False)

    class Meta:
        model = Form
        fields = ('title',
                  'slug',
                  'intro',
                  'response',
                  'template',
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
                  'status_detail',
                  'custom_payment',
                  'recurring_payment',
                  'payment_methods',
                  'intro_position',
                  'fields_position',
                  'pricing_position',
                  'intro_name',
                  'fields_name',
                  'pricing_name',
                 )

    def __init__(self, *args, **kwargs):
        super(FormAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['intro'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['response'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if self.instance.intro_name:
                self.fields['intro'].label = self.instance.intro_name
        else:
            self.fields['intro'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['response'].widget.mce_attrs['app_instance_id'] = 0

        position_fields = ['intro_position', 'fields_position', 'pricing_position']
        for field in position_fields:
            self.fields[field].widget.attrs['class'] = 'position_field'


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
        choices=(('draft',_('Draft')),('published',_('Published')),))
    custom_payment = forms.BooleanField(label=_('Take Payment'), required=False)

    # payment_method_choices = list(PaymentMethod.objects.values_list('id','human_name'))
    # payment_method_choices.append((0, mark_safe('<input type="text" name="custom-payment-method" />')))
    # payment_methods = forms.MultipleChoiceField(
    #     choices=payment_method_choices,
    #     widget=forms.CheckboxSelectMultiple(),
    #     required=False
    # )

    payment_methods = PaymentMethodModelMultipleChoiceField(
            queryset=PaymentMethod.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
            initial=[1,2,3]
        )

    class Meta:
        model = Form
        fields = (
            'title',
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
            'recurring_payment',
            'payment_methods',
            'user_perms',
            'member_perms',
            'group_perms',
            'allow_anonymous_view',
            'status_detail',
        )
        fieldsets = [(_('Form Information'), {
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
                    (_('Permissions'), {
                        'fields': [ 'allow_anonymous_view',
                                    'user_perms',
                                    'member_perms',
                                    'group_perms',
                                    ],
                        'classes': ['permissions'],
                        }),
                    (_('Administrator Only'), {
                        'fields': ['status_detail'],
                        'classes': ['admin-only'],
                    }),
                    (_('Payments'), {
                        'fields':['custom_payment','recurring_payment','payment_methods'],
                        'legend':''
                    }),]

    def __init__(self, *args, **kwargs):
        super(FormForm, self).__init__(*args, **kwargs)

        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')

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

    def clean(self):
        cleaned_data = self.cleaned_data
        field_function = cleaned_data.get("field_function")
        choices = cleaned_data.get("choices")
        field_type = cleaned_data.get("field_type")
        required = cleaned_data.get("required")
        visible = cleaned_data.get("visible")

        if field_function == "GroupSubscription":
            if field_type != "BooleanField":
                raise forms.ValidationError(_("This field's function requires Checkbox as a field type"))
            if not choices:
                raise forms.ValidationError(_("This field's function requires at least 1 group specified."))
            else:
                for val in choices.split(','):
                    try:
                        g = Group.objects.get(name=val.strip())
                        if not g.allow_self_add:
                            raise forms.ValidationError(_("The group \"%(val)s\" does not allow self-add." % { 'val' : val }))
                    except Group.DoesNotExist:
                        raise forms.ValidationError(_("The group \"%(val)s\" does not exist" % { 'val' : val }))

        if field_function == "GroupSubscriptionAuto":
            # field_type doesn't matter since this field shouldn't be rendered anyway.
            if visible:
                raise forms.ValidationError(_("This field must not be visible to users."))
            if not choices:
                raise forms.ValidationError(_("This field's function requires at least 1 group specified."))
            else:
                for val in choices.split(','):
                    try:
                        g = Group.objects.get(name=val.strip())
                        if not g.allow_self_add:
                            raise forms.ValidationError(_("The group \"%(val)s\" does not allow self-add." % { 'val' : val }))
                    except Group.DoesNotExist:
                        raise forms.ValidationError(_("The group \"%(val)s\" does not exist" % { 'val' : val }))

        if field_function == "Recipients":
            if (field_type != "MultipleChoiceField/django.forms.CheckboxSelectMultiple" and
                field_type != "MultipleChoiceField" and
                field_type != "BooleanField" and
                field_type != "ChoiceField"):
                raise forms.ValidationError(_("The \"Email to Recipients\" function requires Multi-select - Checkboxes "
                                            + "or Multi-select - Select Many as field type"))

            if field_type == "BooleanField":
                if not choices:
                    raise forms.ValidationError(_("The \"Email to Recipients\" function requires at least 1 email specified."))
                else:
                    for val in choices.split(','):
                        if not validate_email(val.strip()):
                            raise forms.ValidationError(_("\"%(val)s\" is not a valid email address" % {'val':val}))
            else:
                if not choices:
                    raise forms.ValidationError(_("The \"Email to Recipients\" function requires at least 1 choice specified."))
                else:
                    for val in choices.split(','):
                        val = val.split(':')
                        if len(val) < 2:
                            raise forms.ValidationError(_("The \"Email to Recipients\" function requires choices to be in the following format: <choice_label>:<email_address>."))
                        if not validate_email(val[1].strip()):
                            raise forms.ValidationError(_("\"%(val)s\" is not a valid email address" % {'val':val[1]}))

        if field_function != None and field_function.startswith("Email"):
            if field_type != "CharField":
                raise forms.ValidationError(_("This field's function requires Text as a field type"))

        #unrequire the display only fields
        if field_type == "CharField/tendenci.apps.forms_builder.forms.widgets.Description":
            cleaned_data['required'] = False
        elif field_type == "CharField/tendenci.apps.forms_builder.forms.widgets.Header":
            cleaned_data['required'] = False

        return cleaned_data


class PricingForm(FormControlWidgetMixin, forms.ModelForm):
    billing_dt_select = BillingCycleField(label=_('When to bill'),
                                          widget=BillingDateSelectWidget,
                                          help_text=_('It is used to determine the payment due date for each billing cycle'))
    billing_cycle = BillingCycleField(label=_('How often to bill'),
                                      widget=BillingCycleWidget)
    price = PriceField(max_digits=10, decimal_places=2, required=False,
                       help_text=_('Leaving this field blank allows visitors to set their own price'))

    class Meta:
        model = Pricing
        fields = ('label',
                  'price',
                  'taxable',
                  'tax_rate',
                  'billing_cycle',
                  'billing_dt_select',
                  'has_trial_period',
                  'trial_period_days',
                 )
        fieldsets = [(_('Form Information'), {
                        'fields': [ 'label',
                                    'price',
                                    'taxable',
                                    'tax_rate',
                                    'billing_cycle',
                                    'billing_dt_select',
                                    ],
                        'legend': ''
                        }),
                    (_('Trial Period'), {
                        'fields': [ 'has_trial_period',
                                    'trial_period_days',],
                        'legend': '',
                        }),]

    def __init__(self, *args, **kwargs):
        super(PricingForm, self).__init__(*args, **kwargs)
        # Setup initial values for billing_cycle and billing_dt_select
        # in order to have empty values for extra forms.
        if self.instance.pk:
            self.fields['billing_dt_select'].initial = [self.instance.num_days,
                                                        self.instance.due_sore]
            self.fields['billing_cycle'].initial = [self.instance.billing_frequency,
                                                    self.instance.billing_period]
        else:
            self.fields['billing_dt_select'].initial = [0, u'start']
            self.fields['billing_cycle'].initial = [1, u'month']

        # Add class for recurring payment fields
        recurring_payment_fields = [
            'taxable', 'tax_rate', 'billing_cycle', 'billing_dt_select',
            'has_trial_period', 'trial_period_days'
        ]

        for field in recurring_payment_fields:
            class_attr = self.fields[field].widget.attrs.get('class', None)
            if class_attr and 'recurring-payment' not in class_attr:
                class_attr += ' recurring-payment'

                self.fields[field].widget.attrs.update({'class': class_attr})

    def save(self, **kwargs):
        pricing = super(PricingForm, self).save(**kwargs)
        if self.cleaned_data.get('billing_dt_select'):
            dt_select = self.cleaned_data.get('billing_dt_select').split(',')
            pricing.num_days = dt_select[0]
            pricing.due_sore = dt_select[1]
        if self.cleaned_data.get('billing_cycle'):
            cycle = self.cleaned_data.get('billing_cycle').split(',')
            pricing.billing_frequency = cycle[0]
            pricing.billing_period = cycle[1]
        #pricing.save()
        return pricing

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
