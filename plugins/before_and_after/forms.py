from django import forms
from before_and_after.models import BeforeAndAfter, PhotoSet

class BnAForm(forms.ModelForm):
    class Meta:
        model = BeforeAndAfter
        
        fields = (
            'title',
            'category',
            'subcategory',
            'description',
            'tags',
            'admin_notes',
        )
