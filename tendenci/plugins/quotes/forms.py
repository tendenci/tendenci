from django import forms

from quotes.models import Quote
from perms.forms import TendenciBaseForm

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