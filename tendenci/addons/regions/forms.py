from tendenci.addons.regions.models import Region
from tendenci.core.perms.forms import TendenciBaseForm
from django import forms


class RegionForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'),
                 ('inactive', 'Inactive'),
                 ('pending', 'Pending'),))

    class Meta:
        model = Region
        fields = (
        'region_name',
        'region_code',
        'description',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status_detail',
        )

        fieldsets = [('Region Information', {
                      'fields': ['region_name',
                                 'region_code',
                                 'description',
                                 ],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

#    def __init__(self, *args, **kwargs):
#        super(IndustryForm, self).__init__(*args, **kwargs)
#
#        if not self.user.profile.is_superuser:
#            if 'status_detail' in self.fields:
#                self.fields.pop('status_detail')
