import imghdr
from datetime import datetime
from os.path import splitext

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms.utils import ErrorList
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.fields import SplitDateTimeField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.categories.forms import CategoryField
from tendenci.apps.directories.models import Directory, DirectoryPricing
from tendenci.apps.directories.utils import (get_payment_method_choices,
    get_duration_choices)
from tendenci.apps.directories.choices import (DURATION_CHOICES, ADMIN_DURATION_CHOICES,
    STATUS_CHOICES)
from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField, PriceField
from tendenci.apps.files.utils import get_max_file_upload_size


ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)

request_duration_defaults = {
    'label': _('Requested Duration'),
    'help_text': mark_safe(_('<a href="%s" id="add_id_pricing">Add Pricing Options</a>' % '/directories/pricing/add/')),
}

SEARCH_CATEGORIES = (
    ('', _('-- SELECT ONE --') ),
    ('id', _('Directory ID')),
    ('body', _('Body')),
    ('headline', _('Headline')),
    ('city', _('City')),
    ('state', _('State')),
    ('tags', _('Tags')),
)

SEARCH_CATEGORIES_ADMIN = SEARCH_CATEGORIES + (
    ('creator__id', _('Creator Userid(#)')),
    ('creator__username', _('Creator Username')),
    ('owner__id', _('Owner Userid(#)')),
    ('owner__username', _('Owner Username')),

    ('status_detail', _('Status Detail')),
)


class DirectorySearchForm(FormControlWidgetMixin, forms.Form):
    SEARCH_METHOD_CHOICES = (
                             ('starts_with', _('Starts With')),
                             ('contains', _('Contains')),
                             ('exact', _('Exact')),
                             )
    search_category = forms.ChoiceField(label=_('Search By'),
                                        choices=SEARCH_CATEGORIES_ADMIN, required=False)
    category = CategoryField(label=_('All Categories'), choices=[], required=False)
    sub_category = CategoryField(label=_('All Subcategories'), choices=[], required=False)
    q = forms.CharField(required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False, initial='exact')

    def __init__(self, *args, **kwargs):
        is_superuser = kwargs.pop('is_superuser', None)
        super(DirectorySearchForm, self).__init__(*args, **kwargs)

        if not is_superuser:
            self.fields['search_category'].choices = SEARCH_CATEGORIES

        categories, sub_categories = Directory.objects.get_categories()

        categories = [(cat.pk, cat) for cat in categories]
        categories.insert(0, ('', _('All Categories (%d)' % len(categories))))
        sub_categories = [(cat.pk, cat) for cat in sub_categories]
        sub_categories.insert(0, ('', _('All Subcategories (%d)' % len(sub_categories))))

        self.fields['category'].choices = categories
        self.fields['sub_category'].choices = sub_categories

    def clean(self):
        cleaned_data = self.cleaned_data
        q = self.cleaned_data.get('q', None)
        cat = self.cleaned_data.get('search_category', None)

        if cat is None or cat == "" :
            if not (q is None or q == ""):
                self._errors['search_category'] =  ErrorList(['Select a category'])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                x = int(q)
            except ValueError:
                self._errors['q'] = ErrorList(['ID must be a number.'])

        return cleaned_data


