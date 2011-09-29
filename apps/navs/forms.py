from django import forms
from django.utils.translation import ugettext_lazy as _

from perms.forms import TendenciBaseForm
from perms.utils import is_admin

from navs.models import Nav, NavItem

class NavForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    class Meta:
        model = Nav
        fields = (
            'title',
            'description',
            'megamenu',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status',
            'status_detail',
            )

        fieldsets = [('Nav Information', {
                      'fields': ['title',
                                 'description',
                                 'megamenu',
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
                    })
                    ]
