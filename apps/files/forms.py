from django import forms
from files.models import File
from perms.forms import TendenciBaseForm

class FileForm(TendenciBaseForm):
    class Meta:
        model = File

        fields = (
            'file',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
        )

        fieldsets = [('', {
                      'fields': ['file'],
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
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None
        super(FileForm, self).__init__(*args, **kwargs)