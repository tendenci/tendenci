from decimal import Decimal

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.events.registration.utils import can_use_pricing

class RegistrantBaseFormSet(BaseFormSet):
    """
    Extending the BaseFormSet to be able to add extra_params.
    note that extra_params does not consider conflicts in a single form's kwargs.
    """

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, **kwargs):
        self.event = kwargs.pop('event')
        self.extra_params = kwargs.pop('extra_params', {})
        super(RegistrantBaseFormSet, self).__init__(data, files, auto_id, prefix,
                 initial, error_class)

        # initialize internal variables
        self.pricings = {}
        self.enabled_pricings = []
        self.sets = []
        self.total_price = Decimal('0.00')

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {
            'auto_id': self.auto_id,
            'prefix': self.add_prefix(i),
            'form_index': i,
        }

        for key in self.extra_params:
            defaults[key] = self.extra_params[key]

        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass

        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)

        return form

    def set_pricing_groups(self):
        """
        Organize the forms based on pricings used
        """
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            pricing = form.saved_data['pricing']
            if pricing in self.pricings:
                self.pricings[pricing].append(form)
            else:
                self.pricings[pricing] = [form,]

    def set_sets(self):
        """
        Group each form to their corresponding set
        """
        for pricing in self.pricings:
            for i in range(0, len(self.pricings[pricing])):
                form = self.pricings[pricing][i]
                if i % pricing.quantity == 0:
                    # initialize a new set with this form
                    new_set = [form] # we're assured this is always initialized.
                    self.sets.append(new_set)
                else:
                    new_set.append(form)

        # sort the sets based on first form label
        self.sets = sorted(self.sets, key=lambda s: s[0].get_form_label())

    def get_sets(self):
        if not self.sets:
            self.set_sets()
        return self.sets

    def get_total_price(self):
        return self.total_price

    def get_user_list(self):
        """returns a list of user registrants"""
        users = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            user = form.get_user()
            if not user.is_anonymous:
                users.append(user)
        return users

    def clean(self):
        """
        Validate the set of registrants for all the pricings used.
        """

        if self.total_form_count()<1:
            raise forms.ValidationError(_('You must register at least 1 registrant per registration'))

        # organize pricing dict
        self.set_pricing_groups()

        # validate the reg quantity for each pricing
        for pricing in self.pricings:
            # the registrant length must be divisible by the pricing's quantity
            if len(self.pricings[pricing]) % pricing.quantity != 0:
                raise forms.ValidationError(_("Please enter a valid number of registrants."))

        errors = []
        users = []

        # mark all validated prices is shared pricing
        shared_pricing = get_setting('module', 'events', 'sharedpricing')
        if shared_pricing:
            for pricing in self.pricings:
                for i in range(0, len(self.pricings[pricing])):
                    form = self.pricings[pricing][i]
                    if i % pricing.quantity == 0:
                        user = form.get_user()
                        if can_use_pricing(self.event, user, pricing):
                            self.enabled_pricings.append(pricing)

        # if all quantities are valid, update each form's corresponding price
        for pricing in self.pricings:
            for i in range(0, len(self.pricings[pricing])):
                form = self.pricings[pricing][i]
                if i % pricing.quantity == 0:
                    price = pricing.price

                    # first form of each set must be authorized for the pricing
                    user = form.get_user()
                    # take note of each invalid price but continue setting prices

                    if shared_pricing:
                        if pricing not in self.enabled_pricings:
                            errors.append(forms.ValidationError(_("%(user)s is not authorized to use %(pricing)s" % {'user': user, 'pricing': pricing})))
                    else:
                        if not can_use_pricing(self.event, user, pricing):
                            errors.append(forms.ValidationError(_("%(user)s is not authorized to use %(pricing)s" % {'user': user, 'pricing': pricing})))

                    if not user.is_anonymous:
                        # check if this user has already been used before
                        if user.pk in users:
                            errors.append(forms.ValidationError(_("%s can only be registered once per registration" % user)))
                        else:
                            # mark this pricing pair used
                            users.append(user.pk)
                else:
                    price = Decimal('0.00')

                # associate the price with the form
                form.set_price(price)

                # update the total price
                self.total_price += price

        # raise any errors found
        for error in errors:
            raise error
