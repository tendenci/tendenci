from os.path import splitext, basename, join
import codecs
from csv import reader

from django import forms
from django.contrib.auth.models import User
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from django.forms.models import BaseModelFormSet
from django.urls import reverse

from tendenci.apps.chapters.models import (Chapter, Officer,
                        ChapterMembershipType,
                        ChapterMembershipApp,
                        ChapterMembershipAppField,
                        CustomizedAppField,
                        ChapterMembership,
                        ChapterMembershipFile,
                        CustomizedType)
from tendenci.apps.user_groups.models import Group
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.files.validators import FileValidator
from tendenci.apps.base.fields import StateSelectField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.regions.models import Region
from tendenci.apps.base.fields import PriceField
from tendenci.apps.memberships.fields import TypeExpMethodField, NoticeTimeTypeField
from tendenci.apps.memberships.widgets import (
    CustomRadioSelect, TypeExpMethodWidget)
from tendenci.apps.payments.fields import PaymentMethodModelChoiceField
from tendenci.apps.emails.models import Email
from .fields import ChapterMembershipTypeModelChoiceField
from .models import Notice, ChapterMembershipImport
from .widgets import ChapterNoticeTimeTypeWidget
from .utils import get_notice_token_help_text, get_newsletter_group_queryset


type_exp_method_fields = (
    'period_type', 'period', 'period_unit', 'rolling_option',
    'rolling_option1_day', 'rolling_renew_option', 'rolling_renew_option1_day',
    'rolling_renew_option2_day', 'fixed_option', 'fixed_option1_day',
    'fixed_option1_month', 'fixed_option1_year', 'fixed_option2_day',
    'fixed_option2_month', 'fixed_option2_can_rollover',
    'fixed_option2_rollover_days'
)

type_exp_method_widgets = (
    forms.Select(),
    forms.TextInput(),
    forms.Select(),
    CustomRadioSelect(),
    forms.TextInput(),
    CustomRadioSelect(),
    forms.TextInput(),
    forms.TextInput(),
    CustomRadioSelect(),
    forms.Select(),
    forms.Select(),
    forms.Select(),
    forms.Select(),
    forms.Select(),
    forms.CheckboxInput(),
    forms.TextInput(),
)


def assign_search_fields(form, app_field_objs):
    for obj in app_field_objs:
        # either choice field or text field
        if obj.field_name and obj.field_type not in ['BooleanField']:
            if obj.choices and obj.field_type in ('ChoiceField',
                                  'ChoiceField/django.forms.RadioSelect',
                                  'MultipleChoiceField',
                                  'MultipleChoiceField/django.forms.CheckboxSelectMultiple',
                                  'CountrySelectField'):
                choices = [s.strip() for s in obj.choices.split(",")]
                form.fields[obj.field_name] = forms.MultipleChoiceField(label=obj.label,
                                                        required=False,
                                                        widget=forms.CheckboxSelectMultiple,
                                                        choices=list(zip(choices, choices)))
            else:
                form.fields[obj.field_name] = forms.CharField(label=obj.label, required=False)


