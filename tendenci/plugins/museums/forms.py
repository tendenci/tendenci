from django import forms
from django.utils.translation import ugettext_lazy as _

from museums.models import Museum, Photo
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from tendenci.core.base.fields import SplitDateTimeField

class MuseumForm(TendenciBaseForm):
    class Meta:
        model = Museum
        fields = (
            'name',
            'slug',
            'phone',
            'address',
            'city',
            'state',
            'zip',
            'website',
            'building_photo',
            'about'
            'hours',
            'free_times',
            'parking_information',
            'free_parking',
            'street_parking',
            'paid_parking',
            'dining_information',
            'restaurant',
            'snacks',
            'shopping_information',
            'events',
            'special_offers',
            'facebook',
            'twitter',
            'flickr',
            'youtube',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status',
            'status_detail',
        )
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    about = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Museum._meta.app_label, 
        'storme_model':Museum._meta.module_name.lower()}))

    def __init__(self, *args, **kwargs):
        super(MuseumForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['about'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['about'].widget.mce_attrs['app_instance_id'] = 0

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['file']
        
    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Photo")
