import imghdr
import decimal
import chardet
from os.path import splitext
import operator
from uuid import uuid4
from os.path import join
from datetime import datetime
from functools import reduce
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.forms.fields import ChoiceField
#from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.files.storage import default_storage
from django.template.defaultfilters import filesizeformat
from django.contrib.contenttypes.models import ContentType

# from captcha.fields import CaptchaField
#from tendenci.apps.base.forms import SimpleMathField
from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.industries.models import Industry
from tendenci.apps.memberships.fields import (NoticeTimeTypeField, DonationOptionAmountField)
from tendenci.apps.memberships.widgets import DonationOptionAmountWidget
from tendenci.apps.corporate_memberships.widgets import NoticeTimeTypeWidget
from tendenci.apps.corporate_memberships.models import (
    CorporateMembershipType,
    CorpMembership,
    CorpProfile,
    CorpMembershipApp,
    CorpMembershipAppField,
    CorpMembershipRep,
    CorpMembershipImport,
    Creator,
    Notice)
from tendenci.apps.corporate_memberships.utils import (
    get_corpmembership_type_choices,
    get_indiv_memberships_choices,
    update_authorized_domains,
    get_payment_method_choices,
    get_notice_token_help_text,
    csv_to_dict)
from tendenci.apps.corporate_memberships.settings import UPLOAD_ROOT
from tendenci.apps.base.fields import PriceField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.files.utils import get_max_file_upload_size
from tendenci.apps.base.forms import CustomCatpchaField

fs = FileSystemStorage(location=UPLOAD_ROOT)


class CorporateMembershipTypeForm(forms.ModelForm):
    description = forms.CharField(label=_('Description'),
                                  max_length=500,
                                  required=False,
                               widget=forms.Textarea(
                                    attrs={'rows': '3'}))
    price = PriceField(decimal_places=2, help_text=_("Set 0 for free membership."))
    renewal_price = PriceField(decimal_places=2,
                                       required=False,
                               help_text=_("Set 0 for free membership."))
    above_cap_price = PriceField(decimal_places=2, help_text=_("Price for members who join above cap."))
    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')),
                 ('inactive', _('Inactive')),
                 ('admin hold', _('Admin Hold')),))

    class Meta:
        model = CorporateMembershipType
        fields = (
                  'name',
                  'price',
                  'renewal_price',
                  'membership_type',
                  'apply_cap',
                  'membership_cap',
                  'allow_above_cap',
                  'above_cap_price',
                  'description',
                  'admin_only',
                  'number_passes',
                  'position',
                  'pending_group',
                  'active_group',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs):
        super(CorporateMembershipTypeForm, self).__init__(*args, **kwargs)
        self.fields['pending_group'].queryset = self.fields['pending_group'].queryset.exclude(
                    type='system_generated').exclude(type='membership')
        self.fields['active_group'].queryset = self.fields['active_group'].queryset.exclude(
                    type='system_generated').exclude(type='membership')

    def clean(self):
        cleaned_data = self.cleaned_data
        pending_group = cleaned_data.get("pending_group")
        active_group = cleaned_data.get("active_group")
        if pending_group and active_group and pending_group == active_group:
            raise forms.ValidationError(_('The "Group for Reps upon Pending" and "Group for Reps upon Approval" can not be the same.'))
        return cleaned_data

    def clean_pending_group(self):
        pending_group = self.cleaned_data['pending_group']
        if pending_group:
            if not self.instance or not self.instance.pending_group or self.instance.pending_group != pending_group:
                if pending_group.members.count() > 0:
                    raise forms.ValidationError(_("This group is not empty. Please select another one or add a new group."))
        return pending_group
    
    def clean_active_group(self):
        active_group = self.cleaned_data['active_group']
        if active_group:
            if not self.instance or not self.instance.active_group or self.instance.active_group != active_group:
                if active_group.members.count() > 0:
                    raise forms.ValidationError(_("This group is not empty. Please select another one or add a new group."))
        return active_group

class FreePassesForm(forms.ModelForm):

    class Meta:
        model = CorpMembership
        fields = ('total_passes_allowed',)


