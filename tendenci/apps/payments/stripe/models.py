from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.models import TendenciBaseModel


class StripeAccount(TendenciBaseModel):
    """
    A Stripe connected account
    """
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="stripe_accounts")
    account_name = models.CharField(max_length=250, default='')
    email = models.CharField(max_length=200, default='')
    default_currency = models.CharField(max_length=5, default='usd')
    country = models.CharField(max_length=5, default='US')
    stripe_user_id = models.CharField(_(u'Stripe user id'), max_length=200, unique=True)
    
    scope = models.CharField(max_length=20)
#     token_type = models.CharField(max_length=20)
#     refresh_token = models.CharField(max_length=200)
#     livemode_access_token = models.CharField(max_length=200)
#     testmode_access_token = models.CharField(max_length=200)
#     livemode_stripe_publishable_key = models.CharField(max_length=200)
#     testmode_stripe_publishable_key = models.CharField(max_length=200)

    def __str__(self):
        return self.account_name


class Charge(models.Model):
    account = models.ForeignKey(StripeAccount, related_name="stripe_charges", on_delete=models.CASCADE)
    charge_id = models.CharField(max_length=100, default='')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount_refunded = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=5, default='usd')
    captured = models.BooleanField(default=False)
    livemode = models.BooleanField(default=False)
    charge_dt = models.DateTimeField(_("Charged On"))
    create_dt = models.DateTimeField(_("Created On"), auto_now_add=True)
    update_dt = models.DateTimeField(_("Last Updated"), auto_now=True)
