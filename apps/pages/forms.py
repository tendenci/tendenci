from pages.models import Page
from perms.forms import TendenciBaseForm
from django import forms
from tinymce.widgets import TinyMCE

class PageForm(TendenciBaseForm):
    STATUS_CHOICES = (('active','Active'),('inactive','Inactive'), ('pending','Pending'),)

    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Page._meta.app_label, 
        'storme_model':Page._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)
        
    class Meta:
        model = Page
        fields = (
        'title',
        'slug',
        'content',
        'tags',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',
        'syndicate',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(PageForm, self).__init__(user, *args, **kwargs)
        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0