class CorpMembershipAppForm(TendenciBaseForm):
    description = forms.CharField(required=False,
                     widget=TinyMCE(
                    attrs={'style': 'width:70%'},
                    mce_attrs={
                   'storme_app_label': CorpMembershipApp._meta.app_label,
                   'storme_model': CorpMembershipApp._meta.model_name.lower()}),
                   help_text=_('Will show at the top of the application form.'))
    confirmation_text = forms.CharField(required=False,
                 widget=TinyMCE(
                    attrs={'style': 'width:70%'},
                    mce_attrs={'storme_app_label': CorpMembershipApp._meta.app_label,
                               'storme_model': CorpMembershipApp._meta.model_name.lower()}),
                               help_text=_('Will show on the confirmation page.'))
    notes = forms.CharField(label=_('Notes'), required=False,
               widget=forms.Textarea(attrs={'rows': '3'}),
               help_text=_('Notes for editor. Will not display on the application form.'))
    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')),
                 ('inactive', _('Inactive')),
                 ('admin hold', _('Admin Hold')),))

    class Meta:
        model = CorpMembershipApp
        fields = (
                  'name',
                  'slug',
                  'corp_memb_type',
                  'authentication_method',
                  'memb_app',
                  'payment_methods',
                  'include_tax',
                  'tax_rate',
                  'description',
                  'confirmation_text',
                  'notes',
                  'parent_entities',
                  'allow_anonymous_view',
                  'user_perms',
                  'member_perms',
                  'group_perms',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs):
        super(CorpMembershipAppForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs[
                'app_instance_id'] = self.instance.pk
            self.fields['confirmation_text'].widget.mce_attrs[
                'app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs[
                'app_instance_id'] = 0
            self.fields['confirmation_text'].widget.mce_attrs[
                'app_instance_id'] = 0

    def clean(self):
        cleaned_data = super(CorpMembershipAppForm, self).clean()
        is_public = cleaned_data.get('allow_anonymous_view')
        corp_memb_types = cleaned_data.get('corp_memb_type')

        if is_public and corp_memb_types:
            public_types = [not cm_type.admin_only for cm_type in corp_memb_types]
            if not any(public_types):
                raise forms.ValidationError(_(
                    'Please select a public corporate membership type. \
                    All types currently selected are admin only.'))

        return cleaned_data


class CorpMembershipAppFieldAdminForm(forms.ModelForm):
    class Meta:
        model = CorpMembershipAppField
        fields = (
                'corp_app',
                'label',
                'field_name',
                'required',
                'display',
                'admin_only',
                'field_type',
                'description',
                'help_text',
                'choices',
                'default_value',
                'css_class'
                  )

    def __init__(self, *args, **kwargs):
        super(CorpMembershipAppFieldAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            if not self.instance.field_name:
                self.fields['field_type'].choices = CorpMembershipAppField.FIELD_TYPE_CHOICES2
            else:
                self.fields['field_type'].choices = CorpMembershipAppField.FIELD_TYPE_CHOICES1

            if self.instance.field_name in ['tax_exempt']:
                # handle boolean fields
                self.fields['field_type'].choices = (("BooleanField", _("Checkbox")),
                                ("ChoiceField", _("Select One from a list (Drop Down)")),
                                ("ChoiceField/django.forms.RadioSelect",
                                    _("Select One from a list (Radio Buttons)")),)
                self.fields['choices'].widget = forms.widgets.Select(
                                            choices=(('yesno', _('Yes/No')),))

    def save(self, *args, **kwargs):
        self.instance = super(CorpMembershipAppFieldAdminForm, self).save(*args, **kwargs)
        if self.instance:
            if not self.instance.field_name:
                if self.instance.field_type != 'section_break':
                    self.instance.field_type = 'section_break'
                    self.instance.save()
            else:
                if self.instance.field_type == 'section_break':
                    self.instance.field_type = 'CharField'
                    self.instance.save()
        return self.instance


field_size_dict = {
        'name': 36,
        'city': 24,
        'state': 12,
        'country': 14,
        'zip': 24,
        'phone': 22,
        'url': 36,
        'number_employees': 5,
        'referral_source': 28,
        'referral_source_member_name': 40,
        'referral_source_other': 28,
        'referral_source_member_number': 20,
                   }


def get_field_size(app_field_obj):
    return field_size_dict.get(app_field_obj.field_name, '') or 28


def assign_fields(form, app_field_objs, instance=None):
    # a list of names of app fields
    field_names = [field.field_name for field in app_field_objs
                   if field.field_name != '' and
                   field.field_name in form.fields]
    for name in list(form.fields):
        if name not in field_names:
            del form.fields[name]
    # update the field attrs - label, required...
    for obj in app_field_objs:
        obj.display_only = False

        # on edit set corporate_membership_type and payment_method
        # as display only
        if instance and instance.pk and obj.field_name in ['corporate_membership_type',
                              'payment_method']:
            obj.display_only = True
            if obj.field_name == 'corporate_membership_type':
                obj.display_content = instance.corporate_membership_type.name
                del form.fields['corporate_membership_type']
                continue
            if obj.field_name == 'payment_method':
                if 'payment_method' in form.fields:
                    del form.fields['payment_method']
                if instance.payment_method:
                    obj.display_content = instance.payment_method
                else:
                    obj.display_only = False
                
                if instance.invoice:
                    obj.display_content = """%s - <a href="%s">View Invoice</a>
                                        """ % (obj.display_content,
                                        instance.invoice.get_absolute_url())
                continue

        if obj.field_name in field_names:
            if obj.field_type and obj.field_name not in [
                                    'payment_method',
                                    'corporate_membership_type',
                                    'status',
                                    'status_detail',
                                    'parent_entity',
                                    'industry',
                                    'region']:
                # create form field with customized behavior
                field = obj.get_field_class(
                        initial=form.fields[obj.field_name].initial)
                form.fields[obj.field_name] = field
            else:
                field = form.fields[obj.field_name]
                field.label = obj.label
                field.required = obj.required
                if obj.help_text:
                    field.help_text = obj.help_text

            obj.field_stype = field.widget.__class__.__name__.lower()

            if obj.field_stype == 'textinput':
                size = get_field_size(obj)
                field.widget.attrs.update({'size': size})
            elif obj.field_stype == 'datetimeinput':
                field.widget.attrs.update({'class': 'datepicker'})
            label_type = []
            if obj.field_name not in ['payment_method',
                                      'corporate_membership_type',
                                      ] \
                    and obj.field_stype not in [
                        'radioselect',
                        'checkboxselectmultiple']:
                obj.field_div_class = 'inline-block'
                label_type.append('inline-block')
                if len(obj.label) < 16:
                    label_type.append('short-label')
                    #if obj.field_stype == 'textarea':
                label_type.append('float-left')
                obj.field_div_class = 'float-left'
            obj.label_type = ' '.join(label_type)


class CorpProfileBaseForm(FormControlWidgetMixin, forms.ModelForm):
    logo_file = forms.FileField(
      required=False,
      help_text=_('Company logo. Only jpg, gif, or png images.'))

    def clean_logo_file(self):
        ALLOWED_LOGO_EXT = (
            '.jpg',
            '.jpeg',
            '.gif',
            '.png'
        )

        logo_file = self.cleaned_data['logo_file']
        if logo_file:
            try:
                extension = splitext(logo_file.name)[1]

                # check the extension
                if extension.lower() not in ALLOWED_LOGO_EXT:
                    raise forms.ValidationError(_('The logo must be of jpg, gif, or png image type.'))

                # check the image header
                image_type = '.%s' % imghdr.what('', logo_file.read())
                if image_type not in ALLOWED_LOGO_EXT:
                    raise forms.ValidationError(_('The logo is an invalid image. Try uploading another logo.'))

                max_upload_size = get_max_file_upload_size()
                if logo_file.size > max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(logo_size)s') % {
                                                    'max_upload_size': filesizeformat(max_upload_size),
                                                    'logo_size': filesizeformat(logo_file.size)})
            except IOError:
                logo_file = None

        return logo_file


