import operator
from uuid import uuid4
from os.path import join
from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.forms.fields import ChoiceField
#from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db.models import Q

from captcha.fields import CaptchaField
from tinymce.widgets import TinyMCE

from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.addons.memberships.fields import PriceInput
from tendenci.addons.corporate_memberships.models import (
                    CorporateMembershipType,
                    CorpMembership,
                    CorpProfile,
                    CorpMembershipApp,
                    CorpMembershipRep,
                    CorpMembershipImport,
                    CorpApp,
                    CorpField,
                    CorporateMembership,
                    Creator,
                    CorporateMembershipRep,
                    CorpMembRenewEntry)
from tendenci.addons.corporate_memberships.utils import (
                 get_corpmembership_type_choices,
                 get_corp_memberships_choices,
                 get_indiv_memberships_choices,
                 update_authorized_domains,
                 get_corpapp_default_fields_list,
                 update_auth_domains,
                 get_payment_method_choices,
                 get_indiv_membs_choices,
                 get_corporate_membership_type_choices,
                 csv_to_dict)
from tendenci.addons.corporate_memberships.settings import UPLOAD_ROOT
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.payments.models import PaymentMethod

fs = FileSystemStorage(location=UPLOAD_ROOT)


class CorporateMembershipTypeForm(forms.ModelForm):
    description = forms.CharField(label=_('Description'),
                                  max_length=500,
                                  required=False,
                               widget=forms.Textarea(
                                    attrs={'rows': '3'}))
    price = forms.DecimalField(decimal_places=2, widget=PriceInput(),
                               help_text="Set 0 for free membership.")
    renewal_price = forms.DecimalField(decimal_places=2,
                                       widget=PriceInput(),
                                       required=False,
                               help_text="Set 0 for free membership.")
    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'),
                 ('inactive', 'Inactive'),
                 ('admin hold', 'Admin Hold'),))

    class Meta:
        model = CorporateMembershipType
        fields = (
                  'name',
                  'price',
                  'renewal_price',
                  'membership_type',
                  'description',
                  'apply_threshold',
                  'individual_threshold',
                  'individual_threshold_price',
                  'admin_only',
                  'position',
                  'status',
                  'status_detail',
                  )


