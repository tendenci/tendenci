from django import forms
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

class BaseFieldFormSet(BaseInlineFormSet):
    def clean(self):
        """
        Checks that a subscribe special function has a email field with it.
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        is_grp_sub = False
        has_email = False
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if form.cleaned_data.get("field_function") == "GroupSubscription":
                is_grp_sub = True
            elif form.cleaned_data.get("field_type") == "EmailField":
                has_email = True

        if is_grp_sub and not has_email:
            raise forms.ValidationError(_("Group Subscription Fields require an Email Field to be present."))
