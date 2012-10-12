from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

from tendenci.apps.user_groups.models import Group
from tendenci.addons.photos.models import Image, PhotoSet, License
from tendenci.core.perms.forms import TendenciBaseForm

class LicenseField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.id == 1:
            return obj.name
        return mark_safe("%s -- <a href='%s'>see details</a>" % (obj.name, obj.deed))

class PhotoAdminForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    class Meta:
        model = Image
        fields = (
            'image',
            'title',
            'caption',
            'tags',
            'allow_anonymous_view',
            #'syndicate',
            'status',
            'status_detail',
            'license',
        )
        fieldsets = [('Photo Set Information', {
            'fields': ['title',
                       'description',
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

class PhotoUploadForm(TendenciBaseForm):
    
    class Meta:
        model = Image
        exclude = ('member', 'photoset', 'title_slug', 'effect', 'crop_from', 'group')

    def __init__(self, *args, **kwargs):
        super(PhotoUploadForm, self).__init__(*args, **kwargs)


class PhotoEditForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), 
                ('pending','Pending'),))
    license = LicenseField(queryset=License.objects.all(),
                widget = forms.RadioSelect(), empty_label=None)
    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=False)
    class Meta:
        model = Image

        fields = (
            'title',
            'caption',
            'license',
            'tags',
            'group',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status',
            'status_detail'
        )

        fieldsets = [
                ('Photo Information', {
                      'fields': [
                          'title',
                          'caption',
                          'tags',
                          'group',
                          'license',
                      ], 'legend': '',
                  }),
                ('Permissions', {
                      'fields': [
                          'allow_anonymous_view',
                          'user_perms',
                          'member_perms',
                          'group_perms',
                      ], 'classes': ['permissions'],
                  }),

                ('Administrator Only', {
                      'fields': [
                          'syndicate',
                          'status',
                          'status_detail',
                      ], 'classes': ['admin-only'],
                  }),
        ]


    safetylevel = forms.HiddenInput()
        
    def __init__(self, *args, **kwargs):
        super(PhotoEditForm, self).__init__(*args, **kwargs)

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
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [('Photo Set Information', {
                      'fields': ['name',
                                 'description',
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

    def __init__(self, *args, **kwargs):
        super(PhotoSetAddForm, self).__init__(*args, **kwargs)
        
        if not self.user.profile.is_superuser:
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

#        if self.user.profile.is_superuser:
#            self.fields['status'] = forms.BooleanField(required=False)
#            self.fields['status_detail'] = forms.ChoiceField(
#                choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

class PhotoSetEditForm(TendenciBaseForm):
    """ Photo-Set Edit-Form """

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    class Meta:
        model = PhotoSet
        fields = (
            'name',
            'description',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [('Photo Set Information', {
                      'fields': ['name',
                                 'description',
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
        
    def __init__(self, *args, **kwargs):
        super(PhotoSetEditForm, self).__init__(*args, **kwargs)

        if not self.user.profile.is_superuser:
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
