from django import forms

from files.models import File
from perms.forms import AuditingBaseForm

class FileForm(AuditingBaseForm):
    class Meta:
        model = File
        fields = (
        'file',
        )

    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(FileForm, self).__init__(user, *args, **kwargs)