import re
from datetime import datetime

from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import BaseFormSet
from django.forms.util import ErrorList

from captcha.fields import CaptchaField
from events.models import Event, Place, RegistrationConfiguration, \
    Payment, PaymentMethod, Sponsor, Organizer, Speaker, Type, \
    TypeColorSet, Registrant, GroupRegistrationConfiguration, \
    SpecialPricing
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField
from emails.models import Email
from form_utils.forms import BetterModelForm

from fields import Reg8nDtField, Reg8nDtWidget

class RadioImageFieldRenderer(forms.widgets.RadioFieldRenderer):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioImageInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioImageInput(self.name, self.value, self.attrs.copy(), choice, idx)

class RadioImageInput(forms.widgets.RadioInput):

    def __unicode__(self):        
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = self.choice_label
        return u'<label%s>%s %s</label>' % (label_for, self.tag(), choice_label)

    def tag(self):
        from django.utils.safestring import mark_safe
        from django.forms.util import flatatt

        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class EventForm(TendenciBaseForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Event._meta.app_label, 
        'storme_model':Event._meta.module_name.lower()}))

    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    class Meta:
        model = Event
        fields = (
            'title',
            'description', 
            'start_dt',
            'end_dt',
            'timezone',
            'type',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status',
            'status_detail',
            )

        fieldsets = [('Event Information', {
                      'fields': ['title',
                                 'description',
                                 'start_dt',
                                 'end_dt',
                                 'timezone',
                                 'type',
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
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
                    })
                    ]
        
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')




class TypeChoiceField(forms.ModelChoiceField):

    def __init__(self, queryset, empty_label=u"---------", cache_choices=False,
                 required=True, widget=None, label=None, initial=None, choices=None,
                 help_text=None, to_field_name=None, *args, **kwargs):

        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        self.cache_choices = cache_choices

        self._choices = ()
        if choices:
            self._choices = choices

        forms.fields.ChoiceField.__init__(self, choices=self._choices, widget=widget)

        self.queryset = queryset
        self.choice_cache = None
        self.to_field_name = to_field_name


class TypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TypeForm, self).__init__(*args, **kwargs)
        
        colorsets = TypeColorSet.objects.all()

        color_set_choices = [(color_set.pk, 
            '<img style="width:25px; height:25px" src="/event-logs/colored-image/%s" />'
            % color_set.bg_color) for color_set in colorsets]
        
        self.fields['color_set'] = TypeChoiceField(
            choices=color_set_choices,
            queryset=colorsets,
            widget=forms.RadioSelect(renderer=RadioImageFieldRenderer),
        )

    class Meta:
        model = Type


class PlaceForm(forms.ModelForm):
    label = 'Location Information'
    class Meta:
        model = Place


class SponsorForm(forms.ModelForm):
    label = 'Sponsor'
    class Meta:
        model = Sponsor 


class SpeakerForm(forms.ModelForm):
    label = 'Speaker'
    file = forms.FileField(required=False)

    class Meta:
        model = Speaker
        
        fields = (
            'name',
            'file',
            'description',
        )


class OrganizerForm(forms.ModelForm):
    label = 'Organizer'

    class Meta:
        model = Organizer

        fields = (
            'name',
            'description',
        )

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment

