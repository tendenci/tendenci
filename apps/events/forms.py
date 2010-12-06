from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField

from events.models import Event, Place, RegistrationConfiguration, \
    Payment, PaymentMethod, Sponsor, Organizer, Speaker, Type, TypeColorSet
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField
from emails.models import Email

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

    color_set_choices = [(color_set.pk, 
        '<img style="width:25px; height:25px" src="/event-logs/colored-image/%s" />'
        % color_set.bg_color) for color_set in TypeColorSet.objects.all()]

    color_set = TypeChoiceField(
        choices=color_set_choices,
        queryset=TypeColorSet.objects.all(),
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
    class Meta:
        model = Speaker
        
        fields = (
            'name',
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

class Reg8nEditForm(forms.ModelForm):
    label = 'Registration'
    payment_method = forms.ModelMultipleChoiceField(
        queryset=PaymentMethod.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        initial=[1,2,3]) # first three items (inserted via fixture)

    def clean(self):

        early_price = self.cleaned_data["early_price"]
        regular_price = self.cleaned_data["regular_price"]
        late_price = self.cleaned_data["late_price"]

        # if price is zero
        if sum([early_price, regular_price, late_price]) == 0:
            # remove payment_method error
            if "payment_method" in self._errors:
                self._errors.pop("payment_method")

        return self.cleaned_data

    early_dt = SplitDateTimeField(label=_('Early Date/Time'))
    regular_dt = SplitDateTimeField(label=_('Regular Date/Time'))
    late_dt = SplitDateTimeField(label=_('Late Date/Time'))

    class Meta:
        model = RegistrationConfiguration

class Reg8nForm(forms.Form):
    """
    Registration form.
    """
    name = forms.CharField(max_length=50)
    username = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    captcha = CaptchaField(label=_('Type the code below'))

    def __init__(self, event_id=None, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(self.__class__, self).__init__(*args, **kwargs)

        event = Event.objects.get(pk=event_id)
        payment_method = event.registration_configuration.payment_method.all()

        self.fields['payment_method'] = forms.ModelChoiceField(
            queryset=payment_method, widget=forms.RadioSelect(), initial=1, required=False)

        self.fields['price'] = forms.DecimalField(
            widget=forms.HiddenInput(), initial=event.registration_configuration.price)

        if user and user.is_authenticated():
            self.fields.pop('captcha')
            user_fields = ['name', 'username', 'email']
            for user_field in user_fields:
                self.fields.pop(user_field)
                
class MessageAddForm(forms.ModelForm):
    #events = forms.CharField()
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'}, 
                                          mce_attrs={'storme_app_label':'Message', 
                                                    'storme_model':Email._meta.module_name.lower()}),
                            label=_('Email Content'))
    
    class Meta:
        model = Email
        fields = ('body',
                  )
    
    def __init__(self, event_id=None, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
       


