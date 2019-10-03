from datetime import datetime

from django import forms
from django.contrib.admin import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

# from captcha.fields import CaptchaField
from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.jobs.models import Job
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.fields import EmailVerificationField, CountrySelectField, PriceField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.jobs.models import JobPricing
from tendenci.apps.jobs.models import Category as JobCategory
from tendenci.apps.jobs.utils import get_payment_method_choices, pricing_choices
from tendenci.apps.user_groups.models import Group
from tendenci.apps.base.forms import CustomCatpchaField


request_duration_defaults = {
    'label': _('Requested Duration'),
    'help_text': mark_safe('<a href="%s" id="add_id_pricing">Add Pricing Options</a>' % '/admin/jobs/jobpricing/add/'),
}

DURATION_CHOICES = (
    (14, _('14 Days from Activation date')),
    (30, _('30 Days from Activation date')),
    (60, _('60 Days from Activation date')),
    (90, _('90 Days from Activation date')),
    (120, _('120 Days from Activation date')),
    (180, _('180 Days from Activation date')),
    (365, _('365 Days from Activation date')),
)


STATUS_DETAIL_CHOICES = (
    ('active', _('Active')),
    ('inactive', _('Inactive')),
    ('pending', _('Pending')),
    ('paid - pending approval', _('Paid - Pending Approval')),
)

STATUS_CHOICES = (
    (1, _('Active')),
    (0, _('Inactive')),
)

class JobForm(TendenciBaseForm):

    description = forms.CharField(
        required=False,
        widget=TinyMCE(
            attrs={'style': 'width:100%'},
            mce_attrs={'storme_app_label': Job._meta.app_label, 'storme_model': Job._meta.model_name.lower()}
        )
    )

    captcha = CustomCatpchaField(label=_('Type the code below'))

    start_dt = forms.SplitDateTimeField(
        required=False,
        label=_('Position starts on:'),
        initial=datetime.now())

    activation_dt = forms.SplitDateTimeField(
        label=_('Activation Date/Time'),
        initial=datetime.now())

    post_dt = forms.SplitDateTimeField(
        label=_('Post Date/Time'),
        initial=datetime.now())

    expiration_dt = forms.SplitDateTimeField(
        label=_('Expiration Date/Time'),
        initial=datetime.now())

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)

    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')), ('inactive', _('Inactive')), ('pending', _('Pending')),))

    list_type = forms.ChoiceField(initial='regular', choices=(('regular', _('Regular')),
                                                              ('premium', _('Premium')),))
    payment_method = forms.ChoiceField(error_messages={'required': _('Please select a payment method.')})

    contact_email = EmailVerificationField(label=_("Contact email"), required=False)
    contact_country = CountrySelectField(label=_("Contact country"), required=False)

    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=True, empty_label=None)

    pricing = forms.ModelChoiceField(queryset=JobPricing.objects.filter(status=True).order_by('duration'),
                **request_duration_defaults)
    cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=JobCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)
    sub_cat = forms.ModelChoiceField(label=_("Subcategory"),
                                          queryset=JobCategory.objects.none(),
                                          empty_label=_("Please choose a category first"),
                                          required=False)

    class Meta:
        model = Job
        fields = (
            'title',
            'slug',
            'description',
            'group',
            'code',
            'location',
            'skills',
            'experience',
            'education',
            'level',
            'period',
            'is_agency',
            'contact_method',
            'position_reports_to',
            'salary_from',
            'salary_to',
            'computer_skills',
            'tags',
            'pricing',
            'list_type',
            'start_dt',
            'activation_dt',
            'post_dt',
            'expiration_dt',
            'job_url',
            'entity',
            'contact_company',
            'contact_name',
            'contact_address',
            'contact_address2',
            'contact_city',
            'contact_state',
            'contact_zip_code',
            'contact_country',
            'contact_phone',
            'contact_fax',
            'contact_email',
            'contact_website',
            'tags',
            'allow_anonymous_view',
            'syndicate',
            'status_detail',
            'payment_method',
            'cat',
            'sub_cat'
        )

        fieldsets = [
            (_('Job Information'), {
                'fields': [
                    'title',
                    'slug',
                    'description',
                    'group',
                    'job_url',
                    'start_dt',
                    'code',
                    'location',
                    'skills',
                    'computer_skills',
                    'experience',
                    'education',
                    'level',
                    'period',
                    'contact_method',
                    'position_reports_to',
                    'salary_from',
                    'salary_to',
                    'is_agency',
                    'tags',
                    'pricing',
                    'activation_dt',
                    'expiration_dt',
                    'post_dt',
                    'entity'
                ],
                'legend': ''
            }),
            (_('Payment'), {
                'fields': ['list_type',
                           'payment_method'],
                'classes': ['payment_method'],
            }),
            (_('Contact'), {
                'fields': [
                    'contact_company',
                    'contact_name',
                    'contact_address',
                    'contact_address2',
                    'contact_city',
                    'contact_state',
                    'contact_zip_code',
                    'contact_country',
                    'contact_phone',
                    'contact_fax',
                    'contact_email',
                    'contact_website'
                ],
                'classes': ['contact'],
            }),
            (_('Security Code'), {
                'fields': ['captcha'],
                'classes': ['captcha'],
            }),
            (_('Permissions'), {
                'fields': [
                    'allow_anonymous_view',
                    'user_perms',
                    'member_perms',
                    'group_perms',
                ],
                'classes': ['permissions'],
            }),
            (_('Category'), {
                    'fields': ['cat',
                               'sub_cat'
                               ],
                    'classes': ['boxy-grey job-category'],
                  }),
            (_('Administrator Only'), {
                'fields': ['syndicate',
                           'status_detail'],
                'classes': ['admin-only'],
            })]

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'user'):
            kwargs.update({'user': self.user})
        super(JobForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            #self.fields['pricing'].initial = JobPricing.objects.filter(duration=self.instance.requested_duration)[0]
            if self.user.profile.is_superuser:
                self.fields['status_detail'].choices = STATUS_DETAIL_CHOICES
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['group'].initial = Group.objects.get_initial_group_id()

        # cat and sub_cat
        if self.user.profile.is_superuser:
            self.fields['sub_cat'].help_text = mark_safe('<a href="{0}">{1}</a>'.format(
                                        reverse('admin:jobs_category_changelist'),
                                        _('Manage Categories'),))
        if self.instance and self.instance.pk:
            self.fields['sub_cat'].queryset = JobCategory.objects.filter(
                                                        parent=self.instance.cat)
        if args:
            post_data = args[0]
        else:
            post_data = None
        if post_data:
            cat = post_data.get('cat', '0')
            if cat and cat != '0' and cat != u'':
                cat = JobCategory.objects.get(pk=int(cat))
                self.fields['sub_cat'].queryset = JobCategory.objects.filter(parent=cat)

        self.fields['pricing'].choices = pricing_choices(self.user)

        if 'payment_method' in self.fields:
            choices=get_payment_method_choices(self.user)
            self.fields['payment_method'].widget = forms.RadioSelect(choices=choices)
            self.fields['payment_method'].choices = choices
            #self.fields['payment_method'].widget = forms.RadioSelect(choices=choices)
            if choices and len(choices) == 1:
                self.fields['payment_method'].initial = choices[0][0]

        # adjust fields depending on user status
        fields_to_pop = []
        if not self.user.is_authenticated:
            fields_to_pop += [
                'entity',
                'allow_anonymous_view',
                'user_perms',
                'group_perms',
                'member_perms',
                'post_dt',
                'activation_dt',
                'expiration_dt',
                'syndicate',
                'status_detail'
            ]
        else:
            fields_to_pop += [
                'captcha'
            ]

        if not self.user.profile.is_superuser:
            fields_to_pop += [
                'slug',
                'entity',
                'group',
                'allow_anonymous_view',
                'user_perms',
                'member_perms',
                'group_perms',
                'post_dt',
                'activation_dt',
                'expiration_dt',
                'syndicate',
                'status_detail'
            ]

        for f in list(set(fields_to_pop)):
            if f in self.fields:
                self.fields.pop(f)

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

    def save(self, *args, **kwargs):
        """
        Assigns the requested_duration of a job based on the
        chosen pricing.
        """
        job = super(JobForm, self).save(commit=False)
        if 'pricing' in self.cleaned_data:
            job.requested_duration = self.cleaned_data['pricing'].duration
        if kwargs['commit']:
            job.save()
        return job


class JobAdminForm(JobForm):
    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'user'):
            kwargs.update({'user': self.user})
        super(JobAdminForm, self).__init__(*args, **kwargs)

        if hasattr(self, 'user'):
            self.fields['activation_dt'] = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), initial=datetime.now())
            self.fields['expiration_dt'] = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), initial=datetime.now())
            self.fields['post_dt'] = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), initial=datetime.now())

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


