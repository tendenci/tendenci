from django import forms


class PayPalPaymentForm(forms.Form):
    # the _ext-enter is no longer required.
    cmd = forms.CharField(max_length=10,
                            widget=forms.HiddenInput,
                            initial='_ext-enter')
    redirect_cmd = forms.CharField(max_length=10,
                            widget=forms.HiddenInput,
                            initial='_xclick')
    business = forms.CharField(max_length=50, widget=forms.HiddenInput)
    image_url = forms.CharField(max_length=100, widget=forms.HiddenInput)
    display = forms.CharField(max_length=1,
                              widget=forms.HiddenInput,
                              initial='0')
    # do not prompt buyers to include a note with their payments.
    no_note = forms.CharField(max_length=1,
                              widget=forms.HiddenInput,
                              initial='1')
    # do not prompt buyers for a shipping address.
    no_shipping = forms.CharField(max_length=1,
                              widget=forms.HiddenInput,
                              initial='1')
    # link to thankyou page. add it later because we cannot add it here.
#    return = forms.CharField(max_length=100,
#                            widget=forms.HiddenInput)
    # form method used by thankyou page (2=POST)
    rm = forms.CharField(max_length=1,
                              widget=forms.HiddenInput,
                              initial='2')
    # indicates the use of third-party shopping cart
    upload = forms.CharField(max_length=1,
                              widget=forms.HiddenInput,
                              initial='0')
    paymentaction = forms.CharField(max_length=10,
                              widget=forms.HiddenInput,
                              initial='sale')
    # link to ipn
    notify_url = forms.CharField(max_length=100,
                                 widget=forms.HiddenInput)
    amount = forms.DecimalField(max_digits=15,
                                decimal_places=2,
                                widget=forms.HiddenInput)
    currency_code = forms.CharField(max_length=25,
                                    widget=forms.HiddenInput)
    charset = forms.CharField(max_length=10,
                              widget=forms.HiddenInput,
                              initial='utf-8')
    # pass through variable
    invoice = forms.IntegerField(widget=forms.HiddenInput)
    item_name = forms.CharField(max_length=1600, widget=forms.HiddenInput)

    first_name = forms.CharField(max_length=100, widget=forms.HiddenInput)
    last_name = forms.CharField(max_length=100, widget=forms.HiddenInput)
    email = forms.CharField(max_length=255, widget=forms.HiddenInput)
    address1 = forms.CharField(max_length=100, widget=forms.HiddenInput)
    address2 = forms.CharField(max_length=100, widget=forms.HiddenInput)
    city = forms.CharField(max_length=40, widget=forms.HiddenInput)
    state = forms.CharField(max_length=40, widget=forms.HiddenInput)
    zip = forms.CharField(max_length=7, widget=forms.HiddenInput)
    country = forms.CharField(max_length=20, widget=forms.HiddenInput)
    night_phone_a = forms.CharField(max_length=25, widget=forms.HiddenInput)