class CorpProfileAdminForm(CorpProfileBaseForm):
    class Meta:
        model = CorpProfile
        fields = ('logo_file',
                'name',
                'url',
                'number_employees',
                 'phone',
                 'email',
                 'parent_entity',
                 'address',
                 'address2',
                 'city',
                 'state',
                 'zip',
                 'country',
                 'description',
                 'notes',)

    def __init__(self, *args, **kwargs):
        super(CorpProfileAdminForm, self).__init__(*args, **kwargs)

        if self.instance.logo:
            self.initial['logo_file'] = self.instance.logo.file

        # assign the selected parent_entities to the drop down
        f = self.fields.get('parent_entity', None)
        if f is not None:
            corpmembership_app = CorpMembershipApp.objects.current_app()
            selected_parent_entities = corpmembership_app.parent_entities.all()
            if selected_parent_entities.exists():
                f.queryset = corpmembership_app.parent_entities.all()

    def clean_number_employees(self):
        number_employees = self.cleaned_data['number_employees']
        if not number_employees:
            number_employees = 0

        return number_employees

    def save(self, *args, **kwargs):
        super(CorpProfileAdminForm, self).save(*args, **kwargs)
        from tendenci.apps.files.models import File
        content_type = ContentType.objects.get(
            app_label=self.instance._meta.app_label,
            model=self.instance._meta.model_name)
        logo_file = self.cleaned_data.get('logo_file', None)
        if logo_file:
            file_object, created = File.objects.get_or_create(
                file=logo_file,
                defaults={
                    'name': logo_file.name,
                    'content_type': content_type,
                    'object_id': self.instance.pk,
                    'is_public': True,
                })
            self.instance.logo = file_object
            self.instance.save(log=False)
        else:
            self.instance.logo = None
            self.instance.save(log=False)
            File.objects.filter(
                        content_type=content_type,
                        object_id=self.instance.pk).delete()

        return self.instance