class JobPricingForm(forms.ModelForm):
    duration = forms.ChoiceField(initial=14, choices=DURATION_CHOICES)
    status = forms.ChoiceField(initial=1, choices=STATUS_CHOICES, required=False)
    regular_price = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)
    premium_price = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)
    regular_price_member = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)
    premium_price_member = PriceField(max_digits=15, decimal_places=2, initial=0, required=False)

    class Meta:
        model = JobPricing
        fields = (
            'title',
            'duration',
            'regular_price',
            'premium_price',
            'regular_price_member',
            'premium_price_member',
            'include_tax',
            'tax_rate',
            'show_member_pricing',
            'status',
        )


class JobSearchForm(FormControlWidgetMixin, forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=JobCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)
    sub_cat = forms.ModelChoiceField(label=_("Subcategory"),
                                          queryset=JobCategory.objects.none(),
                                          empty_label=_("Subcategories"),
                                          required=False)

    def __init__(self, *args, **kwargs):
        super(JobSearchForm, self).__init__(*args, **kwargs)

        # setup categories
        categories = JobCategory.objects.filter(parent__isnull=True)
        categories_count = categories.count()
        self.fields['cat'].queryset = categories
        self.fields['cat'].empty_label = _('Categories (%(c)s)' % {'c' : categories_count})
        data = args[0]
        if data:
            try:
                cat = int(data.get('cat', 0))
            except ValueError:
                cat = 0
            if cat:
                sub_categories = JobCategory.objects.filter(parent__id=cat)
                sub_categories_count = sub_categories.count()
                self.fields['sub_cat'].empty_label = _('Subcategories (%(c)s)' % {'c' : sub_categories_count})
                self.fields['sub_cat'].queryset = sub_categories
