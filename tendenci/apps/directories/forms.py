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
from django.urls import reverse

from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.directories.models import Directory, DirectoryPricing
from tendenci.apps.directories.models import Category as DirectoryCategory
from tendenci.apps.directories.utils import (get_payment_method_choices,
    get_duration_choices)
from tendenci.apps.directories.choices import (DURATION_CHOICES, ADMIN_DURATION_CHOICES,
    STATUS_CHOICES)
from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField, PriceField
from tendenci.apps.files.utils import get_max_file_upload_size
from tendenci.apps.regions.models import Region
from tendenci.apps.site_settings.utils import get_setting


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
    ('headline', _('Name')),
    ('body', _('Description')),
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
    region = forms.ModelChoiceField(label=_("Region"),
                                      queryset=Region.objects.filter(status_detail='active'),
                                      empty_label="-----------",
                                      required=False)
    cat = forms.MultipleChoiceField(label=_("Category"),
                                      required=False)
    sub_cat = forms.MultipleChoiceField(label=_("Subcategory"),
                                          required=False)
    q = forms.CharField(required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False, initial='exact')

    def __init__(self, *args, **kwargs):
        is_superuser = kwargs.pop('is_superuser', None)
        super(DirectorySearchForm, self).__init__(*args, **kwargs)

        if not is_superuser:
            self.fields['search_category'].choices = SEARCH_CATEGORIES

        # setup categories
        categories = DirectoryCategory.objects.filter(parent__isnull=True)
        categories_count = categories.count()
        empty_label =  _('ALL Categories (%(c)s)' % {'c' : categories_count})
        self.fields['cat'].choices = _get_cats_choices(empty_label=empty_label)
        self.fields['sub_cat'].choices = _get_sub_cats_choices(empty_label=_('ALL SubCategories'))
        # remove region field if no directories associated with any region
        if not Directory.objects.filter(region__isnull=False).exists():
            del self.fields['region']

        if 'sub_cat' in self.fields and get_setting('module', 'directories', 'disablesubcategories'):
            self.fields.pop('sub_cat')

    def clean(self):
        cleaned_data = super(DirectorySearchForm, self).clean()
        q = cleaned_data.get('q', None)
        cat = cleaned_data.get('search_category', None)

        if cat is None or cat == "" :
            if not (q is None or q == "" or 'tag:' in q):
                self._errors['search_category'] =  ErrorList(['Select a category'])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                int(q)
            except ValueError:
                self._errors['q'] = ErrorList(['ID must be a number.'])

        return cleaned_data


def _get_cats_choices(directory=None, empty_label=None):
    if empty_label:
        choices = [('', empty_label),]
    else:
        choices = []
    cats = DirectoryCategory.objects.filter(parent=None)
    if directory:
        cats = cats.filter(id__in=directory.cats.all())
    for cat in cats:
        choices.append((cat.id, cat.name))

    return choices


def _get_sub_cats_choices(directory=None, empty_label=None):
    if empty_label:
        choices = [('', empty_label),]
    else:
        choices = []
    cats = DirectoryCategory.objects.filter(parent=None)
    if cats.exists():
        if directory and directory.id:
            cats = cats.filter(id__in=directory.cats.all())
        for cat in cats:
            my_choices = []
            sub_cats = DirectoryCategory.objects.filter(parent=cat)
            for sub_cat in sub_cats:
                my_choices.append((sub_cat.id, sub_cat.name))
            if my_choices:
                choices.append((cat.name, my_choices))
    return choices