class CorpProfileForm(CorpProfileBaseForm):
    class Meta:
        model = CorpProfile
        fields = "__all__"

    def __init__(self, app_field_objs, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.corpmembership_app = kwargs.pop('corpmembership_app')
        super(CorpProfileForm, self).__init__(*args, **kwargs)

        if not app_field_objs.filter(field_name='logo_file').exists():
            del self.fields['logo_file']
        else:
            if self.instance.logo:
                self.initial['logo_file'] = self.instance.logo.file

        assign_fields(self, app_field_objs)
        self.add_form_control_class()

        if self.corpmembership_app.authentication_method == 'email':
            self.fields['authorized_domain'] = forms.CharField(help_text="""
            <span style="color: #990000;">comma separated (ex: mydomain.com,
            mydomain.net).</span><br />The
            authorized e-mail  domain will authenticate prospective<br />
            members as they apply for membership under this company.
            """)
            if self.instance.pk:
                auth_domains = ', '.join([domain.name for domain
                             in self.instance.authorized_domains.all()])
                self.fields['authorized_domain'].initial = auth_domains
        if 'secret_code' in self.fields:
            if not self.corpmembership_app.authentication_method == 'secret_code':
                del self.fields['secret_code']
            else:
                self.fields['secret_code'].help_text = 'This is the code ' + \
                    'your members will need when joining under your corporation'

        if 'status' in self.fields:
            del self.fields['status']
        if 'status_detail' in self.fields:
            del self.fields['status_detail']

        # assign the selected parent_entities to the drop down
        f = self.fields.get('parent_entity', None)
        if f is not None:
            selected_parent_entities = self.corpmembership_app.parent_entities.all()
            if selected_parent_entities.exists():
                f.queryset = self.corpmembership_app.parent_entities.all()

        self.field_names = [name for name in self.fields]

    def clean_secret_code(self):
        secret_code = self.cleaned_data['secret_code']
        if secret_code:
            # check if this secret_code is available to ensure the uniqueness
            corp_profiles = CorpProfile.objects.filter(
                                secret_code=secret_code)
            if self.instance:
                corp_profiles = corp_profiles.exclude(id=self.instance.id)
            if corp_profiles:
                raise forms.ValidationError(
            _("This secret code is already taken. Please use a different one.")
            )
        return self.cleaned_data['secret_code']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if CorpProfile.objects.all_inactive().filter(name=name).exists():
                raise forms.ValidationError(
                _("'%s' is not available. Please use a different name." % name)
                )
        return self.cleaned_data['name']

    def clean_number_employees(self):
        number_employees = self.cleaned_data['number_employees']
        if not number_employees:
            number_employees = 0

        return number_employees

    def save(self, *args, **kwargs):
        from tendenci.apps.files.models import File
        if not self.instance.id:
            if not self.request_user.is_anonymous:
                self.instance.creator = self.request_user
                self.instance.creator_username = self.request_user.username
            self.instance.status = True
            self.instance.status_detail = 'active'
        if not self.request_user.is_anonymous:
            self.instance.owner = self.request_user
            self.instance.owner_username = self.request_user.username
        for field_key in self.fields:
            if self.fields[field_key].widget.needs_multipart_form:
                value = self.cleaned_data[field_key]
                if value and hasattr(value, 'name'):
                    value = default_storage.save(join("corporate_memberships",
                                                      str(uuid4()),
                                                      value.name),
                                                 value)
                    setattr(self.instance, field_key, value)

        super(CorpProfileForm, self).save(*args, **kwargs)

        # update authorized domain if needed
        if self.corpmembership_app.authentication_method == 'email':
            update_authorized_domains(self.instance,
                            self.cleaned_data['authorized_domain'])

        content_type = ContentType.objects.get(
            app_label=self.instance._meta.app_label,
            model=self.instance._meta.model_name)
        logo_file = self.cleaned_data.get('logo_file', None)
        if logo_file:
            file_object, created = File.objects.get_or_create(
                file=logo_file,
                defaults={
                    'name': logo_file.name,
                    'content_type': content_type,
                    'object_id': self.instance.pk,
                    'is_public': True,
                })
            self.instance.logo = file_object
            self.instance.save(log=False)
        else:
            self.instance.logo = None
            self.instance.save(log=False)
            File.objects.filter(
                        content_type=content_type,
                        object_id=self.instance.pk).delete()

        return self.instance


class CorpMembershipUpgradeForm(forms.ModelForm):

    class Meta:
        model = CorpMembership
        fields = ["corporate_membership_type"]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.corpmembership_app = kwargs.pop('corpmembership_app')
        super(CorpMembershipUpgradeForm, self).__init__(*args, **kwargs)
        self.fields['corporate_membership_type'].widget = forms.widgets.RadioSelect(
            choices=get_corpmembership_type_choices(
                self.request_user,
                self.corpmembership_app,
                exclude_list=[self.instance.corporate_membership_type.id]),
            attrs=self.fields['corporate_membership_type'].widget.attrs)


class CorpMembershipForm(FormControlWidgetMixin, forms.ModelForm):
    STATUS_DETAIL_CHOICES = (
            ('active', _('Active')),
            ('pending', _('Pending')),
            ('paid - pending approval', _('Paid - Pending Approval')),
            ('expired', _('Expired')),
                             )
    STATUS_CHOICES = (
                      (1, _('Active')),
                      (0, _('Inactive'))
                      )

    class Meta:
        model = CorpMembership
        fields = "__all__"

    def __init__(self, app_field_objs, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.corpmembership_app = kwargs.pop('corpmembership_app')
        super(CorpMembershipForm, self).__init__(*args, **kwargs)
        self.fields['corporate_membership_type'].widget = forms.widgets.RadioSelect(
            choices=get_corpmembership_type_choices(
                self.request_user,
                self.corpmembership_app),
            attrs=self.fields['corporate_membership_type'].widget.attrs)
        self.fields['corporate_membership_type'].empty_label = None
        if 'class' in self.fields['corporate_membership_type'].widget.attrs:
            type_class = self.fields['corporate_membership_type'].widget.attrs['class']
            # remove form-control class
            type_class = type_class.replace('form-control', '')
            self.fields['corporate_membership_type'].widget.attrs['class'] = type_class
        # if all membership types are free, no need to display payment method
        require_payment = self.corpmembership_app.corp_memb_type.filter(
                                price__gt=0).exists()
        if not require_payment:
            del self.fields['payment_method']
        else:
            self.fields['payment_method'].empty_label = None
            self.fields['payment_method'].widget = forms.widgets.RadioSelect(
                        choices=get_payment_method_choices(
                                    self.request_user,
                                    self.corpmembership_app))
        if 'status_detail' in self.fields:
            self.fields['status_detail'].widget = forms.widgets.Select(
                        choices=self.STATUS_DETAIL_CHOICES)
        if 'status' in self.fields:
            self.fields['status'].widget = forms.widgets.Select(
                        choices=self.STATUS_CHOICES)

        assign_fields(self, app_field_objs, instance=self.instance)
        self.add_form_control_class()
        self.field_names = [name for name in self.fields]

    def save(self, **kwargs):
        super(CorpMembershipForm, self).save(commit=False)
        anonymous_creator = kwargs.get('creator')
        corp_profile = kwargs.get('corp_profile')
        creator_owner = self.request_user
        if not self.instance.pk:
            if anonymous_creator:
                self.instance.anonymous_creator = anonymous_creator
#             if not isinstance(self.request_user, User):
#                 [creator_owner] = User.objects.filter(
#                     is_staff=1,
#                     is_active=1)[:1] or [None]
            if not self.request_user.profile.is_superuser:
                self.instance.status = True
                self.instance.status_detail = 'pending'
            if not self.instance.join_dt:
                self.instance.join_dt = datetime.now()
            if not creator_owner.is_anonymous:
                self.instance.creator = creator_owner
                self.instance.creator_username = creator_owner.username
        if not creator_owner.is_anonymous:
            self.instance.owner = creator_owner
            self.instance.owner_username = creator_owner.username
        if corp_profile:
            self.instance.corp_profile = corp_profile
        self.instance.save()

        return self.instance


class CorpMembershipRenewForm(forms.ModelForm):
    members = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        choices=[],
                                        required=False)
    select_all_members = forms.BooleanField(widget=forms.CheckboxInput(),
                                            required=False)

    class Meta:
        model = CorpMembership
        fields = ('corporate_membership_type',
                  'payment_method',
                  )

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.corpmembership_app = kwargs.pop('corpmembership_app')

        super(CorpMembershipRenewForm, self).__init__(*args, **kwargs)

        self.fields['corporate_membership_type'].widget = forms.RadioSelect(
                    choices=get_corpmembership_type_choices(
                                self.request_user,
                                self.corpmembership_app,
                                renew=True))
        self.fields['corporate_membership_type'].empty_label = None
        self.fields['corporate_membership_type'
                ].initial = self.instance.corporate_membership_type.id

        members_choices = get_indiv_memberships_choices(self.instance)
        self.fields['members'].choices = members_choices
        self.fields['members'].label = _("Select the individual members you " +
                                        "want to renew")
        
        if self.corpmembership_app.donation_enabled:
            self.fields['donation_option_value'] = DonationOptionAmountField(required=False)
            self.fields['donation_option_value'].label = self.corpmembership_app.donation_label
            self.fields['donation_option_value'].widget = DonationOptionAmountWidget(attrs={},
                                                default_amount=self.corpmembership_app.donation_default_amount)

        #if not self.instance.corporate_membership_type.membership_type.renewal_price:
        self.fields['select_all_members'].initial = False
        #self.fields['members'].initial = [c[0] for c in members_choices]

        self.fields['payment_method'].widget = forms.RadioSelect(
                                    choices=get_payment_method_choices(
                                    self.request_user,
                                    self.corpmembership_app))
        self.fields['payment_method'].empty_label = None
        self.fields['payment_method'].initial = \
                self.instance.payment_method

    def clean(self):
        cleaned_data = super(CorpMembershipRenewForm, self).clean()
        cmt = cleaned_data['corporate_membership_type']
        members = cleaned_data['members']
        count_members = len(members)
        if cmt.apply_cap:
            if not cmt.allow_above_cap:
                if count_members > cmt.membership_cap:
                    raise forms.ValidationError(
                        _("You've selected {count} individual members, but the maximum allowed is {cap}.".format(count=count_members,  cap=cmt.membership_cap)) )

        return cleaned_data

    def clean_donation_option_value(self):
        value_list = self.cleaned_data['donation_option_value']
        if value_list:
            donation_option, donation_amount = value_list
            if donation_option == 'custom':
                # validate donation_amount
                try:
                    donation_amount = donation_amount.replace('$', '').replace(',', '')
                    donation_amount = decimal.Decimal(donation_amount)
                    return (donation_option, donation_amount)
                except decimal.InvalidOperation:
                    raise forms.ValidationError(_("Please enter a valid donation amount."))

        return value_list


class RosterSearchAdvancedForm(forms.Form):
    SEARCH_CRITERIA_CHOICES = (
                        ('', _('SELECT ONE')),
                        ('username', _('Username')),
                        ('member_number', _('Member Number')),
                        ('phone', _('Phone')),
                        ('city', _('City')),
                        ('state', _('State')),
                        ('zipcode', _('Zip Code')),
                        ('country', _('Country'))
                               )
    SEARCH_METHOD_CHOICES = (
                             ('starts_with', _('Starts With')),
                             ('contains', _('Contains')),
                             ('exact', _('Exact')),
                             )
    cm_id = forms.ChoiceField(label=_('Company Name'),
                                  required=False)
    first_name = forms.CharField(label=_('First Name'),
                                 max_length=100,
                                 required=False)
    last_name = forms.CharField(label=_('Last Name'),
                                max_length=100, required=False)
    email = forms.CharField(label=_('Email'),
                            max_length=100, required=False)
    search_criteria = forms.ChoiceField(choices=SEARCH_CRITERIA_CHOICES,
                                        required=False)
    search_text = forms.CharField(max_length=100, required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False)
    active_only = forms.BooleanField(label=_('Show Active Only'),
                                     widget=forms.CheckboxInput(),
                                     initial=True, required=False)

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user')
        super(RosterSearchAdvancedForm, self).__init__(*args, **kwargs)
        choices = CorpMembership.get_my_corporate_profiles_choices(request_user)
        self.fields['cm_id'].choices = choices


class CorpMembershipSearchForm(FormControlWidgetMixin, forms.Form):
    SEARCH_METHOD_CHOICES = (
                             ('starts_with', _('Starts With')),
                             ('contains', _('Contains')),
                             ('exact', _('Exact')),
                             )
    cp_id = forms.ChoiceField(label=_('Company Name'),
                                  required=False)
    search_criteria = forms.ChoiceField(required=False)
    search_text = forms.CharField(max_length=100, required=False)
    search_method = forms.ChoiceField(
        choices=SEARCH_METHOD_CHOICES,
        required=False
    )
    active_only = forms.BooleanField(label=_('Show Active Only'),
                                     widget=forms.CheckboxInput(),
                                     initial=True, required=False)

    def __init__(self, *args, **kwargs):
        search_field_names_list = kwargs.pop('names_list')
        user = kwargs.pop('user')
        super(CorpMembershipSearchForm, self).__init__(*args, **kwargs)
        # add industry field if industry exists
        app = CorpMembershipApp.objects.current_app()
        if app:
            [industry_field] = app.fields.filter(
                        field_name='industry',
                        display=True
                            )[:1] or [None]

            if industry_field:
                industries = Industry.objects.all()
                if industries:
                    industries_choices = [(0, _('Select One'))]
                    for industry in industries:
                        industries_choices.append((industry.id, industry.industry_name))
                    self.fields['industry'] = forms.ChoiceField(
                                label=industry_field.label,
                                choices=industries_choices,
                                required=False
                                    )
                    self.fields['industry'].widget.attrs.update({'class': 'form-control'})
        # search criteria choices
        search_choices = []
        fields = CorpMembershipAppField.objects.filter(
                        field_name__in=search_field_names_list,
                        display=True)
        if app:
            fields = fields.filter(corp_app=app)
        fields = fields.order_by('label')

        for field in fields:
            label = field.label
            if len(label) > 30:
                label = '%s...' % label[:30]
            search_choices.append((field.field_name, label))
        if user and user.is_superuser:
            search_choices.append(('status_detail', 'Status Detail'))
        self.fields['search_criteria'].choices = search_choices


class ReportByTypeForm(FormControlWidgetMixin, forms.Form):
    DAYS_CHOICES = (
                 ('0', 'ALL'),
                 ('30', _('Last 30 days')),
                 ('60', _('Last 60 days')),
                 ('90', _('Last 90 days')),
                 ('180', _('Last 180 days')),
                 ('365', _('Last 365 days')),
                 ('1826', _('Last 5 years')),
                 )
    days = forms.ChoiceField(label=_('Join Date'),
                             required=False,
                            choices=DAYS_CHOICES,)
    corp_membership_type = forms.ChoiceField(label=_('Type'),
                            required=False,
                            choices= ())

    def __init__(self, *args, **kwargs):
        super(ReportByTypeForm, self).__init__(*args, **kwargs)

        self.fields['days'].widget.attrs.update({'onchange': 'this.form.submit();'})
        self.fields['corp_membership_type'].choices = [(0, 'ALL')] + \
                                [(t.id, t.name) for t in CorporateMembershipType.objects.filter(
                                status=True,
                                status_detail='active'
                                ).order_by('name')]
        self.fields['corp_membership_type'].widget.attrs.update({'onchange': 'this.form.submit();'})
        self.fields['corp_membership_type'].choices = ([(0, 'ALL')] +
            [(t.id, t.name) for t in CorporateMembershipType.objects.filter(
             status=True,
             status_detail='active'
             ).order_by('name')])


class ReportByStatusForm(FormControlWidgetMixin, forms.Form):
    STATUS_CHOICES = (
                 ('', 'ALL'),
                 ('active', _('Active')),
                 ('pending', _('Pending')),
                 ('paid - pending approval', _('Paid - Pending Approval')),
                 ('expired', _('Expired')),
                 )
    days = forms.ChoiceField(label=_('Join Date'),
                             required=False,
                            choices=ReportByTypeForm.DAYS_CHOICES,)
    status_detail = forms.ChoiceField(label=_('Status'),
                            required=False,
                            choices=STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        super(ReportByStatusForm, self).__init__(*args, **kwargs)

        self.fields['days'].widget.attrs.update({'onchange': 'this.form.submit();'})
        self.fields['status_detail'].widget.attrs.update({'onchange': 'this.form.submit();'})


class CorpMembershipUploadForm(forms.ModelForm):
    KEY_CHOICES = (
        ('company_name', _('Company Name')),
        )
    key = forms.ChoiceField(label="Key",
                            choices=KEY_CHOICES)

    class Meta:
        model = CorpMembershipImport
        fields = (
                'key',
                'override',
                'bind_members',
                'upload_file',
                  )

    def __init__(self, *args, **kwargs):
        super(CorpMembershipUploadForm, self).__init__(*args, **kwargs)
        self.fields['key'].initial = 'name'
        for k in self.fields:
            if k in ['key', 'override']:
                self.fields[k].widget.attrs['class'] = 'form-control'

    def clean_upload_file(self):
        key = self.cleaned_data['key']
        upload_file = self.cleaned_data['upload_file']
        if not key:
            raise forms.ValidationError(_('Please specify the key to identify duplicates'))

        file_content = upload_file.read()
        encoding = chardet.detect(file_content)['encoding']
        file_content = file_content.decode(encoding)

        upload_file.seek(0)
        header_line_index = file_content.find('\n')
        header_list = ((file_content[:header_line_index]
                            ).strip('\r')).split(',')

        if 'company_name' not in header_list:
            msg_string = """
                        'Field company_name used to identify the duplicates
                        should be included in the .csv file.'
                        """
            raise forms.ValidationError(_(msg_string))
        return upload_file


class CorpExportForm(forms.Form):
    export_format = forms.ChoiceField(
                label=_('Export Format'),
                choices=(('csv', _('csv (Export)')),))


class CreatorForm(forms.ModelForm):
    class Meta:
        model = Creator
        fields = ('first_name',
                'last_name',
                'email', )

    def __init__(self, *args, **kwargs):
        super(CreatorForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = CustomCatpchaField(label=_('Type the code below'))
        for k in self.fields:
            self.fields[k].widget.attrs['class'] = 'form-control'


class CorpApproveForm(forms.Form):

    users = forms.ChoiceField(
        label=_('Assign creator/owner to this corporate membership'),
        choices=[],
        widget=forms.RadioSelect,
        )

    def suggested_users(self, first_name='', last_name='', email=''):
        """
            Generate list of suggested users based on the given info.
            It queries (first name and last name) or (email) if provided.
        """
        user_set = {}

        qAnd = []
        query = None
        exact_match = 0

        if email:
            query = Q(email=email)
        if first_name:
            qAnd.append(Q(first_name=first_name))
        if last_name:
            qAnd.append(Q(last_name=last_name))

        if qAnd:
            if query:
                query = reduce(operator.and_, qAnd) | query
            else:
                query = reduce(operator.and_, qAnd)

        if query:
            users = User.objects.filter(query).order_by('last_name')

            for u in users:
                user_set[u.pk] = '%s %s %s %s ' % (u.first_name,
                                                   u.last_name,
                                                   u.username,
                                                   u.email)
                if u.first_name and u.last_name and u.username:
                    if u.first_name == first_name and \
                       u.last_name == last_name and \
                       u.email == email:
                        exact_match = u.id

        return list(user_set.items()), exact_match

    def __init__(self, *args, **kwargs):
        corp_memb = kwargs.pop('corporate_membership')
        super(CorpApproveForm, self).__init__(*args, **kwargs)

        if corp_memb.is_join_pending and corp_memb.anonymous_creator:
            suggested_users, exact_match = self.suggested_users(
                           first_name=corp_memb.anonymous_creator.first_name,
                           last_name=corp_memb.anonymous_creator.last_name,
                           email=corp_memb.anonymous_creator.email)
            if not exact_match:
                suggested_users.append((0, 'Create new user for %s %s %s' % (
                                      corp_memb.anonymous_creator.first_name,
                                      corp_memb.anonymous_creator.last_name,
                                      corp_memb.anonymous_creator.email
                                                             )))
            self.fields['users'].choices = suggested_users
            self.fields['users'].initial = exact_match
        else:
            self.fields.pop('users')


class CorpMembershipRepForm(forms.ModelForm):
    user_display = forms.CharField(max_length=800,
                        required=False,
                        help_text=_('Rep must be a valid user on the website. Enter name or username or email, then press the down arrow key to select a suggestion'))

    class Meta:
        model = CorpMembershipRep
        fields = ('user_display',
                 'user',
                'is_dues_rep',
                'is_member_rep',)

    def __init__(self, corp_membership, *args, **kwargs):
        self.corp_membership = corp_membership
        super(CorpMembershipRepForm, self).__init__(*args, **kwargs)

        self.fields['user_display'].label = _("Add a Representative")
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].error_messages['required'
                                ] = _('Please enter a valid user.')

    def clean_user(self):
        value = self.cleaned_data['user']
        try:
            CorpMembershipRep.objects.get(
                corp_profile=self.corp_membership.corp_profile,
                user=value)
            raise forms.ValidationError(
                _("This user is already a representative."))
        except CorpMembershipRep.DoesNotExist:
            pass
        return value


class RosterSearchForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.HiddenInput())
    q = forms.CharField(max_length=100, required=False)


class CSVForm(forms.Form):
    """
    Map CSV import to Membership Application.
    Create Membership Entry on save() method.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically create fields using the membership
        application chosen.  The choices provided to these
        dynamic fields are the csv import columns.
        """
        step_numeral, step_name = kwargs.pop('step', (None, None))
        corp_app = kwargs.pop('corp_app', '')
        file_path = kwargs.pop('file_path', '')

        super(CSVForm, self).__init__(*args, **kwargs)

        if step_numeral == 1:
            """
            Basic Form: Application & File Uploader
            """
            self.fields['corp_app'] = forms.ModelChoiceField(
                label=_('Corp Application'), queryset=CorpMembershipApp.objects.all())

            self.fields['update_option'] = forms.CharField(
                    widget=forms.RadioSelect(
                        choices=(('skip', _('Skip')),
                                 ('update', _('Update Blank Fields')),
                                ('override', _('Override All Fields')),)),
                        initial='skip',
                        label=_('Select an Option for the Existing Records:')
                    )

            self.fields['csv'] = forms.FileField(label=_("CSV File"))

        if step_numeral == 2:
            """
            Basic Form + Mapping Fields
            """

            # file to make field-mapping form
            csv = csv_to_dict(file_path)

            # choices list
            choices = csv[0]

            # make tuples; sort tuples (case-insensitive)
            choice_tuples = [(c, c) for c in csv[0]]

            # insert blank option
            choice_tuples.insert(0, ('', ''))
            choice_tuples = sorted(choice_tuples, key=lambda c: c[0].lower())

            app_fields = CorpMembershipAppField.objects.filter(corp_app=corp_app)
            required_fields = ['name', 'corporate_membership_type']
            for field in app_fields:
                if field.field_type not in ['section_break', 'page_break']:
                    if field.field_name:
                        field_key = field.field_name
                    else:
                        field_key = "field_%s" % field.id
                    is_required = False
                    if field_key in required_fields:
                        is_required = True
                    self.fields[field_key] = ChoiceField(**{
                                                'label': field.label,
                                                'choices': choice_tuples,
                                                'required': is_required,
                                                })
                    for choice in choices:
                        if (field.label).lower() == choice.lower() or \
                            field_key.lower() == choice.lower():
                            self.fields[field_key].initial = choice

            extra_fields = (('secret_code', _('Secret Code')),
                            ('join_dt', _('Join Date')),
                            ('renew_dt', _('Renew Date')),
                            ('expiration_dt', _('Expiration Date')),
                            ('approved', _('Approved')),
                            ('dues_rep', _('Dues Representative')),
                            ('status', _('Status')),
                            ('status_detail', _('Status Detail')))
            # corp_memb_field_names = [smart_str(field.name)
            # for field in CorporateMembership._meta.fields]
            for key, label in extra_fields:
                if key not in self.fields:
                    self.fields[key] = ChoiceField(**{
                                            'label': label,
                                            'choices': choice_tuples,
                                            'required': False,
                                            })
                    for choice in choices:
                        if label.lower() == choice.lower() or \
                         key.lower() == choice.lower():
                            self.fields[key].initial = choice

    def clean_csv(self):
        csv = self.cleaned_data['csv']
        SUPPORTED_FILE_TYPES = ['text/csv',]

        if csv.content_type not in SUPPORTED_FILE_TYPES:
            raise forms.ValidationError(_('File type is not supported. Please upload a CSV File.'))
        return csv

    def save(self, *args, **kwargs):
        """
        Loop through the dynamic fields and create a
        corporate membership record.
        """
        step_numeral, step_name = kwargs.pop('step', (None, None))

        if step_numeral == 1:
            """
            Basic Form: Application & File Uploader
            """
            return self.cleaned_data
        if step_numeral == 2:
            """
            Basic Form + Mapping Fields
            """
            return self.cleaned_data

        if step_numeral == 3:
            pass  # end-user is previewing


class NoticeForm(forms.ModelForm):
    notice_time_type = NoticeTimeTypeField(
        label=_('When to Send'), widget=NoticeTimeTypeWidget)
    email_content = forms.CharField(
        widget=TinyMCE(attrs={'style':'width:70%'},
                       mce_attrs={'storme_app_label': Notice._meta.app_label,
                                  'storme_model':Notice._meta.model_name.lower()}),
        help_text=_("Click here to view available tokens"))

    class Meta:
        model = Notice
        fields = (
            'notice_name',
            'notice_time_type',
            'corporate_membership_type',
            'subject',
            'content_type',
            'sender',
            'sender_display',
            'email_content',
            'status_detail',)

    def __init__(self, *args, **kwargs):
        super(NoticeForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['email_content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['email_content'].widget.mce_attrs['app_instance_id'] = 0

        initial_list = []
        if self.instance.pk:
            initial_list.append(str(self.instance.num_days))
            initial_list.append(str(self.instance.notice_time))
            initial_list.append(str(self.instance.notice_type))

        self.fields['notice_time_type'].initial = initial_list

        self.fields['email_content'].help_text = get_notice_token_help_text(self.instance)

    def clean_notice_time_type(self):
        value = self.cleaned_data['notice_time_type']

        data_list = value.split(',')
        d = dict(zip(['num_days', 'notice_time', 'notice_type'], data_list))

        try:
            d['num_days'] = int(d['num_days'])
        except:
            raise forms.ValidationError(_("Num days must be a numeric number."))
        return value
