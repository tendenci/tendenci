from django import forms

from quotes.models import Quote
from perms.forms import TendenciBaseForm

class QuoteForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    
    class Meta:
        model = Quote