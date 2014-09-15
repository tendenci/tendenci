from tendenci.apps.industries.models import Industry
from tendenci.apps.perms.forms import TendenciBaseForm
from django import forms
from django.utils.translation import ugettext_lazy as _

class IndustryForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')),
                 ('inactive', _('Inactive')),
                 ('pending', _('Pending')),))

    class Meta:
        model = Industry
        fields = (
        'industry_name',
        'industry_code',
        'description',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status_detail',
        )

        fieldsets = [(_('Industry Information'), {
                      'fields': ['industry_name',
                                 'industry_code',
                                 'description',
                                 ],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

#    def __init__(self, *args, **kwargs):
#        super(IndustryForm, self).__init__(*args, **kwargs)
#
#        if not self.user.profile.is_superuser:
#            if 'status_detail' in self.fields:
#                self.fields.pop('status_detail')
