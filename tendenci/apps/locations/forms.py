import imghdr
from os.path import splitext, basename

from tendenci.addons.locations.models import Location
from tendenci.core.perms.forms import TendenciBaseForm
from django import forms
from django.db.models import Q
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from tendenci.core.base.fields import EmailVerificationField, CountrySelectField
from tendenci.core.files.utils import get_max_file_upload_size


ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)


class LocationForm(TendenciBaseForm):

    photo_upload = forms.FileField(label=_('Logo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current logo'), required=False)

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    email = EmailVerificationField(label=_("Email"), required=False)
    country = CountrySelectField(label=_("Country"), required=False)

    class Meta:
        model = Location
        fields = (
        'location_name',
        'slug',
        'description',
        'contact',
        'address',
        'address2',
        'city',
        'state',
        'zipcode',
        'country',
        'phone',
        'fax',
        'email',
        'website',
        'latitude',
        'longitude',
        'photo_upload',
        'hq',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status_detail',
        )

        fieldsets = [(_('Location Information'), {
                      'fields': ['location_name',
                                 'slug',
                                 'description',
                                 'latitude',
                                 'longitude',
                                 'photo_upload',
                                 'hq',
                                 ],
                      'legend': ''
                      }),
                      (_('Contact'), {
                      'fields': ['contact',
                                 'address',
                                 'address2',
                                 'city',
                                 'state',
                                 'zipcode',
                                 'country',
                                 'phone',
                                 'fax',
                                 'email',
                                 'website'
                                 ],
                        'classes': ['contact'],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)

        if self.user:
            if not self.user.profile.is_superuser:
                if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if self.instance.logo:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.logo.pk, basename(self.instance.logo.file.name))
        else:
            self.fields.pop('remove_photo')

    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        if photo_upload:
            extension = splitext(photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The logo must be of jpg, gif, or png image type.'))

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The logo is an invalid image. Try uploading another logo.'))

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(upload_size)s') % {
                                    'max_upload_size': filesizeformat(max_upload_size),
                                    'upload_size': filesizeformat(photo_upload.size)})

        return photo_upload

    def save(self, *args, **kwargs):
        location = super(LocationForm, self).save(*args, **kwargs)

        if self.cleaned_data.get('remove_photo'):
            location.logo = None
        return location


class LocationFilterForm(forms.Form):
    query = forms.CharField(required=False)
    country = forms.ChoiceField(choices=[], required=False)
    state = forms.ChoiceField(choices=[], required=False)
    city = forms.ChoiceField(choices=[], required=False)
    # zipcode = forms.ChoiceField(choices=[], required=False)

    def __init__(self, data={}, *args, **kwargs):
        super(LocationFilterForm, self).__init__(*args, **kwargs)
        # self.update_field_choices('zipcode', data)
        del data['city']
        self.update_field_choices('city', data)
        del data['state']
        self.update_field_choices('state', data)
        self.update_field_choices('country')

    def update_field_choices(self, field_name, data={}):
        choices = Location.objects.exclude(**{'%s' % field_name: ''})
        for key,value in data.iteritems():
            if value:
                choices = choices.filter(**{'%s' % key:value})
        choices = choices.values_list(field_name, field_name).distinct().order_by(field_name)

        if choices.count() > 1:
            self.fields[field_name].choices = choices
            # Adding empty value since we can't add on a ValuesListQuerySet
            self.fields[field_name].choices = [('','----')] + self.fields[field_name].choices
        else:
            del self.fields[field_name]

    def filter_results(self, queryset):
        query = self.cleaned_data.get('query', '')
        country = self.cleaned_data.get('country', '')
        state = self.cleaned_data.get('state', '')
        city = self.cleaned_data.get('city', '')
        # zipcode = self.cleaned_data.get('zipcode', '')

        filter_params = {}
        if country:
            filter_params['country'] = country
        if state:
            filter_params['state'] = state
        if city:
            filter_params['city'] = city
        # if zipcode:
        #     filter_params['zipcode'] = zipcode

        queryset = queryset.filter(**filter_params)

        if query:
            queryset = queryset.filter(Q(location_name__icontains=query)|
                                       Q(contact__icontains=query)|
                                       Q(address__icontains=query)|
                                       Q(phone__icontains=query)|
                                       Q(email__icontains=query))
        return queryset
