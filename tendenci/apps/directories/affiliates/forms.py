from urllib.parse import urlparse

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.urls import resolve
from django.urls.exceptions import Resolver404

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.directories.models import Directory
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.emails.models import Email
from tendenci.apps.notifications import models as notification
from .models import RequestEmail, AffiliateRequest
from .utils import get_content_from_template


class RequestAssociateForm(FormControlWidgetMixin, forms.ModelForm):
    from_directory_url = forms.URLField(label=_('Your Listing'))
    message = forms.CharField(max_length=1000,
                               widget=forms.Textarea(attrs={'rows':'3'}))
    
    
    class Meta:
        model = RequestEmail
        fields = (
            'from_directory_url',
            'message')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.to_directory = kwargs.pop('to_directory')
        super(RequestAssociateForm, self).__init__(*args, **kwargs)
        self.fields['from_directory_url'].help_text = _('Example: %s/%s/example/') % (
                                        get_setting('site', 'global', 'siteurl'),
                                        get_setting('module', 'directories', 'url'))
        self.fields['from_directory_url'].widget.attrs.update({'placeholder': _('Your marketplace listing')})

    def clean_from_directory_url(self):
        from_directory_url = self.cleaned_data['from_directory_url']
        
        # check if this request to associate is allowed
        o = urlparse(from_directory_url)
        url_path = o.path
        try:
            resolver = resolve(url_path)
        except Resolver404:
            raise forms.ValidationError(_("Your marketplace listing is not valid. Please check your URL."))

        if 'slug' in resolver.kwargs and Directory.objects.filter(slug=resolver.kwargs['slug']).exists():
            self.from_directory = Directory.objects.get(slug=resolver.kwargs['slug'])
            if not self.to_directory.can_connect_from(self.from_directory):
                raise forms.ValidationError(_("This connection is not allowed."))
        else:
            raise forms.ValidationError(_("Invalid marketplace listing."))

        
        return self.cleaned_data
    
    def save(self, *args, **kwargs):
        """
        Save the request form and send email notifications
        """
        request_email = super(RequestAssociateForm, self).save(*args, **kwargs)
        [affiliate_request] = AffiliateRequest.objects.filter(
            to_directory=self.to_directory,
            from_directory=self.from_directory,
            )[:1] or [None]
        if not affiliate_request:
            affiliate_request = AffiliateRequest.objects.create(
                to_directory=self.to_directory,
                from_directory=self.from_directory,
                creator= self.request.user,)
        request_email.affiliate_request = affiliate_request
        request_email.sender = self.request.user
        
        # get recipients emails
        request_email.recipients = self.to_directory.get_owner_emails_list()
        
        request_email.save()
        
        self.send_emails(request_email)

        return request_email

    def send_emails(self, request_email):
        # email notifications
        if request_email.recipients:
            site_display_name = get_setting('site', 'global', 'sitedisplayname')
            site_url = get_setting('site', 'global', 'siteurl')
            params = {
                'SITE_GLOBAL_SITEDISPLAYNAME': site_display_name,
                'SITE_GLOBAL_SITEURL': site_url,
                'directory': self.to_directory,
                'from_directory': self.from_directory,
                'message': request_email.message,
                'first_name': request_email.sender.first_name,
                'last_name': request_email.sender.last_name,
            }
            
            # to to_directory owner
            params['reply_to'] = request_email.sender.email
            notification.send_emails(request_email.recipients,
                    'affiliate_requested_to_owner', params)

            # to submitter
            submitter_email = (request_email.sender.email).strip()
            params['reply_to'] = request_email.recipients[0]
            notification.send_emails([submitter_email],
                    'affiliate_requested_to_submitter', params)

