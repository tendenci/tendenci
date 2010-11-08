from django import forms
from perms.forms import TendenciBaseForm
from models import MembershipType, MembershipApplication, MembershipApplicationPage, \
MembershipApplicationSection, MembershipApplicationField

class MembershipTypeForm(TendenciBaseForm):
    class Meta:
        model = MembershipType

class MembershipApplicationForm(TendenciBaseForm):
    class Meta:
        model = MembershipApplication

class MembershipApplicationPageForm(forms.ModelForm):
    class Meta:
        model = MembershipApplicationPage

class MembershipApplicationSectionForm(forms.ModelForm):
    class Meta:
        model = MembershipApplicationSection

class MembershipApplicationFieldForm(forms.ModelForm):
    class Meta:
        model = MembershipApplicationField