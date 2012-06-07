from django import forms
from django.utils.translation import ugettext_lazy as _
from perms.forms import TendenciBaseForm
from lots.models import Lot, Map, Line


class MapForm(TendenciBaseForm):
    name = forms.CharField()
    status_detail = forms.ChoiceField(choices=(('active', 'Active'), ('pending', 'Pending')))

    class Meta:
        model = Map
        fields = (
            'name',
            'file',
            'description',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [('Map Information', {
                      'fields': ['name',
                                 'file',
                                 'description',
                                 ],
                      'legend': ''
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
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(MapForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Image")


class LotForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('active', 'Active'), ('pending', 'Pending')))

    class Meta:
        model = Lot
        fields = (
            'map',
            'name',
            'suite_number',
            'link',
            'description',
            'contact_info',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )
        widgets = {
          'map': forms.HiddenInput
        }

        fieldsets = [('Map Information', {
                      'fields': ['map',
                                 'name',
                                 'suite_number',
                                 'link',
                                 'description',
                                 'contact_info',
                                 'tags',
                                 ],
                      'legend': ''
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
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]


class LineForm(forms.ModelForm):
    class Meta:
        model = Line
        exclude = ('lot',)
