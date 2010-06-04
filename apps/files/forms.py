from django import forms

from files.models import File
from perms.forms import AuditingBaseForm

class FileForm(AuditingBaseForm):
    class Meta:
        model = File
        fields = (
        'file',
        )