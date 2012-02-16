from django import forms
from profiles.models import Profile

class ProfileForm(forms.ModelForm):
    """Profile Form
    """
    class Meta:
        model = Profile
        fields = (
            'salutation',
            'user',
            'phone',
            'phone2',
            'fax',
            'work_phone',
            'home_phone',
            'mobile_phone',
            'email',
            'email2',
            'company',
            'position_title',
            'position_assignment',
            'display_name',
            'hide_in_search',
            'hide_phone',
            'hide_email',
            'hide_address',
            'initials',
            'sex',
            'mailing_name',
            'address',
            'address2',
            'city',
            'state',
            'zipcode',
            'county',
            'country',
            'url',
            'dob',
            'ssn',
            'spouse',
            'time_zone',
            'department',
            'education',
            'student',
            'direct_mail',
            'notes',
            'allow_anonymous_view',
            'admin_notes',
            'entity',
            'status',
            'status_detail',
        )
    
