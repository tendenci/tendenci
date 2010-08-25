from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from events.models import Event, Place, RegistrationConfiguration, \
    Payment, PaymentMethod, Sponsor, Organizer, Speaker, Type
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

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
            'allow_user_view',
            'allow_user_edit',
            'status',
            'status_detail',
            )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(self.__class__, self).__init__(self.user, *args, **kwargs)
        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

class TypeForm(forms.ModelForm):

    class Meta:
        model = Type

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place

class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor

class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker

class OrganizerForm(forms.ModelForm):
    class Meta:
        model = Organizer

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment

class Reg8nEditForm(forms.ModelForm):

    payment_method = forms.ModelMultipleChoiceField(
        queryset=PaymentMethod.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        initial=[1,2,3]) # first three items (inserted via fixture)

    early_dt = SplitDateTimeField(label=_('Early Date/Time'))
    regular_dt = SplitDateTimeField(label=_('Regular Date/Time'))
    late_dt = SplitDateTimeField(label=_('Late Date/Time'))

    class Meta:
        model = RegistrationConfiguration

class Reg8nForm(forms.Form):
    """
    Registration form.  People who want to attend the event
    register using this form.
    """
    def __init__(self, event_id=None, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        event = Event.objects.get(pk=event_id)
        payment_method = event.registration_configuration.payment_method.all()

        self.fields['payment_method'] = forms.ModelChoiceField(
            queryset=payment_method, widget=forms.RadioSelect(), initial=1)

        self.fields['price'] = forms.DecimalField(
            widget=forms.HiddenInput(), initial=event.registration_configuration.price())
