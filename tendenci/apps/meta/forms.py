from django import forms
from tendenci.apps.meta.models import Meta as MetaTag
from tendenci.apps.base.forms import FormControlWidgetMixin

class MetaForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = MetaTag
        fields = (
            'title',
            'keywords',
            'description',
            'canonical_url',
        )
