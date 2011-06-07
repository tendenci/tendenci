from django import forms
from before_and_after.models import BeforeAndAfter, Category, Subcategory

class BnAForm(forms.ModelForm):
    class Meta:
        model = BeforeAndAfter

class SearchForm(forms.Form):
    category = forms.ModelChoiceField(
                        queryset=Category.objects.all(),
                        required=False,
                    )
    subcategory = forms.ModelChoiceField(
                        queryset=Subcategory.objects.all(),
                        required=False,
                    )
    q = forms.CharField(required=False)
