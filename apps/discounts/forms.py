from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django import forms
from perms.forms import TendenciBaseForm
from perms.utils import is_admin
from discounts.models import Discount
from base.fields import SplitDateTimeField

class DiscountForm(TendenciBaseForm):
    class Meta:
        model = Discount
        fields = (
            'discount_code',
            'value',
            'start_dt',
            'end_dt',
            'never_expires',
            'cap',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status',
            'status_detail',
            )

        fieldsets = [('Discount Information', {
                      'fields': ['discount_code',
                                 'start_dt',
                                 'end_dt',
                                 'value',
                                 'cap',
                                 'never_expires',
                                 ],
                      'legend': ''
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
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })
                    ]
        
    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=datetime.now())
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
        
    def __init__(self, *args, **kwargs):
        super(DiscountForm, self).__init__(*args, **kwargs)
        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
            
    def clean_discount_code(self):
        data = self.cleaned_data['discount_code']
        try:
            Discount.objects.get(discount_code=data)
        except Discount.DoesNotExist:
            return data
        raise forms.ValidationError('There a discount for this code already exists.')

    def clean(self):
        cleaned_data = self.cleaned_data
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")

        if start_dt > end_dt:
            errors = self._errors.setdefault("end_dt", ErrorList())
            errors.append(u"This cannot be \
                earlier than the start date.")

        # Always return the full collection of cleaned data.
        return cleaned_data