class Reg8nEditForm(BetterModelForm):
    label = 'Registration'
    limit = forms.IntegerField(
            _('Registration Limit'),
            initial=0,
            help_text=_("Enter the maximum number of registrants. Use 0 for unlimited registrants")
    )
    payment_method = forms.ModelMultipleChoiceField(
        queryset=PaymentMethod.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        initial=[1,2,3]) # first three items (inserted via fixture)

    early_dt = SplitDateTimeField(label=_('Early Date/Time'))
    regular_dt = SplitDateTimeField(label=_('Regular Date/Time'))
    late_dt = SplitDateTimeField(label=_('Late Date/Time'))
    end_dt = SplitDateTimeField(label=_('End Date/Time'))
    
    reg8n_dt_price = Reg8nDtField(label=_('Pricing and Times'), required=False)

    def clean(self):

        early_price = self.cleaned_data.get('early_price') or 0
        regular_price = self.cleaned_data.get('regular_price') or 0
        late_price = self.cleaned_data.get('late_price') or 0

        # if price is zero
        if sum([early_price, regular_price, late_price]) == 0:
            # remove payment_method error
            if "payment_method" in self._errors:
                self._errors.pop("payment_method")

        return self.cleaned_data

    class Meta:
        model = RegistrationConfiguration

        fields = (
            'payment_method',
            'early_price',
            'regular_price',
            'late_price',
            'payment_required',
            'early_dt',
            'regular_dt',
            'late_dt',
            'end_dt',
            'enabled',
            'limit',
        )

        fieldsets = [('Registration Configuration', {
          'fields': ['enabled',
                     'limit',
                     'reg8n_dt_price',
                     'payment_method',
                     'payment_required',
                     ],
          'legend': ''
          })
        ]

    def __init__(self, *args, **kwargs):
        super(Reg8nEditForm, self).__init__(*args, **kwargs)
        self.fields['reg8n_dt_price'].build_widget_reg8n_dict(*args, **kwargs)
        
class GroupReg8nEditForm(BetterModelForm):
    label = 'Group Registration'
    
    early_price = forms.DecimalField(widget=forms.TextInput(attrs={'class':'short_text_input'}))
    regular_price = forms.DecimalField(widget=forms.TextInput(attrs={'class':'short_text_input'}))
    late_price = forms.DecimalField(widget=forms.TextInput(attrs={'class':'short_text_input'}))
    early_dt = SplitDateTimeField(label=_('Early Date/Time'))
    regular_dt = SplitDateTimeField(label=_('Regular Date/Time'))
    late_dt = SplitDateTimeField(label=_('Late Date/Time'))
    end_dt = SplitDateTimeField(label=_('End Date/Time'))
    
    #reg8n_dt_price = Reg8nDtField(label=_('Times and Pricing'), required=False)
    
    def clean(self):
        
        early_price = self.cleaned_data.get('early_price') or 0
        regular_price = self.cleaned_data.get('regular_price') or 0
        late_price = self.cleaned_data.get('late_price') or 0
        
        # if price is zero
        if sum([early_price, regular_price, late_price]) == 0:
            # remove payment_method error
            if "payment_method" in self._errors:
                self._errors.pop("payment_method")
        
        return self.cleaned_data
        
    class Meta:
        model = GroupRegistrationConfiguration
        
        fields = (
            'group',
            'early_price',
            'regular_price',
            'late_price',
            'early_dt',
            'regular_dt',
            'late_dt',
            'end_dt',
        )
        
        widgets = {
            'early_price': forms.TextInput(attrs={'class':'short_text_input'}),
            'regular_price': forms.TextInput(attrs={'class':'short_text_input'}),
            'late_price': forms.TextInput(attrs={'class':'short_text_input'}),
        }
        
class SpecialPricingForm(BetterModelForm):
    label = 'Special Registration'
    
    early_price = forms.DecimalField(widget=forms.TextInput(attrs={'class':'short_text_input'}))
    regular_price = forms.DecimalField(widget=forms.TextInput(attrs={'class':'short_text_input'}))
    late_price = forms.DecimalField(widget=forms.TextInput(attrs={'class':'short_text_input'}))
    early_dt = SplitDateTimeField(label=_('Early Date/Time'))
    regular_dt = SplitDateTimeField(label=_('Regular Date/Time'))
    late_dt = SplitDateTimeField(label=_('Late Date/Time'))
    end_dt = SplitDateTimeField(label=_('End Date/Time'))
    
    def clean(self):
        
        early_price = self.cleaned_data.get('early_price') or 0
        regular_price = self.cleaned_data.get('regular_price') or 0
        late_price = self.cleaned_data.get('late_price') or 0
        
        # if price is zero
        if sum([early_price, regular_price, late_price]) == 0:
            # remove payment_method error
            if "payment_method" in self._errors:
                self._errors.pop("payment_method")
        
        return self.cleaned_data
        
    class Meta:
        model = SpecialPricing
        
        fields = (
            'title',
            'group',
            'quantity',
            'early_price',
            'regular_price',
            'late_price',
            'early_dt',
            'regular_dt',
            'late_dt',
            'end_dt',
        )
        
        widgets = {
            'early_price': forms.TextInput(attrs={'class':'short_text_input'}),
            'regular_price': forms.TextInput(attrs={'class':'short_text_input'}),
            'late_price': forms.TextInput(attrs={'class':'short_text_input'}),
        }