class DirectoryForm(TendenciBaseForm):
    body = forms.CharField(label=_("Description"), required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Directory._meta.app_label,
        'storme_model':Directory._meta.model_name.lower()}))

    logo = forms.FileField(
      required=False,
      help_text=_('Company logo. Only jpg, gif, or png images.'))

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')), ('expired',_('Expired')),))

    list_type = forms.ChoiceField(initial='regular', choices=(('regular',_('Regular')),
                                                              ('premium', _('Premium')),))
    payment_method = forms.CharField(error_messages={'required': _('Please select a payment method.')})

    activation_dt = forms.SplitDateTimeField(initial=datetime.now())
    expiration_dt = forms.SplitDateTimeField(initial=datetime.now())

    email = EmailVerificationField(label=_("Email"), required=False)
    email2 = EmailVerificationField(label=_("Email 2"), required=False)
    country = CountrySelectField(label=_("Country"), required=False)

    pricing = forms.ModelChoiceField(queryset=DirectoryPricing.objects.filter(status=True).order_by('duration'),
                    **request_duration_defaults)

    cats = forms.ModelMultipleChoiceField(label=_("Categories"),
                                          queryset=DirectoryCategory.objects.filter(parent=None),
                                          required=False,
                                          help_text=_('Hold down "Control", or "Command" on a Mac, to select more than one.'))
    sub_cats = forms.ModelMultipleChoiceField(label=_("Subcategories"),
                                          queryset=None,
                                          required=False,
                                          help_text=_('Please choose a category first'))

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
            'region',
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
            'linkedin',
            'facebook',
            'twitter',
            'instagram',
            'youtube',
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
            'cats',
            'sub_cats',
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
                                 'region',
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
                     (_('Social Media'), {
                      'fields': ['linkedin',
                                 'facebook',
                                  'twitter',
                                  'instagram',
                                  'youtube',
                                 ],
                        'classes': ['social-media'],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
#                       (_('Category'), {
#                         'fields': ['cats',
#                                    'sub_cats'
#                                    ],
#                         'classes': ['boxy-grey job-category'],
#                       }),
                     (_('Administrator Only'), {
                      'fields': ['cats',
                                 'sub_cats',
                                 'syndicate',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(DirectoryForm, self).__init__(*args, **kwargs)
        self.fields['headline'].help_text = _('Company or Organization name')
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
        self.logo_extension_error_message = _('The logo must be of jpg, gif, or png image type.')
        self.logo_mime_error_message = _('The logo is an invalid image. Try uploading another logo.')
        if self.instance.pk:
            if self.instance.get_membership():
                # individual - display "Photo" instead of Logo
                self.fields['logo'].label = _('Photo')
                self.fields['logo'].help_text=_('Only jpg, gif, or png images.')
                self.logo_extension_error_message = _('The photo must be of jpg, gif, or png image type.')
                self.logo_mime_error_message = _('The photo is an invalid image. Try uploading another photo.')
            

        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if 'payment_method' in self.fields:
            self.fields['payment_method'] = forms.ChoiceField(widget=forms.RadioSelect, choices=get_payment_method_choices(self.user))
        if 'pricing' in self.fields:
            self.fields['pricing'].choices = get_duration_choices(self.user)

        self.fields['timezone'].initial = settings.TIME_ZONE

        # cat and sub_cat
        self.fields['sub_cats'].queryset = DirectoryCategory.objects.exclude(parent=None)
        self.fields['sub_cats'].choices = _get_sub_cats_choices(directory=self.instance)
        
        if self.user.profile.is_superuser:
            self.fields['sub_cats'].help_text = mark_safe('<a href="{0}">{1}</a>'.format(
                                        reverse('admin:directories_category_changelist'),
                                        _('Manage Categories'),))
#         if self.instance and self.instance.pk:
#             self.fields['sub_cats'].queryset = DirectoryCategory.objects.filter(
#                                                         parent__in=self.instance.cats.all())
#         if args:
#             post_data = args[0]
#         else:
#             post_data = None
#         if post_data:
#             cats = post_data.get('cats', None)
#             if cats:
#                 cats = [int(cat) for cat in cats if cat.isdigit()]
#                 cats = DirectoryCategory.objects.filter(pk__in=cats)
#                 self.fields['sub_cats'].queryset = DirectoryCategory.objects.filter(parent__in=cats)

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
                'cats',
                'sub_cats',
                'status_detail'
            ]

        for f in list(set(fields_to_pop)):
            if f in self.fields:
                self.fields.pop(f)

        if 'sub_cats' in self.fields and get_setting('module', 'directories', 'disablesubcategories'):
            self.fields.pop('sub_cats')

        if 'sub_cats' not in self.fields:
            if self.user.profile.is_superuser:
                self.fields['cats'].help_text += mark_safe('<br /><a href="{0}">{1}</a>'.format(
                            reverse('admin:directories_category_changelist'),
                            _('Manage Categories'),))
            

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
                    raise forms.ValidationError(self.logo_extension_error_message)

                # check the image header
                image_type = '.%s' % imghdr.what('', logo.read())
                if image_type not in ALLOWED_LOGO_EXT:
                    raise forms.ValidationError(self.logo_mime_error_message)

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

    def save(self, *args, **kwargs):
        from tendenci.apps.files.models import File
        directory = super(DirectoryForm, self).save(*args, **kwargs)

        content_type = ContentType.objects.get(
                app_label=Directory._meta.app_label,
                model=Directory._meta.model_name)

        if 'pricing' in self.cleaned_data:
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
                    'creator': self.user,
                    'owner': self.user,
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

        if 'payment_method' in self.fields:
            self.fields['payment_method'].widget = forms.RadioSelect(choices=get_payment_method_choices(self.user))
        if 'pricing' in self.fields:
            self.fields['pricing'].choices = get_duration_choices(self.user)

    def save(self, *args, **kwargs):
        directory = super(DirectoryRenewForm, self).save(*args, **kwargs)
        if 'pricing' in self.cleaned_data:
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
