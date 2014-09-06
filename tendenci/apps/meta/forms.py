from django import forms
from tendenci.apps.meta.models import Meta as MetaTag

class MetaForm(forms.ModelForm):
    class Meta:
        model = MetaTag
        fields = (
            'title',
            'keywords',
            'description',
            'canonical_url',
        )