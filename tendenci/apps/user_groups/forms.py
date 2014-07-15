from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.forms.util import ErrorList

from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.user_groups.utils import member_choices
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.apps.entities.models import Entity
from tendenci.core.site_settings.utils import get_setting


SEARCH_CATEGORIES = (
    ('', '-- SELECT ONE --' ),
    ('creator__id', 'Creator Userid #'),
    ('creator__username', 'Creator Username'),

    ('guid', 'User Group GUID'),
    ('id', 'User Group ID #'),
    ('label__icontains', 'User Group Label'),
    ('name__icontains', 'User Group Name'),

    ('owner__id', 'Owner Userid #'),
    ('owner__username', 'Owner Username'),

)


class GroupSearchForm(forms.Form):
    search_category = forms.ChoiceField(choices=SEARCH_CATEGORIES, required=False)
    q = forms.CharField(required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        q = self.cleaned_data.get('q', None)
        cat = self.cleaned_data.get('search_category', None)

        if q is None or q == "":
            return cleaned_data

        if cat is None or cat == "" :
            self._errors['search_category'] =  ErrorList(['Select a category'])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                x = int(q)
            except ValueError:
                self._errors['q'] = ErrorList(['Must be an integer'])

        return cleaned_data


class GroupAdminForm(TendenciBaseForm):
    email_recipient = forms.CharField(label="Recipient Email",
                                      required=False, max_length=100,
        help_text='Recipient email(s), comma delimited')
    show_as_option = forms.BooleanField(initial=1, label="Show Option",
        help_text='Display this user group as an option to logged-in users.',
        required=False)

    class Meta:
        model = Group
        fields = ('name',
          'label',
          'entity',
          'type',
          'email_recipient',
          'show_as_option',
          'sync_newsletters',
          'allow_self_add',
          'allow_self_remove',
          'description',
          'auto_respond',
          'auto_respond_priority',
          'notes',
          'allow_anonymous_view',
          'members',
          'permissions',
          'user_perms',
          'status_detail',
          )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # filter out the unwanted permissions,
        content_types = ContentType.objects.exclude(app_label='auth')
        self.fields['permissions'].queryset = Permission.objects.filter(
                                        content_type__in=content_types)
        entity = Entity.objects.first()
        self.fields['entity'].initial = entity
        self.fields['entity'].required = True
        self.fields['entity'].empty_label = None


class GroupForm(TendenciBaseForm):
    STATUS_CHOICES = (('active', 'Active'), ('inactive', 'Inactive'),)
    email_recipient = forms.CharField(label="Recipient Email",
                                      required=False, max_length=100,
        help_text='Recipient email(s), comma delimited')
    show_as_option = forms.BooleanField(initial=1, label="Show Option",
        help_text='Display this group as an option to logged-in users.',
        required=False)
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = Group
        fields = ('name',
                  'label',
                  'entity',
                  'type',
                  'email_recipient',
                  'show_as_option',
                  'sync_newsletters',
                  'allow_self_add',
                  'allow_self_remove',
                  'description',
                  'auto_respond',
                  'auto_respond_priority',
                  'notes',
                  'allow_anonymous_view',
                  'user_perms',
                  'status_detail',
                  )
        exclude = ('members', 'group_perms')

        fieldsets = [('Group Information', {
                      'fields': ['name',
                                 'label',
                                 'entity',
                                 'email_recipient',
                                 'show_as_option',
                                 'sync_newsletters',
                                 'allow_self_add',
                                 'allow_self_remove',
                                 'description'
                                 'auto_respond',
                                 'auto_respond_priority'
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')
        entity = Entity.objects.first()
        self.fields['entity'].initial = entity
        self.fields['entity'].required = True
        self.fields['entity'].empty_label = None


class GroupMembershipForm(forms.ModelForm):
    def __init__(self, group=None, user_id=None, *args, **kwargs):
        super(GroupMembershipForm, self).__init__(*args, **kwargs)
        if group:
            # exclude those already joined
            exclude_userid = [user.id for user in group.members.all()]
            self.fields['member'].queryset = User.objects.filter(is_active=1
                                        ).exclude(id__in=exclude_userid)
        else:
            self.fields['member'].queryset = User.objects.filter(is_active=1)
        if user_id:
            del self.fields["member"]

    class Meta:
        model = GroupMembership
        exclude = ('group',)


class GroupMembershipBulkForm(forms.Form):
    def __init__(self, group, *args, **kwargs):
        member_label = kwargs.pop('member_label', 'username')
        super(GroupMembershipBulkForm, self).__init__(*args, **kwargs)
        self.fields['members'].initial = group.members.all()
        self.fields['members'].choices = member_choices(group, member_label)

    members = forms.ModelMultipleChoiceField(
                    queryset=User.objects.filter(is_active=1),
                    required=False)
    role = forms.CharField(required=False, max_length=255)
    status = forms.BooleanField(required=False, initial=True)
    status_detail = forms.ChoiceField(choices=(('active', 'Active'),
                                               ('inactive', 'Inactive'),),
                                      initial='active')


class GroupPermissionForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('permissions',)

    def __init__(self, *args, **kwargs):
        super(GroupPermissionForm, self).__init__(*args, **kwargs)
        # filter out the unwanted permissions,
        # only display the permissions for the apps in APPS
        content_types = ContentType.objects.exclude(app_label='auth')

        self.fields['permissions'].queryset = Permission.objects.filter(
                                        content_type__in=content_types)


class GroupMembershipEditForm(forms.ModelForm):
    class Meta:
        model = GroupMembership
        fields = ('role', 'status', 'status_detail')


class MessageForm(forms.Form):
  """Handles Message Form"""
  to_addr = forms.CharField(label=u'To')
  from_addr = forms.CharField(label=u'From')
  subject = forms.CharField()
  body = forms.CharField(widget=forms.Textarea)
  is_test = forms.BooleanField(label=u'Send test email to me only', required=False, initial=True)

  def __init__(self, *args, **kwargs):
    from django.template.defaultfilters import pluralize
    request = kwargs.pop('request')
    num_members = kwargs.pop('num_members')
    super(MessageForm, self).__init__(*args, **kwargs)

    self.fields['to_addr'].initial = 'All %s member%s' % (num_members, pluralize(num_members))
    self.fields['to_addr'].widget.attrs['readonly'] = True

    self.fields['from_addr'].initial = get_setting('site', 'global', 'siteemailnoreplyaddress')
    self.fields['from_addr'].widget.attrs['readonly'] = True










