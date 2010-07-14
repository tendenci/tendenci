from django import forms
from django.utils.translation import ugettext_lazy as _

from photos.models import Image, PhotoSet
from perms.utils import is_admin
from perms.forms import TendenciBaseForm

class PhotoUploadForm(TendenciBaseForm):
    
    class Meta:
        model = Image
        exclude = ('member', 'photoset', 'title_slug', 'effect', 'crop_from')
        
    def clean_image(self):
        if '#' in self.cleaned_data['image'].name:
            raise forms.ValidationError(
                _("Image filename contains an invalid character: '#'. Please remove the character and try again."))
        return self.cleaned_data['image']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PhotoUploadForm, self).__init__(user, *args, **kwargs)

class PhotoEditForm(TendenciBaseForm):
    
    class Meta:
        model = Image
        exclude = ('member', 'title_slug', 'effect', 'crop_from', 'image',)

    safetylevel = forms.HiddenInput()
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PhotoEditForm, self).__init__(user, *args, **kwargs)

class PhotoSetAddForm(TendenciBaseForm):
    """ Photo-Set Add-Form """

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    class Meta:
        model = PhotoSet
        fields = (
            'name',
            'description',
            'tags',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_user_edit',
            'status',
            'status_detail',
        )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PhotoSetAddForm, self).__init__(user, *args, **kwargs)

        if is_admin(user):
            self.fields['status'] = forms.BooleanField(required=False)
            self.fields['status_detail'] = forms.ChoiceField(
                choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

class PhotoSetEditForm(TendenciBaseForm):
    """ Photo-Set Edit-Form """

    class Meta:
        model = PhotoSet
        fields = (
            'name',
            'description',
            'tags',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_user_edit',
            'status',
            'status_detail',
        )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PhotoSetEditForm, self).__init__(user, *args, **kwargs)

        if not is_admin(user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
