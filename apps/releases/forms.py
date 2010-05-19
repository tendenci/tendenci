from django import forms
from releases.models import Release

class ReleaseForm(forms.ModelForm):
    class Meta:
        model = Release
        fields = (
        'headline',
        'summary',
        'body',
        'source',
        'website',
        'release_dt',
        'timezone',
        'first_name',
        'last_name',
        'phone',
        'fax',
        'email',
        
        'enclosure_url',

        'allow_anonymous_view',
        'allow_user_view',
        'allow_user_edit',

        'syndicate',
        'status',
        'status_detail',
        )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(ReleaseForm, self).__init__(*args, **kwargs)

class ReleaseEditForm(forms.ModelForm):
    class Meta:
        model = Release
        fields = (
        'headline',
        'summary',
        'body',
        'source',
        'website',
        'release_dt',
        'timezone',
        'first_name',
        'last_name',
        'phone',
        'fax',
        'email',

        'enclosure_url',

        'allow_anonymous_view',
        'allow_user_view',
        'allow_user_edit',

        'syndicate',
        'owner',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(ReleaseEditForm, self).__init__(*args, **kwargs)