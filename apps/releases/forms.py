from django.forms import ModelForm
from releases.models import Release

class ReleaseForm(ModelForm):
    class Meta:
        model = Release
        exclude = ('guid',)
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
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',

        'syndicate',
        'owner',
        'status',
        'status_detail',
        )
