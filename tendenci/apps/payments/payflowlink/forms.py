from django import forms
from django.conf import settings

class PayflowLinkPaymentForm(forms.Form):
    # required fields: login, partner, amount, type

    login = forms.CharField(max_length=20, required=True,
                            widget=forms.HiddenInput,
                            initial=settings.PAYPAL_MERCHANT_LOGIN)
    partner = forms.CharField(max_length=20, widget=forms.HiddenInput)
    amount = forms.DecimalField(max_digits=15, decimal_places=2, widget=forms.HiddenInput)
    type = forms.CharField(max_length=4, widget=forms.HiddenInput)
    showconfirm = forms.IntegerField(widget=forms.HiddenInput, initial=1)
    disablereceipt = forms.IntegerField(widget=forms.HiddenInput, initial=0)
    custid = forms.IntegerField(widget=forms.HiddenInput)

    name = forms.CharField(max_length=100, widget=forms.HiddenInput)
    email = forms.CharField(max_length=255, widget=forms.HiddenInput)
    address = forms.CharField(max_length=100, widget=forms.HiddenInput)
    city = forms.CharField(max_length=40, widget=forms.HiddenInput)
    state = forms.CharField(max_length=40, widget=forms.HiddenInput)
    zip = forms.CharField(max_length=7, widget=forms.HiddenInput)
    country = forms.CharField(max_length=20, widget=forms.HiddenInput)
    fax = forms.CharField(max_length=25, widget=forms.HiddenInput)
    phone = forms.CharField(max_length=25, widget=forms.HiddenInput)

    nametoship = forms.CharField(max_length=100, widget=forms.HiddenInput)
    addresstoship = forms.CharField(max_length=100, widget=forms.HiddenInput)
    citytoship = forms.CharField(max_length=40, widget=forms.HiddenInput)
    statetoship = forms.CharField(max_length=40, widget=forms.HiddenInput)
    ziptoship = forms.CharField(max_length=7, widget=forms.HiddenInput)
    countrytoship = forms.CharField(max_length=20, widget=forms.HiddenInput)

    comment1 = forms.CharField(max_length=1600, widget=forms.HiddenInput)
    comment2 = forms.CharField(max_length=250, widget=forms.HiddenInput)
