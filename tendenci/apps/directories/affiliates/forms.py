from urllib.parse import urlparse

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.urls import resolve
from django.urls.exceptions import Resolver404

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.directories.models import Directory, Category
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.emails.models import Email
from tendenci.apps.notifications import models as notification
from .models import RequestEmail, AffiliateRequest, Connection


class RequestAssociateForm(FormControlWidgetMixin, forms.ModelForm):
    from_directory_url = forms.URLField(label=_('Your Listing URL'))
    request_as = forms.ModelChoiceField(queryset=None, required=True)
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
        self.fields['from_directory_url'].widget.attrs.update({'placeholder': _('Your marketplace listing URL')})
        affiliate_cats_queryset = Category.objects.filter(id__in=Connection.objects.filter(
                                    cat__in=self.to_directory.cats.all()).values_list(
                                        'affliated_cats', flat=True)).distinct()
        self.fields['request_as'].queryset = affiliate_cats_queryset

    def clean(self):
        self.cleaned_data = super(RequestAssociateForm, self).clean()
        from_directory_url = self.cleaned_data['from_directory_url']
        request_as = self.cleaned_data['request_as']
        
        # check if this request to associate is allowed
        o = urlparse(from_directory_url)
        url_path = o.path
        try:
            resolver = resolve(url_path)
        except Resolver404:
            raise forms.ValidationError(_("Your marketplace listing is not valid. Please check your URL."))

        if 'slug' in resolver.kwargs and resolver.view_name == 'directory' \
                and Directory.objects.filter(slug=resolver.kwargs['slug']).exists():
            self.from_directory = Directory.objects.get(slug=resolver.kwargs['slug'])
            if not (self.request.user.is_superuser or self.from_directory.is_owner(self.request.user)):
                raise forms.ValidationError(_("You are not allowed to submit this listing."))
            elif not self.to_directory.can_connect_from(directory_from=self.from_directory):
                raise forms.ValidationError(_("This connection is not allowed."))
            elif request_as not in self.from_directory.cats.all():
                raise forms.ValidationError(_("This connection can not be established."))
        else:
            raise forms.ValidationError(_("Invalid marketplace listing."))

        return self.cleaned_data


    def save(self, *args, **kwargs):
        """
        Save the request form and send email notifications
        """
        self.instance = super(RequestAssociateForm, self).save(*args, **kwargs)
        [affiliate_request] = AffiliateRequest.objects.filter(
            to_directory=self.to_directory,
            from_directory=self.from_directory,
            request_as=self.cleaned_data['request_as']
            )[:1] or [None]
        if not affiliate_request:
            affiliate_request = AffiliateRequest.objects.create(
                to_directory=self.to_directory,
                from_directory=self.from_directory,
                request_as=self.cleaned_data['request_as'],
                creator= self.request.user,)
        self.instance.affiliate_request = affiliate_request
        self.instance.sender = self.request.user
        
        # get recipients emails
        self.instance.recipients = self.to_directory.get_owner_emails_list()
        
        self.instance.save()
        
        self.send_emails(self.instance)

        return self.instance

    def send_emails(self, request_email):
        # email notifications
        if request_email.recipients:
            site_display_name = get_setting('site', 'global', 'sitedisplayname')
            site_url = get_setting('site', 'global', 'siteurl')
            params = {
                'SITE_GLOBAL_SITEDISPLAYNAME': site_display_name,
                'SITE_GLOBAL_SITEURL': site_url,
                'MODULE_DIRECTORIES_LABEL_PLURAL': get_setting('module', 'directories', 'label_plural'),
                'directory': self.to_directory,
                'from_directory': self.from_directory,
                'message': request_email.message,
                'first_name': request_email.sender.first_name,
                'last_name': request_email.sender.last_name,
                'affiliate_request': self.instance.affiliate_request,
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