class CorpMembershipAppForm(TendenciBaseForm):
    description = forms.CharField(required=False,
                     widget=TinyMCE(
                    attrs={'style': 'width:70%'},
                    mce_attrs={
                   'storme_app_label': CorpMembershipApp._meta.app_label,
                   'storme_model': CorpMembershipApp._meta.module_name.lower()}),
                   help_text='Will show at the top of the application form.')
    confirmation_text = forms.CharField(required=False,
                 widget=TinyMCE(
                    attrs={'style': 'width:70%'},
                    mce_attrs={'storme_app_label': CorpMembershipApp._meta.app_label,
                               'storme_model': CorpMembershipApp._meta.module_name.lower()}),
                               help_text='Will show on the confirmation page.')
    notes = forms.CharField(label=_('Notes'), required=False,
               widget=forms.Textarea(attrs={'rows': '3'}),
               help_text='Notes for editor. Will not display on the application form.')
    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'),
                 ('inactive', 'Inactive'),
                 ('admin hold', 'Admin Hold'),))

    class Meta:
        model = CorpMembershipApp
        fields = (
                  'name',
                  'slug',
                  'corp_memb_type',
                  'authentication_method',
                  'memb_app',
                  'payment_methods',
                  'description',
                  'confirmation_text',
                  'notes',
                  'allow_anonymous_view',
                  'user_perms',
                  'member_perms',
                  'group_perms',
                  'status',
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
    form_field_keys = form.fields.keys()
    # a list of names of app fields
    field_names = [field.field_name for field in app_field_objs \
                   if field.field_name != '' and \
                   field.field_name in form_field_keys]
    for name in form_field_keys:
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
                del form.fields['payment_method']
                obj.display_content = instance.payment_method
                if instance.invoice:
                    obj.display_content = """%s - <a href="%s">View Invoice</a>
                                        """ % (obj.display_content,
                                        instance.invoice.get_absolute_url())
                continue

        if obj.field_name in field_names:
            field = form.fields[obj.field_name]
            field.label = obj.label
            field.required = obj.required
            obj.field_stype = field.widget.__class__.__name__.lower()

            if obj.field_stype == 'textinput':
                size = get_field_size(obj)
                field.widget.attrs.update({'size': size})
            elif obj.field_stype == 'datetimeinput':
                field.widget.attrs.update({'class': 'datepicker'})
            label_type = []
            if obj.field_name not in ['payment_method',
                                      'corporate_membership_type',
                                      ]:
                obj.field_div_class = 'inline-block'
                label_type.append('inline-block')
                if len(obj.label) < 16:
                    label_type.append('short-label')
                    #if obj.field_stype == 'textarea':
                label_type.append('float-left')
                obj.field_div_class = 'float-left'
            obj.label_type = ' '.join(label_type)


class CorpProfileForm(forms.ModelForm):
    class Meta:
        model = CorpProfile

    def __init__(self, app_field_objs, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.corpmembership_app = kwargs.pop('corpmembership_app')
        super(CorpProfileForm, self).__init__(*args, **kwargs)

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
        if not self.corpmembership_app.authentication_method == 'secret_code':
            del self.fields['secret_code']
        else:
            self.fields['secret_code'].help_text = 'This is the code that ' + \
                'your members will need to enter to join under your corporate'

        del self.fields['status']
        del self.fields['status_detail']

        assign_fields(self, app_field_objs)
        self.field_names = [name for name in self.fields.keys()]

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

    def save(self, *args, **kwargs):
        if not self.instance.id:
            if not self.request_user.is_anonymous():
                self.instance.creator = self.request_user
                self.instance.creator_username = self.request_user.username
            self.instance.status = True
            self.instance.status_detail = 'active'
        if not self.request_user.is_anonymous():
            self.instance.owner = self.request_user
            self.instance.owner_username = self.request_user.username

        super(CorpProfileForm, self).save(*args, **kwargs)

        # update authorized domain if needed
        if self.corpmembership_app.authentication_method == 'email':
            update_authorized_domains(self.instance,
                            self.cleaned_data['authorized_domain'])
        return self.instance


class CorpMembershipForm(forms.ModelForm):
    STATUS_DETAIL_CHOICES = (
            ('active', 'Active'),
            ('pending', 'Pending'),
            ('paid - pending approval', 'Paid - Pending Approval'),
            ('expired', 'Expired'),
                             )
    STATUS_CHOICES = (
                      (1, 'Active'),
                      (0, 'Inactive')
                      )

    class Meta:
        model = CorpMembership

    def __init__(self, app_field_objs, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.corpmembership_app = kwargs.pop('corpmembership_app')
        super(CorpMembershipForm, self).__init__(*args, **kwargs)
        self.fields['corporate_membership_type'].widget = forms.widgets.RadioSelect(
                    choices=get_corpmembership_type_choices(self.request_user,
                                                        self.corpmembership_app),
                    attrs=self.fields['corporate_membership_type'].widget.attrs)
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
        self_fields_keys = self.fields.keys()
        if 'status_detail' in self_fields_keys:
            self.fields['status_detail'].widget = forms.widgets.Select(
                        choices=self.STATUS_DETAIL_CHOICES)
        if 'status' in self_fields_keys:
            self.fields['status'].widget = forms.widgets.Select(
                        choices=self.STATUS_CHOICES)

        assign_fields(self, app_field_objs, instance=self.instance)
        self.field_names = [name for name in self.fields.keys()]

    def save(self, **kwargs):
        super(CorpMembershipForm, self).save(commit=False)
        anonymous_creator = kwargs.get('creator', None)
        corp_profile = kwargs.get('corp_profile', None)
        creator_owner = self.request_user
        if not self.instance.pk:
            if anonymous_creator:
                self.instance.anonymous_creator = anonymous_creator
            if not isinstance(self.request_user, User):
                [creator_owner] = User.objects.filter(is_staff=1,
                                                is_active=1)[:1] or [None]
            if not self.request_user.profile.is_superuser:
                self.instance.status = True
                self.instance.status_detail = 'pending'
            if not self.instance.join_dt:
                self.instance.join_dt = datetime.now()
            if not creator_owner.is_anonymous():
                self.instance.creator = creator_owner
                self.instance.creator_username = creator_owner.username
        if not creator_owner.is_anonymous():
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
        self.fields['members'].label = "Select the individual members you " + \
                                        "want to renew"
        if self.instance.corporate_membership_type.renewal_price == 0:
            self.fields['select_all_members'].initial = True
            self.fields['members'].initial = [c[0] for c in members_choices]

        self.fields['payment_method'].widget = forms.RadioSelect(
                                    choices=get_payment_method_choices(
                                    self.request_user,
                                    self.corpmembership_app))
        self.fields['payment_method'].empty_label = None
        self.fields['payment_method'].initial = \
                self.instance.payment_method


class RosterSearchAdvancedForm(forms.Form):
    SEARCH_CRITERIA_CHOICES = (
                        ('username', _('Username')),
                        ('member_number', _('Member Number')),
                        ('phone', _('Phone')),
                        ('city', _('City')),
                        ('state', _('State')),
                        ('zip', _('Zip Code')),
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

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user')
        super(RosterSearchAdvancedForm, self).__init__(*args, **kwargs)
        choices = CorpMembership.get_my_corporate_profiles_choices(request_user)
        self.fields['cm_id'].choices = choices


class CorpMembershipSearchForm(forms.Form):
    cp_id = forms.ChoiceField(label=_('Company Name'),
                                  choices=(),
                                  required=False)
    q = forms.CharField(max_length=100,
                                 required=False)


class CorpMembershipUploadForm(forms.ModelForm):
    KEY_CHOICES = (
        ('company_name', 'Company Name'),
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

    def clean_upload_file(self):
        key = self.cleaned_data['key']
        upload_file = self.cleaned_data['upload_file']
        if not key:
            raise forms.ValidationError('Please specify the key to identify duplicates')

        file_content = upload_file.read()
        upload_file.seek(0)
        header_line_index = file_content.find('\n')
        header_list = ((file_content[:header_line_index]
                            ).strip('\r')).split(',')
        if 'company_name' not in header_list:
            raise forms.ValidationError(
                        """
                        'Field %s used to identify the duplicates
                        should be included in the .csv file.'
                        """ % 'company_name')
        return upload_file


class CorpExportForm(forms.Form):
    export_format = forms.ChoiceField(
                label=_('Export Format'),
                choices=(('csv', 'csv (Export)'),))


class CorpAppForm(forms.ModelForm):
    description = forms.CharField(required=False,
                     widget=TinyMCE(
                    attrs={'style': 'width:70%'},
                    mce_attrs={
                   'storme_app_label': CorpApp._meta.app_label,
                   'storme_model': CorpApp._meta.module_name.lower()}),
                   help_text='Will show at the top of the application form.')
    confirmation_text = forms.CharField(required=False,
                 widget=TinyMCE(
                    attrs={'style': 'width:70%'},
                    mce_attrs={'storme_app_label': CorpApp._meta.app_label,
                               'storme_model': CorpApp._meta.module_name.lower()}),
                               help_text='Will show on the confirmation page.')
    notes = forms.CharField(label=_('Notes'), required=False,
               widget=forms.Textarea(attrs={'rows': '3'}),
               help_text='Notes for editor. Will not display on the application form.')
    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'),
                 ('inactive', 'Inactive'),
                 ('admin hold', 'Admin Hold'),))

    class Meta:
        model = CorpApp
        fields = (
                  'name',
                  'slug',
                  'corp_memb_type',
                  'authentication_method',
                  'memb_app',
                  'payment_methods',
                  'description',
                  'confirmation_text',
                  'notes',
                  #'use_captcha',
                  #'require_login',
                  'status',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs): 
        super(CorpAppForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['confirmation_text'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['confirmation_text'].widget.mce_attrs['app_instance_id'] = 0

default_corpapp_inline_fields_list = get_corpapp_default_fields_list()
if default_corpapp_inline_fields_list:
    required_corpapp_inline_fields_list = [
                    str(field_d['field_name']) for field_d in \
                    default_corpapp_inline_fields_list  \
                    if field_d['required']]
else:
    required_corpapp_inline_fields_list = []


class CorpFieldForm(forms.ModelForm):
    instruction = forms.CharField(label=_('Instruction for User'),
                          max_length=500,
                          required=False,
                          widget=forms.Textarea(
                                attrs={'rows': '3'}))
    field_name = forms.CharField(label=(''), max_length=30,
                                 required=False,
                               widget=forms.HiddenInput())

    class Meta:
        model = CorpField
        fields = (
                  'label',
                  'field_name',
                  #'object_type',
                  'field_type',
                  'size',
                  'choices',
                  'field_layout',
                  'required',
                  'visible',
                  'no_duplicates',
                  'instruction',
                  'default_value',
                  'admin_only',
                  'css_class',
                  'position'
                  )

    def __init__(self, *args, **kwargs):
        super(CorpFieldForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if instance.field_name in required_corpapp_inline_fields_list \
            and instance.required:
                self.fields['required'].widget.attrs['disabled'] = "disabled"
                self.fields['visible'].widget.attrs['disabled'] = "disabled"
            if instance.field_name == 'name':
                self.fields['no_duplicates'].widget.attrs['disabled'] = "disabled"

    def clean_required(self):
        if self.instance.field_name in required_corpapp_inline_fields_list \
         and self.instance.required:
            return self.instance.required
        return self.cleaned_data['required']

    def clean_visible(self):
        if self.instance.field_name in required_corpapp_inline_fields_list \
         and self.instance.visible:
            return self.instance.visible
        return self.cleaned_data['visible']

    def clean_no_duplicates(self):
        if self.instance.field_name == 'name' and self.instance.no_duplicates:
            return self.instance.no_duplicates
        return self.cleaned_data['no_duplicates']


class CorpMembForm(forms.ModelForm):
    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'),
                 ('pending', 'Pending'),
                 ('paid - pending approval', 'Paid - Pending Approval'),
                 ('admin hold', 'Admin Hold'),
                 ('inactive', 'Inactive'),
                 ('expired', 'Expired'),))
    join_dt = SplitDateTimeField(label=_('Join Date/Time'),
        initial=datetime.now())
    expiration_dt = SplitDateTimeField(
                       label=_('Expiration Date/Time'),
                       required=False,
                       help_text='Not specified = Never expires')

    class Meta:
        model = CorporateMembership
        exclude = ('corp_app', 'guid', 'renewal', 'invoice',
                   'renew_dt', 'secret_code',
                   'approved', 'approved_denied_dt',
                   'approved_denied_user',
                   'creator_username',
                   'owner', 'owner_username',
                   'anonymous_creator')

    def __init__(self, corp_app, field_objs, *args, **kwargs):
        """
            Dynamically build the form fields.
        """
        self.corp_app = corp_app
        self.field_objs = field_objs
        super(CorpMembForm, self).__init__(*args, **kwargs)

        for field in field_objs:
            if field.field_type not in ['section_break', 'page_break']:
                if field.field_name:
                    field_key = field.field_name
                else:
                    field_key = "field_%s" % field.id

                # if field is display only, remove it from the form
                # for example, on the edit page, we
                # set corporate_membership_type
                # and payment_method as the display only fields
                if hasattr(field, 'display_only') and field.display_only:
                    del self.fields[field_key]
                else:
                    # get field class and set field initial
                    self.fields[field_key] = field.get_field_class()
                    if ((not field.field_name) \
                        or field.field_name == 'authorized_domains') \
                        and self.instance:
                        initial = field.get_value(self.instance)
                        if field.field_type in [
                            'MultipleChoiceField/django.forms.CheckboxSelectMultiple',
                            'MultipleChoiceField']:
                            if initial:
                                self.fields[field_key].initial = [
                                item.strip() for item in initial.split(',')]
                        else:
                            self.fields[field_key].initial = initial

        #self.fields['captcha'] = CaptchaField(label=_('Type the code below'))

    def clean_corporate_membership_type(self):
        if self.cleaned_data['corporate_membership_type']:
            return CorporateMembershipType.objects.get(
            pk=int(self.cleaned_data['corporate_membership_type']))
        return self.cleaned_data['corporate_membership_type']

    def clean_secret_code(self):
        secret_code = self.cleaned_data['secret_code']
        if secret_code:
            # check if this secret_code is available to ensure the uniqueness
            corp_membs = CorporateMembership.objects.filter(
                                secret_code=secret_code)
            if self.instance:
                corp_membs = corp_membs.exclude(id=self.instance.id)
            if corp_membs:
                raise forms.ValidationError(
            _("This secret code is already taken. Please use a different one.")
            )
        return self.cleaned_data['secret_code']

    def clean_payment_method(self):
        if self.cleaned_data['payment_method']:
            return PaymentMethod.objects.get(
                pk=int(self.cleaned_data['payment_method'])
                )
        return self.cleaned_data['payment_method']

    def save(self, user, **kwargs):
        """
            Create a CorporateMembership instance and related
            CorpFieldEntry instances for each form field.
        """
        corporate_membership = super(CorpMembForm, self).save(commit=False)
        corporate_membership.corp_app = self.corp_app
        creator_owner = user

        if not self.instance.pk:
            mode = 'add'
        else:
            mode = 'edit'

        if mode == 'add':
            anonymous_creator = kwargs.get('creator', None)
            if anonymous_creator:
                corporate_membership.anonymous_creator = anonymous_creator
            if not isinstance(creator_owner, User):
                # if anonymous is creating the corporate membership
                # temporarily use the first admin, the creator will be assigned 
                # back to the real user on approval
                tmp_user = User.objects.filter(is_staff=1, is_active=1)[0]
                creator_owner = tmp_user

            corporate_membership.creator = creator_owner
            corporate_membership.creator_username = creator_owner.username

            if not user.profile.is_superuser:
                corporate_membership.status = 1
                corporate_membership.status_detail = 'pending'
                corporate_membership.join_dt = datetime.now()

        corporate_membership.owner = creator_owner
        corporate_membership.owner_username = creator_owner.username

            # calculate the expiration dt
        corporate_membership.save()
        for field_obj in self.field_objs:
            if (not field_obj.field_name) and field_obj.field_type not in [
                'section_break', 'page_break']:
                field_key = "field_%s" % field_obj.id
                value = self.cleaned_data[field_key]
                if value and self.fields[field_key].widget.needs_multipart_form:
                    if not type(value) is unicode:
                        value = fs.save(join("forms",
                                        str(uuid4()),
                                        value.name),
                                        value)
                # if the value is a list convert is to a comma delimited string
                if isinstance(value, list):
                    value = ','.join(value)
                if not value:
                    value = ''

                if hasattr(field_obj, 'entry') and field_obj.entry:
                    field_obj.entry.value = value
                    field_obj.entry.save()
                else:
                    corporate_membership.fields.create(field_id=field_obj.id,
                                                       value=value)

        # update authorized domain if needed
        if self.corp_app.authentication_method == 'email':
            update_auth_domains(corporate_membership,
                                self.cleaned_data['authorized_domains'])

        return corporate_membership


class CreatorForm(forms.ModelForm):
    class Meta:
        model = Creator
        fields = ('first_name',
                'last_name',
                'email', )

    def __init__(self, *args, **kwargs):
        super(CreatorForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = CaptchaField(label=_('Type the code below'))


class CorpApproveForm(forms.Form):

    users = forms.ChoiceField(
        label='Assign creator/owner to this corporate membership',
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

        return user_set.items(), exact_match

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
    user_display = forms.CharField(max_length=100,
                        required=False,
                        help_text='type name, or username or email')

    class Meta:
        model = CorpMembershipRep
        fields = ('user_display',
                 'user',
                'is_dues_rep',
                'is_member_rep',)

    def __init__(self, corp_membership, *args, **kwargs):
        self.corp_membership = corp_membership
        super(CorpMembershipRepForm, self).__init__(*args, **kwargs)

        self.fields['user_display'].label = "Add a Representative"
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].error_messages['required'
                                ] = 'Please enter a valid user.'

    def clean_user(self):
        value = self.cleaned_data['user']
        try:
            rep = CorpMembershipRep.objects.get(
                corp_profile=self.corp_membership.corp_profile,
                user=value)
            raise forms.ValidationError(
                _("This user is already a representative."))
        except CorpMembershipRep.DoesNotExist:
            pass
        return value


class CorpMembRepForm(forms.ModelForm):
    user_display = forms.CharField(max_length=100,
                        required=False,
                        help_text='type name, or username or email')

    class Meta:
        model = CorporateMembershipRep
        fields = ('user_display',
                 'user',
                'is_dues_rep',
                'is_member_rep',)
#        exclude = (
#                  'corporate_membership',
#                  )

    def __init__(self, corp_memb, *args, **kwargs):
        self.corporate_membership = corp_memb
        super(CorpMembRepForm, self).__init__(*args, **kwargs)

        self.fields['user_display'].label = "Add a Representative"
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].error_messages['required'
                                ] = 'Please enter a valid user.'

    def clean_user(self):
        value = self.cleaned_data['user']
        try:
            rep = CorporateMembershipRep.objects.get(
                corporate_membership=self.corporate_membership,
                user=value)
            raise forms.ValidationError(
                _("This user is already a representative."))
        except CorporateMembershipRep.DoesNotExist:
            pass
        return value


class RosterSearchForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.HiddenInput())
    q = forms.CharField(max_length=100, required=False)


class CorpMembRenewForm(forms.ModelForm):
    members = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        choices=[],
                                        required=False)
    select_all_members = forms.BooleanField(widget=forms.CheckboxInput(),
                                            required=False)

    class Meta:
        model = CorpMembRenewEntry
        fields = ('corporate_membership_type',
                  'members',
                  'payment_method',
                  'select_all_members')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        corporate_membership = kwargs.pop('corporate_membership', None)

        super(CorpMembRenewForm, self).__init__(*args, **kwargs)

        self.fields['corporate_membership_type'].widget = forms.RadioSelect(
                    choices=get_corporate_membership_type_choices(user,
                    corporate_membership.corp_app,
                    renew=True))
        self.fields['corporate_membership_type'].empty_label = None
        self.fields['corporate_membership_type'
                ].initial = corporate_membership.corporate_membership_type.id

        members_choices = get_indiv_membs_choices(corporate_membership)
        self.fields['members'].choices = members_choices
        self.fields['members'].label = "Select the individual members you " + \
                                        "want to renew"
        if corporate_membership.corporate_membership_type.renewal_price == 0:
            self.fields['select_all_members'].initial = True 
            self.fields['members'].initial = [c[0] for c in members_choices]

        self.fields['payment_method'].widget = forms.RadioSelect(
                                    choices=get_payment_method_choices(
                                    user, corporate_membership.corp_app))
        self.fields['payment_method'].empty_label = None
        self.fields['payment_method'].initial = \
                corporate_membership.payment_method


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
                label=_('Corp Application'), queryset=CorpApp.objects.all())

            self.fields['update_option'] = forms.CharField(
                    widget=forms.RadioSelect(
                        choices=(('skip', 'Skip'),
                                 ('update', 'Update Blank Fields'),
                                ('override', 'Override All Fields'),)),
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
            choices = csv[0].keys()

            # make tuples; sort tuples (case-insensitive)
            choice_tuples = [(c, c) for c in csv[0].keys()]

            # insert blank option
            choice_tuples.insert(0, ('', ''))
            choice_tuples = sorted(choice_tuples, key=lambda c: c[0].lower())

            app_fields = CorpField.objects.filter(corp_app=corp_app)
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

            extra_fields = (('secret_code', 'Secret Code'),
                            ('join_dt', 'Join Date'),
                            ('renew_dt', 'Renew Date'),
                            ('expiration_dt', 'Expiration Date'),
                            ('approved', 'Approved'),
                            ('dues_rep', 'Dues Representative'),
                            ('status', 'Status'),
                            ('status_detail', 'Status Detail'))
            # corp_memb_field_names = [smart_str(field.name)
            # for field in CorporateMembership._meta.fields]
            for key, label in extra_fields:
                if key not in self.fields.keys():
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

        if not csv.content_type in SUPPORTED_FILE_TYPES:
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


class ExportForm(forms.Form):
    corp_app = forms.ModelChoiceField(
                label=_('Corp Application'),
                queryset=CorpApp.objects.all())
    passcode = forms.CharField(label=_("Type Your Password"),
                               widget=forms.PasswordInput(render_value=False))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', '')
        super(ExportForm, self).__init__(*args, **kwargs)

    def clean_passcode(self):
        value = self.cleaned_data['passcode']

        if not self.user.check_password(value):
            raise forms.ValidationError(_("Invalid password."))
        return value