class ChapterMemberSearchForm(FormControlWidgetMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        app_fields = kwargs.pop('app_fields')
        user = kwargs.pop('user')
        self.chapter = kwargs.pop('chapter')
        super(ChapterMemberSearchForm, self).__init__(*args, **kwargs)
        if not self.chapter:
            # chapter field
            chapter_choices = [(0, _('All'))]
            chapter_choices += [(c.id, c.title) for c in Chapter.objects.all().order_by('title')]
            self.fields['chapter'] = forms.IntegerField(
                                    required=False,
                                    label=_('Chapter'),
                                    widget = forms.widgets.Select(
                                    choices=chapter_choices))
        # membership_type field
        membership_type_choices = [(0, _('All'))]
        membership_type_choices += [(mt.id, mt.name) for mt in ChapterMembershipType.objects.filter(
                                        status_detail='active').order_by('name')]
        self.fields['membership_type'] = forms.IntegerField(
                                required=False,
                                label=_('Membership Type'),
                                widget = forms.widgets.Select(
                                choices=membership_type_choices))
        # payment_status
        self.fields['payment_status'] = forms.ChoiceField(
                    required=False,
                    choices=(('', _('All')),
                             ('paid', _('Paid')),
                             ('not_paid', _('Not Paid'))))
        # status_detail
        self.fields['status_detail'] = forms.ChoiceField(
                    required=False,
                    choices=(('', _('All')),
                            ('active', _('Active')),
                            ('pending', _('Pending')),
                            ('expired', _('Expired'))))
        assign_search_fields(self, app_fields)
        self.add_form_control_class()


class EmailChapterMemberForm(FormControlWidgetMixin, forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%;padding:5px 0;'}))
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label': Email._meta.app_label,
        'storme_model': Email._meta.model_name.lower()}),
        label=_('Email Content'),
        help_text=_("""Available tokens:
                    <ul><li>{{ first_name }}</li>
                    <li>{{ last_name }}</li>
                    <li>{{ chapter_name }}</li>
                    <li>{{ view_url }}</li>
                    <li>{{ edit_url }}</li>
                    <li>{{ site_url }}</li>
                    <li>{{ site_display_name }}</li></ul>"""))

    class Meta:
        model = Email
        fields = ('subject',
                  'body',
                  'sender_display',
                  'reply_to',)

    def __init__(self, *args, **kwargs):
        super(EmailChapterMemberForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0


class ChapterMembershipTypeForm(TendenciBaseForm):
    type_exp_method = TypeExpMethodField(label=_('Period Type'))
    description = forms.CharField(label=_('Notes'), max_length=500, required=False,
                               widget=forms.Textarea(attrs={'rows': '3'}))
    price = PriceField(decimal_places=2, help_text=_("Set 0 for free membership."))
    renewal_price = PriceField(decimal_places=2, required=False,
                                 help_text=_("Set 0 for free membership."))
    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')), ('inactive', _('Inactive')))
    )

    class Meta:
        model = ChapterMembershipType
        fields = (
                  #'app',
                  'name',
                  'price',
                  'description',
                  'type_exp_method',
                  'renewal_price',
                  'allow_renewal',
                  'renewal',
                  'never_expires',
                  'require_approval',
                  'require_payment_approval',
                  'admin_only',
                  'renewal_require_approval',
                  'renewal_period_start',
                  'renewal_period_end',
                  'expiration_grace_period',
                  'position',
                  'status',
                  'status_detail',
                  )

    def __init__(self, *args, **kwargs):
        super(ChapterMembershipTypeForm, self).__init__(*args, **kwargs)

        self.type_exp_method_fields = type_exp_method_fields

        initial_list = []
        if self.instance.pk:
            for field in self.type_exp_method_fields:
                field_value = getattr(self.instance, field)
                if field == 'fixed_option2_can_rollover' and (not field_value):
                    field_value = ''
                else:
                    if not field_value:
                        field_value = ''
                initial_list.append(str(field_value))
            self.fields['type_exp_method'].initial = ','.join(initial_list)

        else:
            self.fields['type_exp_method'].initial = "rolling,1,years,0,1,0,1,1,0,1,1,,1,1,,1"

        # a field position dictionary - so we can retrieve data later
        fields_pos_d = {}
        for i, field in enumerate(self.type_exp_method_fields):
            fields_pos_d[field] = (i, type_exp_method_widgets[i])

        self.fields['type_exp_method'].widget = TypeExpMethodWidget(attrs={'id': 'type_exp_method'},
                                                                    fields_pos_d=fields_pos_d)

    def clean(self):
        cleaned_data = super(ChapterMembershipTypeForm, self).clean()
        # Make sure Expiretion Grace Period <= Renewal Period End
        if 'expiration_grace_period' in self.cleaned_data \
            and 'renewal_period_end' in self.cleaned_data:
            expiration_grace_period = self.cleaned_data['expiration_grace_period']
            renewal_period_end = self.cleaned_data['renewal_period_end']
            if expiration_grace_period > renewal_period_end:
                raise forms.ValidationError(_("The Expiration Grace Period should be less than or equal to the Renewal Period End."))
        return cleaned_data


    def clean_expiration_grace_period(self):
        value = self.cleaned_data['expiration_grace_period']
        if value > 100:
            raise forms.ValidationError(_("This number should be less than 100 (days)."))
        return value

    def clean_type_exp_method(self):
        value = self.cleaned_data['type_exp_method']

        # if never expires is checked, no need to check further
        if self.cleaned_data['never_expires']:
            return value

        data_list = value.split(',')
        d = dict(zip(self.type_exp_method_fields, data_list))
        if d['period_type'] == 'rolling':
            if d['period']:
                try:
                    d['period'] = int(d['period'])
                except:
                    raise forms.ValidationError(_("Period must be a numeric number."))
            else:
                raise forms.ValidationError(_("Period is a required field."))
            try:
                d['rolling_option'] = int(d['rolling_option'])
            except:
                raise forms.ValidationError(_("Please select a expiration option for join."))
            if d['rolling_option'] not in [0, 1]:
                raise forms.ValidationError(_("Please select a expiration option for join."))
            if d['rolling_option'] == 1:
                try:
                    d['rolling_option1_day'] = int(d['rolling_option1_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in option 2 of Expires On must be a numeric number."))
            # renew expiration
            try:
                d['rolling_renew_option'] = int(d['rolling_renew_option'])
            except:
                raise forms.ValidationError(_("Please select a expiration option for renewal."))
            if d['rolling_renew_option'] not in [0, 1, 2]:
                raise forms.ValidationError(_("Please select a expiration option for renewal."))
            if d['rolling_renew_option'] == 1:
                try:
                    d['rolling_renew_option1_day'] = int(d['rolling_renew_option1_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in option 2 of Renew Expires On must be a numeric number."))
            if d['rolling_renew_option'] == 2:
                try:
                    d['rolling_renew_option2_day'] = int(d['rolling_renew_option2_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in option 3 of Renew Expires On must be a numeric number."))

        else:  # d['period_type'] == 'fixed'
            try:
                d['fixed_option'] = int(d['fixed_option'])
            except:
                raise forms.ValidationError(_("Please select an option for fixed period."))
            if d['fixed_option'] not in [0, 1]:
                raise forms.ValidationError(_("Please select an option for fixed period."))
            if d['fixed_option'] == 0:
                try:
                    d['fixed_option1_day'] = int(d['fixed_option1_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in the option 1 of Expires On must be a numeric number."))
            if d['fixed_option'] == 1:
                try:
                    d['fixed_option2_day'] = int(d['fixed_option2_day'])
                except:
                    raise forms.ValidationError(_("The day(s) field in the option 2 of Expires On must be a numeric number."))

            if 'fixed_option2_can_rollover' in d:
                try:
                    d['fixed_option2_rollover_days'] = int(d['fixed_option2_rollover_days'])
                except:
                    raise forms.ValidationError(_("The grace period day(s) for optoin 2 must be a numeric number."))

        return value


class ChapterMembershipAppPreForm(FormControlWidgetMixin, forms.Form):
    chapter_id = forms.ChoiceField(label=_('Select a Chapter'))

    def __init__(self, *args, **kwargs):
        super(ChapterMembershipAppPreForm, self).__init__(*args, **kwargs)
        chapters_list = [(0, 'SELECT ONE')]
        chapters = Chapter.objects.filter(status_detail='active').order_by('title')
        for chapter in chapters:
            chapters_list.append((chapter.id, chapter.title))
        self.fields['chapter_id'].choices = chapters_list


class ChapterMembershipAppForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': ChapterMembershipApp._meta.app_label,
        'storme_model': ChapterMembershipApp._meta.model_name.lower()}))

    confirmation_text = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': ChapterMembershipApp._meta.app_label,
        'storme_model': ChapterMembershipApp._meta.model_name.lower()}))

    status_detail = forms.ChoiceField(
        choices=(
            ('draft', _('Draft')),
            ('published', _('Published')),
            ('inactive', _('Inactive'))
        ),
        initial='published'
    )

    class Meta:
        model = ChapterMembershipApp
        fields = (
            'name',
            'slug',
            'description',
            'confirmation_text',
            'renewal_description',
            'renewal_confirmation_text',
            'notes',
            'membership_types',
            'payment_methods',
            'use_captcha',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status_detail',
            )

    def __init__(self, *args, **kwargs):
        super(ChapterMembershipAppForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs[
                            'app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0

        if self.instance.pk:
            self.fields['confirmation_text'].widget.mce_attrs[
                            'app_instance_id'] = self.instance.pk
        else:
            self.fields['confirmation_text'].widget.mce_attrs[
                                    'app_instance_id'] = 0


class ChapterMembershipAppFieldAdminForm(forms.ModelForm):
    class Meta:
        model = ChapterMembershipAppField
        fields = (
                'membership_app',
                'label',
                'field_name',
                'required',
                'display',
                'customizable',
                'admin_only',
                'field_type',
                'description',
                'help_text',
                'choices',
                'default_value',
                'css_class'
                  )

    def __init__(self, *args, **kwargs):
        super(ChapterMembershipAppFieldAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            if not self.instance.field_name:
                self.fields['field_type'].choices = ChapterMembershipAppField.FIELD_TYPE_CHOICES2
            else:
                self.fields['field_type'].choices = ChapterMembershipAppField.FIELD_TYPE_CHOICES1

    def save(self, *args, **kwargs):
        self.instance = super(ChapterMembershipAppFieldAdminForm, self).save(*args, **kwargs)
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


class AppFieldCustomForm(FormControlWidgetMixin, forms.ModelForm):
    choices = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':'1'}),
                              help_text=_("Comma separated options where applicable"))
    class Meta:
        model = ChapterMembershipAppField

        fields = (
            'field_name',
            'label',
            'choices',
            'help_text',
            'default_value',
        )

        fieldsets = [(_('Application Field'), {
          'fields': ['field_name',
                    'label',
                    'choices',
                    'help_text',
                    'default_value',
                    ],
          'legend': '',
          'classes': ['boxy-grey'],
          })
        ]

    def __init__(self, *args, chapter, **kwargs):
        self.chapter = chapter
        super(AppFieldCustomForm, self).__init__(*args, **kwargs)
        [self.cfield] = self.chapter.customizedappfield_set.filter(
            app_field__id=self.instance.id)[:1] or [None]
        if self.cfield:
            # override with the value in CustomizedAppField (saved previously, if any)
            self.initial['choices'] = self.cfield.choices
            self.initial['help_text'] = self.cfield.help_text
            self.initial['default_value'] = self.cfield.default_value

        # set these fields as readyonly as chapter leaders should not change them
        readonly_fields = ['field_name', 'label',]
        for field in readonly_fields:
            self.fields[field].widget.attrs['readonly'] = True

        if 'ChoiceField' not in self.instance.field_type:
            del self.fields['choices']

    def save(self, commit=True):
        if not self.cfield:
            self.cfield = CustomizedAppField(app_field=self.instance,
                                        chapter=self.chapter)
        self.cfield.choices = self.cleaned_data.get('choices', '')
        self.cfield.help_text = self.cleaned_data['help_text']
        self.cfield.default_value = self.cleaned_data['default_value']
        self.cfield.save()
        return self.cfield


class CustomMembershipTypeForm(FormControlWidgetMixin, forms.ModelForm):
    price = PriceField(decimal_places=2, help_text=_("Set 0 for free membership."))
    renewal_price = PriceField(decimal_places=2, required=False,
                                 help_text=_("Set 0 for free membership."))
    class Meta:
        model = ChapterMembershipType

        fields = (
            'name',
            'price',
            'renewal_price',
        )

    def __init__(self, *args, chapter, **kwargs):
        self.chapter = chapter
        super(CustomMembershipTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = _('Membership Type')
        [self.ctype] = self.chapter.customizedtype_set.filter(
            membership_type__id=self.instance.id)[:1] or [None]
        if self.ctype:
            # override with the value in CustomizedAppField (saved previously, if any)
            self.initial['price'] = self.ctype.price
            self.initial['renewal_price'] = self.ctype.renewal_price

        # set membership type name as readyonly as chapter leaders should not change it
        readonly_fields = ['name',]
        for field in readonly_fields:
            self.fields[field].widget.attrs['readonly'] = True

    def save(self, commit=True):
        if not self.ctype:
            self.ctype = CustomizedType(membership_type=self.instance,
                                        chapter=self.chapter)
        self.ctype.price = self.cleaned_data['price']
        self.ctype.renewal_price = self.cleaned_data['renewal_price']
        self.ctype.save()
        return self.ctype


class AppFieldBaseFormSet(BaseModelFormSet):
    def save(self, commit=True):
        return self.save_existing_objects(commit)


class MembershipTypeBaseFormSet(AppFieldBaseFormSet):
    def save(self, commit=True):
        return self.save_existing_objects(commit)


class ChapterMembershipForm(FormControlWidgetMixin, forms.ModelForm):
    STATUS_DETAIL_CHOICES = (
            ('active', _('Active')),
            ('pending', _('Pending')),
            ('admin_hold', _('Admin Hold')),
            ('inactive', _('Inactive')),
            ('expired', _('Expired')),
            ('archive', _('Archive')),
    )
    payment_method = PaymentMethodModelChoiceField(
        label=_('Payment Method'),
        widget=forms.RadioSelect(),
        empty_label=None,
        queryset=None
    )
    membership_type = ChapterMembershipTypeModelChoiceField(
        label=_('Membership Type'),
        empty_label=None,
        queryset=None
    )

    class Meta:
        model = ChapterMembership
        fields = "__all__"

    def __init__(self, app_field_objs, chapter, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        self.is_renewal = kwargs.pop('is_renewal', False)
        self.renew_from_id = kwargs.pop('renew_from_id', None)
        self.edit_mode = kwargs.pop('edit_mode', False)
        self.app = kwargs.pop('app')
        self.chapter = chapter
        self.app_field_objs = app_field_objs
        super(ChapterMembershipForm, self).__init__(*args, **kwargs)
        
        from tendenci.apps.memberships.forms import assign_fields
        assign_fields(self, self.app_field_objs)
        
        # handle file upload on edit
        if self.edit_mode:
            for field_obj in  self.app_field_objs:
                if field_obj.field_type == 'FileField':
                    field_key = field_obj.field_name
                    field_current_value = getattr(self.instance, field_key, None)
                    if field_current_value:
                        cm_file = (ChapterMembershipFile.objects.filter(id=field_current_value)[:1] or [None])[0]
                        if cm_file:
                            file_name = cm_file.basename()
                            file_url = reverse('chapters.cm_file_display', args=[cm_file.id])
                            if not self.fields[field_key].required:
                                self.fields[field_key].help_text = f"""
                                <input name="remove_{field_key}" id="id_remove_{field_key}" type="checkbox"/>
                                Remove current file: <a target="_blank" href="{file_url}">{file_name}</a>
                                """
                            else:
                                self.fields[field_key].help_text = f"""
                                Current file: <a target="_blank" href="{file_url}">{file_name}</a>
                                """
                                self.fields[field_key].required = False

        # membership types query set
        self.fields['membership_type'].renew_mode = self.is_renewal
        self.fields['membership_type'].chapter = self.chapter
        membership_types_qs = self.app.membership_types.all()
        if not self.request_user.is_superuser:
            membership_types_qs = membership_types_qs.filter(admin_only=False)
        membership_types_qs = membership_types_qs.order_by('position')
        if not self.is_renewal and not self.edit_mode:
            membership_types_qs = membership_types_qs.exclude(renewal=True)
        self.fields['membership_type'].queryset = membership_types_qs
        self.fields['membership_type'].widget = forms.widgets.RadioSelect(
                choices=self.fields['membership_type'].choices,
            )

        if 'renew_dt' in self.fields:
            if not (self.instance and self.instance.renew_dt):
                del self.fields['renew_dt']
            else:
                self.fields['renew_dt'].widget = forms.TextInput(attrs={'readonly': 'readonly'})

        if self.edit_mode:
            self.fields['membership_type'].required = False
            self.fields['membership_type'].widget.attrs['disabled'] = 'disabled'

        if 'status_detail' in self.fields:
            self.fields['status_detail'].widget = forms.widgets.Select(
                        choices=self.STATUS_DETAIL_CHOICES)

        require_payment = True
        if self.edit_mode:
            self.fields['payment_method'].required = False
            self.fields['payment_method'].widget.attrs['disabled'] = 'disabled'

        if not require_payment:
            if 'payment_method' in self.fields:
                del self.fields['payment_method']
        else:
            payment_method_qs = self.app.payment_methods.all()
            if not self.request_user.is_superuser:
                payment_method_qs = payment_method_qs.exclude(admin_only=True)
            self.fields['payment_method'].queryset = payment_method_qs
            if payment_method_qs.count() == 1:
                self.fields['payment_method'].initial = payment_method_qs[0]

        self.field_names = [name for name in self.fields]
        self.add_form_control_class()

    def clean_membership_type(self):
        if self.edit_mode:
            return self.instance.membership_type
        else:
            return self.cleaned_data['membership_type']

    def clean_payment_method(self):
        if self.edit_mode:
            return self.instance.payment_method
        else:
            return self.cleaned_data['payment_method']

    def clean(self):
        cleaned_data = super(ChapterMembershipForm, self).clean()
        if not (self.is_renewal or self.edit_mode):
            # check if a chapter membership already exists
            if ChapterMembership.objects.filter(user=self.request_user,
                                        chapter=self.chapter).exclude(
                                            status_detail='archive'):
                raise forms.ValidationError(_('You have already signed up for this chapter.'))
        return cleaned_data

    def save(self):
        chapter_membership = super(ChapterMembershipForm, self).save(commit=False)

        if not self.edit_mode:
            chapter_membership.entity = self.chapter.entity
            chapter_membership.user = self.request_user
            chapter_membership.renewal = self.is_renewal
            if self.renew_from_id:
                chapter_membership.renew_from_id = self.renew_from_id
            chapter_membership.app = self.app
            chapter_membership.chapter = self.chapter
            chapter_membership.save()
    
            chapter_membership.set_member_number()
            chapter_membership.save()
        else:
            chapter_membership.save()
            
        for field_obj in  self.app_field_objs:
            field_key = field_obj.field_name
            
            if field_key in self.fields and self.fields[field_key].widget.needs_multipart_form:
                
                # handle file upload
                # save file to the value field of ChapterMembershipFile
                # and assign the id of ChapterMembershipFile to the value of the field
                value = self.cleaned_data[field_key]
                if self.instance and getattr(self.instance, field_key) == value:
                    # on edit or renew
                    remove_value = self.request.POST.get(f"remove_{field_key}", False)
                    cm_file = (ChapterMembershipFile.objects.filter(
                                field_id=field_obj.id,
                                chapter_membership=chapter_membership)[:1] or [None])[0]
                    if remove_value and cm_file:
                        if not field_obj.required:
                            cm_file.delete()
                            setattr(chapter_membership, field_key, '')
                            chapter_membership.save()
                elif value:
                    cm_file, created = ChapterMembershipFile.objects.get_or_create(
                                    field_id=field_obj.id,
                                    chapter_membership=chapter_membership)
                    if cm_file.file:
                        cm_file.file.delete()
                    cm_file.file = value
                    cm_file.save()
                    setattr(chapter_membership, field_key, cm_file.id)
                    chapter_membership.save()

        return chapter_membership


class NoticeForm(forms.ModelForm):
    notice_time_type = NoticeTimeTypeField(label=_('When to Send'),
                                          widget=ChapterNoticeTimeTypeWidget)
    email_content = forms.CharField(widget=TinyMCE(attrs={'style': 'width:70%'},
        mce_attrs={'storme_app_label': Notice._meta.app_label,
        'storme_model': Notice._meta.model_name.lower()}), help_text=_("Click here to view available tokens"))

    class Meta:
        model = Notice
        fields = (
                  'notice_name',
                  'notice_time_type',
                  'chapter',
                  'membership_type',
                  'subject',
                  'content_type',
                  'sender',
                  'sender_display',
                  'email_content',
                  'status',
                  'status_detail',
                  )

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
        else:
            initial_list = ['0', 'attimeof', 'apply']

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
    #newsletter_group = forms.ModelChoiceField(required=False, queryset=None)


    class Meta:
        model = Chapter
        fields = (
        'title',
        'slug',
        'newsletter_group',
        'region',
        'state',
        'county',
        'mission',
        'content',
        'notes',
        'sponsors',
        'photo_upload',
        'contact_name',
        'contact_email',
        'join_link',
        'tags',
        'external_payment_link',
        'allow_anonymous_view',
        'syndicate',
        'status_detail',
        )
        fieldsets = [('Chapter Information', {
                      'fields': ['title',
                                 'slug',
                                 'newsletter_group',
                                 'region',
                                 'state',
                                 'county',
                                 'mission',
                                 'content',
                                 'notes',
                                 'sponsors',
                                 'photo_upload',
                                 'contact_name',
                                 'contact_email',
                                 'join_link',
                                 'tags',
                                 'external_payment_link',
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

        # newsletter group
        self.fields['newsletter_group'].queryset = get_newsletter_group_queryset()

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
        'newsletter_group',
        'region',
        'state',
        'county',
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
        self.fields['newsletter_group'].queryset = get_newsletter_group_queryset()


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
        self.field_order = ['user', 'position', 'phone', 'email', 'expire_dt']
        super(OfficerForm, self).__init__(*args, **kwargs)
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
    county = forms.CharField(required=False, max_length=50,)


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
        if Chapter.objects.exclude(county='').exists():
            self.fields['county'].widget.attrs.update({'placeholder': _('County')})
        else:
            del self.fields['county']


class ChapterMembershipUploadForm(FormControlWidgetMixin, forms.ModelForm):
    KEY_CHOICES = (
               ('username,membership_type_id,chapter_id', _('username and membership_type_id and chapter_id')),
               )
    key = forms.ChoiceField(label="Identify duplicates by", required=True,
                            choices=KEY_CHOICES)
    class Meta:
        model = ChapterMembershipImport
        fields = ('override', 'key', 'upload_file',)

    def __init__(self, *args, **kwargs):
        self.chapter = kwargs.pop('chapter')
        super(ChapterMembershipUploadForm, self).__init__(*args, **kwargs)
        self.fields['upload_file'].validators = [FileValidator(allowed_extensions=['.csv'], allowed_mimetypes=['text/csv', 'text/plain'])]
        if self.chapter:
            self.fields['key'].choices = (('username,membership_type_id', _('username and membership_type_id')),)

    def clean(self):
        cleaned_data = super(ChapterMembershipUploadForm, self).clean()

        # check for valid content in the csv file
        if 'upload_file' not in cleaned_data:
            return cleaned_data

        upload_file = cleaned_data['upload_file']
        csv_reader = reader(codecs.iterdecode(upload_file, 'utf-8'))
        header_row = next(csv_reader)
        if not header_row:
            raise forms.ValidationError(_('There is no data in the spreadsheet.'))

        first_row = None
        if header_row != None:
            for row in csv_reader:
                first_row = row
                break
        upload_file.seek(0)
        if not first_row:
            raise forms.ValidationError(_('There is no data rows in the spreadsheet.'))

        # check for valid key
        key = cleaned_data['key']
        

        key_list = [k for k in key.split(',')]
        missing_columns = [item for item in key_list if item not in header_row]
        if missing_columns:
            raise forms.ValidationError(_(
                        """
                        Field(s) "%(fields)s" used to identify the duplicates
                        should be included in the .csv file.
                        """ % {'fields' : ', '.join(missing_columns)}))

        return cleaned_data

