from django import forms

from tendenci.apps.quotes.models import Quote
from tendenci.core.perms.forms import TendenciBaseForm

class QuoteForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    
    class Meta:
        model = Quote
        fields = (
            'quote',
            'author',
            'source',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status',
            'status_detail',
        )