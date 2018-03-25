import re

from decimal import Decimal

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser

# from captcha.fields import CaptchaField
#from tendenci.apps.base.forms import SimpleMathField
from tendenci.apps.discounts.models import Discount
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.memberships.models import Membership

from tendenci.apps.events.models import PaymentMethod, Registrant
from tendenci.apps.base.forms import CustomCatpchaField

class RegistrationForm(forms.Form):
    """
    Registration form.
    Focuses on non-registrant specific details.
    """
    amount_for_admin = forms.DecimalField(decimal_places=2, required=False)
    discount = forms.CharField(label=_('Discount Code'), required=False)
    captcha = CustomCatpchaField(label=_('Type the code below'))
    payment_method = forms.ModelChoiceField(empty_label=None, required=True,
        queryset=PaymentMethod.objects.none(), widget=forms.RadioSelect, initial=1)

    def __init__(self, event, user, *args, **kwargs):
        """
        event: instance of Event model
        user: request.user
        reg_count: used for discount validation (discounts have usage limits)
        """
        self.event = event
        self.user = user
        self.reg_count = kwargs.pop('reg_count', 0)

        super(RegistrationForm, self).__init__(*args, **kwargs)

        # no need for captcha if logged in
        if user.is_authenticated:
            self.fields.pop('captcha')

        # admin only price override field
        if not user.profile.is_superuser:
            self.fields.pop('amount_for_admin')

        reg_conf =  event.registration_configuration
        if reg_conf.can_pay_online:
            payment_methods = reg_conf.payment_method.all()
        else:
            payment_methods = reg_conf.payment_method.exclude(
                machine_name='credit card').order_by('pk')
        self.fields['payment_method'].queryset = payment_methods

    def get_user(self):
        return self.user

    def get_event(self):
        return self.event

    def clean_discount(self):
        """
        Returns the discount instance if it exists for a given code.
        Returns none if the code is blank.
        """
        code = self.cleaned_data['discount']
        if code:
            try:
                discount = Discount.objects.get(discount_code=self.cleaned_data['discount'])
                if discount.available_for(self.reg_count):
                    return discount
                else:
                    raise forms.ValidationError(_("Discount Code cannot be used for %s people." % self.reg_count))
            except Discount.objects.DoesNotExist:
                raise forms.ValidationError(_("This is not a valid Discount Code!"))
        return code

class RegistrantForm(forms.Form):
    """
    Each registrant form will have a hidden pricing field.
    Each registrant form will have a hidden reg_set field.
    The reg_set field will be used to group the registrant data and validate
    them as a whole.
    """
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    memberid = forms.CharField(label=_("Member ID"), max_length=50, required=False)
    company_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        self.pricings = kwargs.pop('pricings')
        self.form_index = kwargs.pop('form_index', None)

        super(RegistrantForm, self).__init__(*args, **kwargs)

        # make the fields in the subsequent forms as not required
        if self.form_index and self.form_index > 0:
            for key in self.fields:
                self.fields[key].required = False

        # initialize pricing options and reg_set field
        self.fields['pricing'] = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=self.pricings)

        allow_memberid = get_setting('module', 'events', 'memberidpricing')
        if not allow_memberid:
            self.fields.pop('memberid')

        # initialize internal variables
        self.price = Decimal('0.00')
        self.saved_data = {}

    def set_price(self, price):
        self.price = price

    def get_price(self):
        return self.price

    def get_form_label(self):
        return self.form_index + 1

    def get_user(self):
        """
        Gets the user from memberid or email.
        Return AnonymousUser if both are unavailable.
        """
        user = AnonymousUser()
        memberid = self.saved_data.get('memberid', None)
        email = self.saved_data.get('email', None)

        if memberid:  # memberid takes priority over email
            membership = Membership.objects.first(member_number=memberid)
            if hasattr(membership, 'user'):
                user = membership.user
        elif email:
            users = User.objects.filter(email=email)
            if users:
                user = users[0]

        return user

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        # detect markup
        markup_pattern = re.compile(r'<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError(_("Markup is not allowed in the name field"))

        # detect URL and Email
        pattern_string = r'\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError(_("URL's and Emails are not allowed in the name field"))

        data.strip()
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']

        # detect markup
        markup_pattern = re.compile(r'<[^>]*?>', re.I and re.M)
        markup = markup_pattern.search(data)
        if markup:
            raise forms.ValidationError(_("Markup is not allowed in the name field"))

        # detect URL and Email
        pattern_string = r'\w\.(com|net|org|co|cc|ru|ca|ly|gov)$'
        pattern = re.compile(pattern_string, re.I and re.M)
        domain_extension = pattern.search(data)
        if domain_extension or "://" in data:
            raise forms.ValidationError(_("URL's and Emails are not allowed in the name field"))

        data.strip()
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        data.strip()
        return data

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, forms.FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except forms.ValidationError as e:
                self._errors[name] = self.error_class(e.messages)
                if name in self.cleaned_data:
                    del self.cleaned_data[name]
            # save invalid or valid data into saved_data
            self.saved_data[name] = value

    def clean(self):
        data = self.cleaned_data
        pricing = self.cleaned_data['pricing']
        user = self.get_user()
        if not (user.is_anonymous or pricing.allow_anonymous):
            already_registered = Registrant.objects.filter(user=user)
            if already_registered:
                if not user.profile.is_superuser:
                    raise forms.ValidationError(_('%s is already registered for this event' % user))
        return data
