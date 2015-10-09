from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.utils import ErrorList

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.discounts.models import Discount
from tendenci.apps.base.fields import SplitDateTimeField, PriceField
from tendenci.apps.discounts.utils import assign_discount

END_DT_INITIAL = datetime.now() + timedelta(weeks=4)

class DiscountForm(TendenciBaseForm):

    value = PriceField(label=_('Discount Value'), max_digits=10, decimal_places=2,
                       help_text=_('Enter discount value as a positive number.'))

    class Meta:
        model = Discount
        fields = (
            'discount_code',
            'value',
            'start_dt',
            'end_dt',
            'never_expires',
            'cap',
            'apps',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status_detail',
            )

        fieldsets = [(_('Discount Information'), {
                      'fields': ['discount_code',
                                 'value',
                                 'cap',
                                 'never_expires',
                                 'apps',
                                 'start_dt',
                                 'end_dt',
                                 ],
                      'legend': ''
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
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })
                    ]

    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=END_DT_INITIAL)
    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    def __init__(self, *args, **kwargs):
        super(DiscountForm, self).__init__(*args, **kwargs)
        if self.user and not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        MODELS_WITH_DISCOUNT = ['registrationconfiguration',
                                'membershipset']
        content_types = ContentType.objects.filter(model__in=MODELS_WITH_DISCOUNT)
        if 'apps' in self.fields.keys():
            self.fields['apps'].choices = ((c.id, c.app_label) for c in content_types)

    def clean_discount_code(self):
        data = self.cleaned_data['discount_code']
        try:
            discount = Discount.objects.get(discount_code=data)
        except Discount.DoesNotExist:
            return data
        if not discount == self.instance:
            raise forms.ValidationError(_('There a discount for this code already exists.'))
        return data

    def clean(self):
        cleaned_data = self.cleaned_data
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")

        if start_dt > end_dt:
            errors = self._errors.setdefault("end_dt", ErrorList())
            errors.append(_(u"This cannot be earlier than the start date."))

        # Always return the full collection of cleaned data.
        return cleaned_data

class DiscountCodeForm(forms.Form):
    price = forms.DecimalField(decimal_places=2)
    code = forms.CharField()
    model = forms.CharField()
    count = forms.IntegerField()

    def clean(self):
        code = self.cleaned_data.get('code', '')
        count = self.cleaned_data.get('count', 1)
        model = self.cleaned_data.get('model', '')

        try:
            discount = Discount.objects.get(discount_code=code, apps__model=model)
        except Discount.DoesNotExist:
            raise forms.ValidationError(_('This is not a valid discount code.'))
        if not discount.available_for(count):
            raise forms.ValidationError(_('This is not a valid discount code.'))
        return self.cleaned_data

    def new_price(self):
        code = self.cleaned_data['code']
        price = self.cleaned_data['price']
        count = self.cleaned_data['count']
        discount = Discount.objects.get(discount_code=code).value * Decimal(count)
        new_price = price - discount
        if new_price < 0:
            new_price = Decimal('0.00')
        return (new_price, discount)


class DiscountHandlingForm(forms.Form):
    """
    Process a list of prices, and returns a list of discounted prices.
    """
    prices = forms.CharField()
    code = forms.CharField()
    model = forms.CharField()

    def clean(self):
        code = self.cleaned_data.get('code', '')
        model = self.cleaned_data.get('model', '')
        [self.discount] = Discount.objects.filter(discount_code=code, apps__model=model)[:1] or [None]
        if not self.discount:
            raise forms.ValidationError(_('This is not a valid discount code.'))

        if not self.discount.never_expires:
            now = datetime.now()
            if self.discount.start_dt > now:
                raise forms.ValidationError(_('This discount code is not in effect yet.'))
            if self.discount.end_dt <= now:
                raise forms.ValidationError(_('This discount code has expired.'))

        self.limit = 0
        if self.discount.cap != 0:
            self.limit = self.discount.cap - self.discount.num_of_uses()
            if self.limit <= 0:
                raise forms.ValidationError(_('This discount code has passed the limit.'))

        return self.cleaned_data

    def get_discounted_prices(self):
        prices = self.cleaned_data['prices']
        price_list = [Decimal(price) for price in prices.split(';')]

        return assign_discount(price_list, self.discount)