class DirectoryForm(TendenciBaseForm):
    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Directory._meta.app_label,
        'storme_model':Directory._meta.model_name.lower()}))

    logo = forms.FileField(
      required=False,
      help_text=_('Company logo. Only jpg, gif, or png images.'))

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    list_type = forms.ChoiceField(initial='regular', choices=(('regular',_('Regular')),
                                                              ('premium', _('Premium')),))
    payment_method = forms.CharField(error_messages={'required': _('Please select a payment method.')})

    activation_dt = SplitDateTimeField(initial=datetime.now())
    expiration_dt = SplitDateTimeField(initial=datetime.now())

    email = EmailVerificationField(label=_("Email"), required=False)
    email2 = EmailVerificationField(label=_("Email 2"), required=False)
    country = CountrySelectField(label=_("Country"), required=False)

    pricing = forms.ModelChoiceField(queryset=DirectoryPricing.objects.filter(status=True).order_by('duration'),
                    **request_duration_defaults)

    class Meta:
        model = Directory
        fields = (
            'headline',
            'slug',
            'summary',
            'body',
            'logo',
            'source',
            'timezone',
            'first_name',
            'last_name',
            'address',
            'address2',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'phone2',
            'fax',
            'email',
            'email2',
            'website',
            'tags',
            'pricing',
            'list_type',
            'payment_method',
            'activation_dt',
            'expiration_dt',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_user_edit',
            'syndicate',
            'user_perms',
            'member_perms',
            'group_perms',
            'status_detail',
        )

        fieldsets = [(_('Directory Information'), {
                      'fields': ['headline',
                                 'slug',
                                 'summary',
                                 'body',
                                 'logo',
                                 'tags',
                                 'source',
                                 'timezone',
                                 'activation_dt',
                                 'pricing',
                                 'expiration_dt',
                                 ],
                      'legend': ''
                      }),
                      (_('Payment'), {
                      'fields': ['list_type',
                                 'payment_method'
                                 ],
                        'classes': ['payment_method'],
                      }),
                      (_('Contact'), {
                      'fields': ['first_name',
                                 'last_name',
                                  'address',
                                  'address2',
                                  'city',
                                  'state',
                                  'zip_code',
                                  'country',
                                  'phone',
                                  'phone2',
                                  'fax',
                                  'email',
                                  'email2',
                                  'website'
                                 ],
                        'classes': ['contact'],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['syndicate',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def clean_syndicate(self):
        """
        clean method for syndicate added due to the update
        done on the field BooleanField -> NullBooleanField
        NOTE: BooleanField is converted to NullBooleanField because
        some Boolean data has value of None than False. This was updated
        on Django 1.6. BooleanField cannot have a value of None.
        """
        data = self.cleaned_data.get('syndicate', False)
        if data:
            return True
        else:
            return False

    def clean_logo(self):
        logo = self.cleaned_data['logo']
        if logo:
            try:
                extension = splitext(logo.name)[1]

                # check the extension
                if extension.lower() not in ALLOWED_LOGO_EXT:
                    raise forms.ValidationError(_('The logo must be of jpg, gif, or png image type.'))

                # check the image header
                image_type = '.%s' % imghdr.what('', logo.read())
                if image_type not in ALLOWED_LOGO_EXT:
                    raise forms.ValidationError(_('The logo is an invalid image. Try uploading another logo.'))

                max_upload_size = get_max_file_upload_size()
                if logo.size > max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(logo_size)s') % {
                                                    'max_upload_size': filesizeformat(max_upload_size),
                                                    'logo_size': filesizeformat(logo.size)})
            except IOError:
                logo = None

        return logo

    def clean_headline(self):
        """
        remove extra leading and trailing white spaces
        """
        return self.cleaned_data.get('headline', '').strip()

    def __init__(self, *args, **kwargs):
        super(DirectoryForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if self.user.profile.is_superuser:
                self.fields['status_detail'].choices = (('active',_('Active')),
                                                        ('inactive',_('Inactive')),
                                                        ('pending',_('Pending')),
                                                        ('paid - pending approval', _('Paid - Pending Approval')),)
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

        if self.instance.logo:
            self.initial['logo'] = self.instance.logo

        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if self.fields.has_key('payment_method'):
            self.fields['payment_method'] = forms.ChoiceField(widget=forms.RadioSelect, choices=get_payment_method_choices(self.user))
        if self.fields.has_key('pricing'):
            self.fields['pricing'].choices = get_duration_choices(self.user)

        self.fields['timezone'].initial = settings.TIME_ZONE

        # expiration_dt = activation_dt + requested_duration
        fields_to_pop = ['expiration_dt']
        if not self.user.profile.is_superuser:
            fields_to_pop += [
                'slug',
                'entity',
                'allow_anonymous_view',
                'user_perms',
                'member_perms',
                'group_perms',
                'post_dt',
                'activation_dt',
                'syndicate',
                'status_detail'
            ]

        for f in list(set(fields_to_pop)):
            if f in self.fields:
                self.fields.pop(f)

    def save(self, *args, **kwargs):
        from tendenci.apps.files.models import File
        directory = super(DirectoryForm, self).save(*args, **kwargs)

        content_type = ContentType.objects.get(
                app_label=Directory._meta.app_label,
                model=Directory._meta.model_name)

        if self.cleaned_data.has_key('pricing'):
            directory.requested_duration = self.cleaned_data['pricing'].duration

        if self.cleaned_data['logo']:
            file_object, created = File.objects.get_or_create(
                file=self.cleaned_data['logo'],
                defaults={
                    'name': self.cleaned_data['logo'].name,
                    'content_type': content_type,
                    'object_id': directory.pk,
                    'is_public': directory.allow_anonymous_view,
                    'tags': directory.tags,
                })

            directory.logo_file = file_object
            directory.save(log=False)

        # clear logo; if box checked
        if self.cleaned_data['logo'] is False:
          directory.logo_file = None
          directory.save(log=False)
          File.objects.filter(
            content_type=content_type,
            object_id=directory.pk).delete()

        return directory


class DirectoryPricingForm(forms.ModelForm):
    status = forms.ChoiceField(initial=1, choices=STATUS_CHOICES, required=False)
    regular_price = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)
    premium_price = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)
    regular_price_member = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)
    premium_price_member = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)

    class Meta:
        model = DirectoryPricing
        fields = ('duration',
                  'regular_price',
                  'premium_price',
                  'regular_price_member',
                  'premium_price_member',
                  'show_member_pricing',
                  'status',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DirectoryPricingForm, self).__init__(*args, **kwargs)
        if user and user.profile.is_superuser:
            self.fields['duration'] = forms.ChoiceField(initial=14, choices=ADMIN_DURATION_CHOICES)
        else:
            self.fields['duration'] = forms.ChoiceField(initial=14, choices=DURATION_CHOICES)


