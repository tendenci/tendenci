from os.path import splitext, basename

from django import forms
from django.contrib.auth.models import User
from django.forms import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.chapters.models import Chapter, Officer
from tendenci.apps.user_groups.models import Group
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.files.validators import FileValidator
from tendenci.apps.base.fields import StateSelectField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.regions.models import Region

class ChapterForm(TendenciBaseForm):
    mission = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Chapter._meta.app_label,
        'storme_model':Chapter._meta.model_name.lower()}))
    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Chapter._meta.app_label,
        'storme_model':Chapter._meta.model_name.lower()}))
    notes = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Chapter._meta.app_label,
        'storme_model':Chapter._meta.model_name.lower()}))
    sponsors = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Chapter._meta.app_label,
        'storme_model':Chapter._meta.model_name.lower()}))
    photo_upload = forms.FileField(label=_('Featured Image'), required=False,
                                   validators=[FileValidator(allowed_extensions=('.jpg', '.jpeg', '.gif', '.png'))],)
    state = StateSelectField(required=False)


    class Meta:
        model = Chapter
        fields = (
        'title',
        'slug',
        'region',
        'state',
        'mission',
        'content',
        'notes',
        'sponsors',
        'photo_upload',
        'contact_name',
        'contact_email',
        'join_link',
        'tags',
        'allow_anonymous_view',
        'syndicate',
        'status_detail',
        )
        fieldsets = [('Chapter Information', {
                      'fields': ['title',
                                 'slug',
                                 'region',
                                 'state',
                                 'mission',
                                 'content',
                                 'notes',
                                 'sponsors',
                                 'photo_upload',
                                 'contact_name',
                                 'contact_email',
                                 'join_link',
                                 'tags'
                                 ],
                      'legend': '',
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
                      'fields': ['syndicate',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))

    def __init__(self, *args, **kwargs):
        super(ChapterForm, self).__init__(*args, **kwargs)
        if self.instance.featured_image:
            self.fields['photo_upload'].help_text = 'Current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.featured_image.pk, basename(self.instance.featured_image.file.name))
        if self.instance.pk:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = 0
            
    def save(self, *args, **kwargs):
        chapter = super(ChapterForm, self).save(*args, **kwargs)
        # save photo
        if 'photo_upload' in self.cleaned_data:
            photo = self.cleaned_data['photo_upload']
            if photo:
                chapter.save(photo=photo)
        return chapter


class ChapterAdminForm(TendenciBaseForm):
    mission = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Chapter._meta.app_label,
        'storme_model':Chapter._meta.model_name.lower()}))
    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Chapter._meta.app_label,
        'storme_model':Chapter._meta.model_name.lower()}))
    notes = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Chapter._meta.app_label,
        'storme_model':Chapter._meta.model_name.lower()}))

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    photo_upload = forms.FileField(label=_('Featured Image'), required=False,
                                   validators=[FileValidator(allowed_extensions=('.jpg', '.jpeg', '.gif', '.png'))],)
    state = StateSelectField(required=False)

    class Meta:
        model = Chapter

        fields = (
        'title',
        'slug',
        'mission',
        'content',
        'notes',
        'photo_upload',
        'contact_name',
        'contact_email',
        'join_link',
        'tags',
        'allow_anonymous_view',
        'syndicate',
        'status_detail',
        )

    def __init__(self, *args, **kwargs):
        super(ChapterAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = 0
        if self.instance.featured_image:
            self.fields['photo_upload'].help_text = 'Current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.featured_image.pk, basename(self.instance.featured_image.file.name))
            self.fields['photo_upload'].required = False


class ChapterAdminChangelistForm(TendenciBaseForm):
    group = forms.ModelChoiceField(required=True, queryset=Group.objects.filter(status=True, status_detail="active").order_by('name'))

    class Meta:
        model = Chapter

        fields = (
        'title',
        'group',
        )


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, u):
        label = ''
        if u.first_name and u.last_name:
            label = u.first_name + ' ' + u.last_name
        elif u.username:
            label = u.username
        elif u.email:
            label = u.email
        if len(label) > 23:
            label = label[0:20] + '...'
        return label


class OfficerBaseFormSet(BaseInlineFormSet):
    def __init__(self,  *args, **kwargs): 
        self.chapter = kwargs.pop("chapter", None)
        super(OfficerBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        if hasattr(self, 'chapter'):
            kwargs['chapter'] = self.chapter
        return super(OfficerBaseFormSet, self)._construct_form(i, **kwargs)


class OfficerForm(forms.ModelForm):
    user = UserModelChoiceField(queryset=User.objects.none())

    class Meta:
        model = Officer
        exclude = ('chapter',)

    def __init__(self, chapter, *args, **kwargs):
        kwargs.update({'use_required_attribute': False})
        super(OfficerForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['position', 'user', 'phone']
        # Initialize user.  Label depends on nullability.
        # Priority
        # 1. fullname
        # 2. username
        # 3. email
        if chapter:
            self.fields['user'].queryset = User.objects.filter(group_member__group=chapter.group)
        else:
            self.fields['user'].queryset = User.objects.none()
        self.fields['user'].widget.attrs['class'] = 'officer-user'
        self.fields['expire_dt'].widget.attrs['class'] = 'datepicker'


class ChapterSearchForm(FormControlWidgetMixin, forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    region = forms.ChoiceField(choices=(), required=False)
    state = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwargs):
        super(ChapterSearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update({'placeholder': _('Chapter title / keywords')})
        if Chapter.objects.exclude(region__isnull=True).exists():
            regions = Region.objects.filter(id__in=Chapter.objects.values_list('region', flat=True))
            self.fields['region'].choices = [('', _('All Regions'))] + [(region.id, region.region_name) for region in regions]
        else:
            del self.fields['region']
            
        if Chapter.objects.exclude(state='').exists():
            states = Chapter.objects.exclude(state='').values_list('state', flat=True).distinct()
            self.fields['state'].choices = [('', _('All States'))] + [(state, state) for state in states]
        else:
            del self.fields['state']

