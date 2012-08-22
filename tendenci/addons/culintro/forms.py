from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from locations.models import Location
from categories.models import Category, CategoryItem
from jobs.models import JobPricing
from jobs.utils import get_payment_method_choices, pricing_choices
from culintro.models import CulintroJob
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

STATUS_DETAIL_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('pending', 'Pending'),
    ('paid - pending approval', 'Paid - Pending Approval'),
)

class CulintroJobForm(TendenciBaseForm):
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': CulintroJob._meta.app_label,
        'storme_model': CulintroJob._meta.module_name.lower()}))

    activation_dt = SplitDateTimeField(label=_('Activation Date/Time'),
        initial=datetime.now())
    post_dt = SplitDateTimeField(label=_('Post Date/Time'),
        initial=datetime.now())
    expiration_dt = SplitDateTimeField(label=_('Expiration Date/Time'),
        initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending'),))

    list_type = forms.ChoiceField(initial='regular', choices=(('regular', 'Regular'),
                                                              ('premium', 'Premium'),))
    payment_method = forms.CharField(error_messages={'required': 'Please select a payment method.'})
    pricing = forms.ModelChoiceField(label=_('Requested Duration'), 
                    queryset=JobPricing.objects.filter(status=1).order_by('duration'))
	
    class Meta:
        model = CulintroJob
        fields = (
        'title',
        'slug',
        'description',
        'location_2',
        'location_other',
        'list_type',
        'pricing',
        'tags',
        'activation_dt',
        'post_dt',
        'expiration_dt',
        'contact_name',
        'contact_email',
        'contact_phone',
        'open_call',
        'promote_posting',
        'payment_method',
        )
        
        fieldsets = [('Job Information', {
                      'fields': ['title',
                                'slug',
                                'description',
                                'location_2',
                                'location_other',
                                'tags',
                                'pricing',
                                'activation_dt',
                                'expiration_dt',
                                'post_dt',
                                'contact_name',
                                'contact_email',
                                'contact_phone',
                                'open_call',
                                'promote_posting',
                                 ],
                      'legend': ''
                      }),
                      ('Payment', {
                      'fields': ['list_type',
                                 'payment_method'
                                 ],
                        'classes': ['payment_method'],
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
                      'fields': ['syndicate',
                                 'status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(CulintroJobForm, self).__init__(*args, **kwargs)

        if self.user:
            if 'payment_method' in self.fields:
                self.fields['payment_method'].widget = forms.RadioSelect(choices=get_payment_method_choices(self.user))

        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if self.user.profile.is_superuser:
                self.fields['status_detail'].choices = STATUS_DETAIL_CHOICES
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0


class CulintroSearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    open_call = forms.BooleanField(required=False, )
    location = forms.ModelMultipleChoiceField(queryset=Location.objects.all(), required=False, )
    categories = forms.MultipleChoiceField(required=False, )
    
    def __init__(self, *args, **kwargs):
        super(CulintroSearchForm, self).__init__(*args, **kwargs)
        self.fields['location'].widget.attrs['data-placeholder'] = 'Start typing a city'
        
        # Setup categories
        """
            choices = [
                ['category-label0',[
                        ('category-pk0:sub_category-pk0', 'sub_category-label0'),
                        ('category-pk0:sub_category-pk1', 'sub_category-label1')
                    ]
                ],
                ['category-label1',[
                        ('category-pk1:sub_category-pk2', 'sub_category-label2'),
                        ('category-pk1:sub_category-pk3', 'sub_category-label3')
                    ]
                ],
            ]
        """
        choices = []
        (categories, sub_categories) = Category.objects.get_for_model(CulintroJob)
        for category in categories:
            # Get sub_categories associated with category
            subs = Category.objects.get_for_model(CulintroJob, category)[1]
            sub_list = []
            for sub in subs:
                sub_list.append(
                    (str(category.pk) + ':' + str(sub.pk), sub.name)
                )
            choices.append((category.name, sub_list))
			
        self.fields['categories'].widget.attrs['data-placeholder'] = 'Pick a job position'
        self.fields['categories'].choices = choices
        
    def clean_categories(self):
        data = self.cleaned_data.get('categories')
        categories = []
        for cat in data:
            (cat_pk, sub_cat_pk) = cat.split(':')
            category = Category.objects.get(pk=cat_pk)
            sub_category = Category.objects.get(pk=sub_cat_pk)
            categories.append((category, sub_category))
        return categories
