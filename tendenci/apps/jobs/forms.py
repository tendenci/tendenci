from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.admin import widgets

from captcha.fields import CaptchaField
from tendenci.core.categories.models import Category
from tendenci.addons.jobs.models import Job
from tendenci.core.perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from tendenci.core.base.fields import SplitDateTimeField, EmailVerificationField, CountrySelectField, PriceField
from tendenci.addons.jobs.models import JobPricing
from tendenci.addons.jobs.utils import get_payment_method_choices, pricing_choices
from tendenci.apps.user_groups.models import Group


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
            mce_attrs={'storme_app_label': Job._meta.app_label, 'storme_model': Job._meta.module_name.lower()}
        )
    )

    captcha = CaptchaField(label=_('Type the code below'))

    start_dt = SplitDateTimeField(
        required=False,
        label=_('Position starts on:'),
        initial=datetime.now())

    activation_dt = SplitDateTimeField(
        label=_('Activation Date/Time'),
        initial=datetime.now())

    post_dt = SplitDateTimeField(
        label=_('Post Date/Time'),
        initial=datetime.now())

    expiration_dt = SplitDateTimeField(
        label=_('Expiration Date/Time'),
        initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')), ('inactive', _('Inactive')), ('pending', _('Pending')),))

    list_type = forms.ChoiceField(initial='regular', choices=(('regular', _('Regular')),
                                                              ('premium', _('Premium')),))
    payment_method = forms.CharField(error_messages={'required': _('Please select a payment method.')})

    contact_email = EmailVerificationField(label=_("Contact email"), required=False)
    contact_country = CountrySelectField(label=_("Contact country"), required=False)

    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=True, empty_label=None)

    pricing = forms.ModelChoiceField(queryset=JobPricing.objects.filter(status=True).order_by('duration'),
                **request_duration_defaults)

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

        self.fields['pricing'].choices = pricing_choices(self.user)

        if 'payment_method' in self.fields:
            self.fields['payment_method'].widget = forms.RadioSelect(choices=get_payment_method_choices(self.user))

        # adjust fields depending on user status
        fields_to_pop = []
        if not self.user.is_authenticated():
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

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'user'):
            kwargs.update({'user': self.user})
        super(JobAdminForm, self).__init__(*args, **kwargs)

        if hasattr(self, 'user'):
            self.fields['activation_dt'] = forms.DateTimeField(widget=widgets.AdminSplitDateTime(), initial=datetime.now())
            self.fields['expiration_dt'] = forms.DateTimeField(widget=widgets.AdminSplitDateTime(), initial=datetime.now())
            self.fields['post_dt'] = forms.DateTimeField(widget=widgets.AdminSplitDateTime(), initial=datetime.now())


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


class JobSearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    categories = forms.ChoiceField(required=False)
    subcategories = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super(JobSearchForm, self).__init__(*args, **kwargs)

        # setup categories
        (categories, sub_categories) = Category.objects.get_for_model(Job)
        cat_length = len(categories)
        cat_choices = [('', _('Categories (%(l)s)' % {'l' : cat_length}))]
        for category in categories:
            cat_choices.append((category.pk, category.name))

        query_string = args[0]
        category = query_string.get('categories', None)
        if category:
            sub_categories = Category.objects.get_for_model(Job, category)[1]
        subcat_length = len(sub_categories)
        subcat_choices = [('', _('Subcategories (%(l)s)' % {'l' : subcat_length}))]
        for category in sub_categories:
            subcat_choices.append((category.pk, category.name))

        self.fields['categories'].choices = cat_choices
        self.fields['subcategories'].choices = subcat_choices