class Reg8nForm(forms.Form):
    """
    Registration form.
    """
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    company_name = forms.CharField(max_length=100, required=False)
    username = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField()
    captcha = CaptchaField(label=_('Type the code below'))

    def __init__(self, event_id=None, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(self.__class__, self).__init__(*args, **kwargs)

        event = Event.objects.get(pk=event_id)
        payment_method = event.registration_configuration.payment_method.all()

        self.fields['payment_method'] = forms.ModelChoiceField(empty_label=None, 
            queryset=payment_method, widget=forms.RadioSelect(), initial=1, required=False)

        self.fields['price'] = forms.DecimalField(
            widget=forms.HiddenInput(), initial=event.registration_configuration.price)

        if user and user.is_authenticated():
            self.fields.pop('captcha')
            user_fields = ['first_name', 'last_name', 'company_name', 'username', 'phone','email']
            for user_field in user_fields:
                self.fields.pop(user_field)

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        markup_pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError("Markup is not allowed in the name field")

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError("URL's and Emails are not allowed in the name field")

        return data
    
class RegistrationForm(forms.Form):
    """
    Registration form - not include the registrant.
    """
    captcha = CaptchaField(label=_('Type the code below'))

    def __init__(self, event=None, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(self.__class__, self).__init__(*args, **kwargs)

        free_event = event.registration_configuration.price <= 0
        if not free_event:
            payment_method = event.registration_configuration.payment_method.all()
    
            self.fields['payment_method'] = forms.ModelChoiceField(empty_label=None, 
                queryset=payment_method, widget=forms.RadioSelect(), initial=1, required=False)

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        markup_pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError("Markup is not allowed in the name field")

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError("URL's and Emails are not allowed in the name field")

        return data
    
class RegistrantForm(forms.Form):
    """
    Registrant form.
    """
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    company_name = forms.CharField(max_length=100, required=False)
    #username = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        self.form_index = kwargs.pop('form_index', None)
        
        super(self.__class__, self).__init__(*args, **kwargs)
        
        # make the fields in the subsequent forms as not required
        if self.form_index and self.form_index > 0:
            for key in self.fields.keys():
                self.fields[key].required = False
        

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        markup_pattern = re.compile('<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError("Markup is not allowed in the name field")

        # detect URL and Email
        pattern_string = '\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError("URL's and Emails are not allowed in the name field")

        return data
    
    def clean_email(self):
        # check if user by this email has already registered
        data = self.cleaned_data['email']
        if data.strip() <> '':
            registrants = Registrant.objects.filter(email=data)
            for registrant in registrants:
                if registrant.registration.event.id == self.event.id:
                    raise forms.ValidationError("User by this email address has already registered.")

        return data
  
# extending the BaseFormSet because i want to pass the event obj 
# but the BaseFormSet doesn't accept extra parameters 
class RegistrantBaseFormSet(BaseFormSet):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, **kwargs):
        self.event = kwargs.pop('event', None)
        super(RegistrantBaseFormSet, self).__init__(data, files, auto_id, prefix,
                 initial, error_class)
        
    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}
        
        defaults['event'] = self.event
        defaults['form_index'] = i
        
        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        return form
        
    
                
class MessageAddForm(forms.ModelForm):
    #events = forms.CharField()
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Email._meta.app_label,
        'storme_model':Email._meta.module_name.lower()}),
        label=_('Email Content'))

    payment_status = forms.ChoiceField(
        initial='all',
        widget=RadioSelect(),
        choices=(
            ('all','All'),
            ('paid','Paid'),
            ('not-paid','Not Paid'),
    ))

    class Meta:
        model = Email
        fields = ('body',)
    
    def __init__(self, event_id=None, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