class DirectoryRenewForm(TendenciBaseForm):
    list_type = forms.ChoiceField(initial='regular', choices=(('regular',_('Regular')),
                                                              ('premium', _('Premium')),))
    payment_method = forms.CharField(error_messages={'required': _('Please select a payment method.')})

    pricing = forms.ModelChoiceField(label=_('Requested Duration'),
                    queryset=DirectoryPricing.objects.filter(status=True).order_by('duration'))

    class Meta:
        model = Directory
        fields = (
            'pricing',
            'list_type',
            'payment_method',
        )

        fieldsets = [(_('Payment'), {
                      'fields': ['list_type',
                                 'pricing',
                                 'payment_method'
                                 ],
                        'classes': ['payment_method'],
                    })]

    def __init__(self, *args, **kwargs):
        super(DirectoryRenewForm, self).__init__(*args, **kwargs)

        if self.fields.has_key('payment_method'):
            self.fields['payment_method'].widget = forms.RadioSelect(choices=get_payment_method_choices(self.user))
        if self.fields.has_key('pricing'):
            self.fields['pricing'].choices = get_duration_choices(self.user)

    def save(self, *args, **kwargs):
        directory = super(DirectoryRenewForm, self).save(*args, **kwargs)
        if self.cleaned_data.has_key('pricing'):
            directory.requested_duration = self.cleaned_data['pricing'].duration
        return directory


class DirectoryExportForm(forms.Form):

    STATUS_DETAIL_CHOICES = (
        ('', _('Export All Directories')),
        ('active', _(' Export Active Directories')),
        ('pending', _('Export Pending Directories')),
        ('inactive', _('Export Inactive Directories')),
    )

    EXPORT_FIELD_CHOICES = (
        ('main_fields', _('Export Main Fields (fastest)')),
        ('all_fields', _('Export All Fields')),
    )

    export_format = forms.CharField(widget=forms.HiddenInput(), initial='csv')
    export_status_detail = forms.ChoiceField(choices=STATUS_DETAIL_CHOICES, required=False)
    export_fields = forms.ChoiceField(choices=EXPORT_FIELD_CHOICES)

