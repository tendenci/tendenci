from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from directories.models import Directory
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class DirectoryForm(TendenciBaseForm):
    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Directory._meta.app_label, 
        'storme_model':Directory._meta.module_name.lower()}))

    #activation_dt = SplitDateTimeField(label=_('Activation Date/Time'),
    #    initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    class Meta:
        model = Directory
        fields = (
            'headline',
            'slug',
            'summary',
            'body',
            'source',
            'logo',
            'timezone',
            'first_name',
            'last_name',
            'address',
            'address2',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'phone2',
            'fax',
            'email',
            'email2',
            'website',
            'tags',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_user_edit',
            'syndicate',
            'status',
            'status_detail',
        )


    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(DirectoryForm, self).__init__(user, *args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

        if not is_admin(user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

