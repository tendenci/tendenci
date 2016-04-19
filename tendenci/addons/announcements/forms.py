from django import forms
from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.addons.announcements.models import EmergencyAnnouncement
from tendenci.core.perms.forms import TendenciBaseForm


class EmergencyAnnouncementAdminForm(TendenciBaseForm):

    content = forms.CharField(
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': EmergencyAnnouncement._meta.app_label,
        'storme_model': EmergencyAnnouncement._meta.module_name.lower()}))

    class Meta:
        model = EmergencyAnnouncement
        fields = ('title', 'content', 'enabled', 'allow_anonymous_view',
                  'user_perms', 'member_perms', 'group_perms')

    def __init__(self, *args, **kwargs):
        super(EmergencyAnnouncementAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0

