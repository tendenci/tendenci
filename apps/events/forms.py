from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from events.models import Event, Type, Place, Registration, \
    Payment, Sponsor, Discount, Organizer, Speaker
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import render_to_response
from django.template import RequestContext

class EventForm(forms.ModelForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Event._meta.app_label, 
        'storme_model':Event._meta.module_name.lower()}))

    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=datetime.now())

    # location
    location_name = forms.CharField(label=_('Location Name'), max_length=255, required=False)
    location_url = forms.URLField(label=_('Location URL'), max_length=255, required=False)
    location_address = forms.CharField(label=_('Location Address'), max_length=100, required=False) 
    location_state = forms.CharField(label=_('Location State'), max_length=50, required=False) 
    location_country = forms.CharField(label=_('Location Country'), max_length=50, required=False) 
    location_phone = forms.CharField(label=_('Location Phone'), max_length=50, required=False) 

    # speaker
    speaker_name = forms.CharField(label=_('Speaker Name'), max_length=500, required=False) 
    speaker_company = forms.CharField(label=_('Speaker Company'), max_length=500, required=False)
    speaker_position = forms.CharField(label=_('Speaker Position'), max_length=500, required=False)

    # contact
    contact_name = forms.CharField(label=_('Contact Name'), max_length=100, required=False)
    contact_email = forms.CharField(label=_('Contact Email'), max_length=50, required=False)
    contact_url = forms.CharField(label=_('Contact URL'), max_length=100, required=False)
    contact_phone = forms.CharField(label=_('Contact Phone'), max_length=50, required=False)
    contact_fax = forms.CharField(label=_('Contact Fax'), max_length=50, required=False)

    # coordinator
    coord5r_name = forms.CharField(label=_('Coordinator Name'), max_length=100, required=False)
    coord5r_email = forms.CharField(label=_('Coordinator Email'), max_length=50, required=False)
    coord5r_phone = forms.CharField(label=_('Coordinator Phone'), max_length=50, required=False)
    coord5r_fax = forms.CharField(label=_('Coordinator Fax'), max_length=50, required=False)

    price = forms.DecimalField(label=_('Price'), max_digits=21, decimal_places=2, required=False)

    class Meta:
        model = Event
        fields = (
            'title',
            'description',
            'type',
            'start_dt',
            'end_dt',
            'timezone',

            'location_name',
            'location_url',
            'location_address',
            'location_state',
            'location_country',
            'location_phone',

            'speaker_name',
            'speaker_company',
            'speaker_position',

            'contact_name',
            'contact_email',
            'contact_url',
            'contact_phone',
            'contact_fax',

            'coord5r_name',
            'coord5r_email',
            'coord5r_phone',
            'coord5r_fax',

            'price',

            'private',
            'password',

#            'allow_anonymous_view',
#            'allow_user_view',
#            'allow_user_edit',
#
#            'status',
#            'status_detail',
        )

#    def __init__(self, user=None, *args, **kwargs):
#        self.user = user 
#        super(EventForm, self).__init__(user, *args, **kwargs)
#        if self.instance.pk:
#            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
#        else:
#            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

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

class Reg8nForm(forms.ModelForm):
    class Meta:
        model = Registration

class EventWizard(FormWizard):

    event = None
    place = None
    sponsor = None
    speaker = None
    organizer = None
    payment = None
    reg8n = None

    def get_template(self, step):
        return 'events/wizard.html'

    def done(self, request, form_list):

        for form in form_list:

            if isinstance(form, EventForm):
                self.event_handler(form)
            elif isinstance(form, PlaceForm):
                self.place_handler(form)
            elif isinstance(form, SpeakerForm):
                self.speaker_handler(form)
            elif isinstance(form, OrganizerForm):
                self.organizer_handler(form)
            elif isinstance(form, PaymentForm):
                self.payment_handler(form)
            elif isinstance(form, Reg8nForm):
                self.reg8n_handler(form)

        return render_to_response(
            'events/done.html', {
            'form_data': [form.cleaned_data for form in form_list]},
            context_instance=RequestContext(request))

    def event_handler(self, form):
        self.event = form.save()

    def place_handler(self, form):
        self.place = form.save(commit=False)
        if self.event:
            self.place.event = self.event
            self.place.save()

    def sponsor_handler(self, form):
        self.sponsor = form.save()

    def speaker_handler(self, form):
        self.speaker = form.save()

    def organizer_handler(self, form):
        self.organizer = form.save()

    def payment_handler(self, form):
        self.payment = form.save()

    def reg8n_handler(self, form):
        self.reg8n = form.save(commit=False)
        if self.event:
            self.reg8n.event = self.event
            self.reg8n.save()





