from itertools import groupby

from django.forms import MultipleChoiceField, CheckboxInput
from django.contrib.contenttypes.models import ContentType
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.apps.user_groups.models import Group


user_perm_options = {
    'label': _('User Permissions'),
    'help_text': _('Select view/change to allow all authenticated users to view or change'),
    'required': False,
    'choices': (('allow_user_view', _('User')), ('allow_user_edit', _('User')))
}

member_perm_options = {
    'label': _('Member Permissions'),
    'help_text': _('Select view/change to allow all members to view or change'),
    'required': False,
    'choices': (('allow_member_view', _('Member')), ('allow_member_edit', _('Member')))
}


def group_choices():
    # groups = Group.objects.filter(status=1, status_detail='active', use_for_membership=0).order_by('name')
    groups = Group.objects.filter(status=True, status_detail='active').order_by('name')
    choices = []
    if groups:
        for g in groups:
            choices.append(('%s_%s' % ('view', g.pk), g.name))
            choices.append(('%s_%s' % ('change', g.pk), g.name))
        return tuple(choices)
    return choices


group_perm_options = {
    'label': _('Group Permissions'),
    'help_text': _('Groups who have view/change permissions'),
    'required': False,
}


def user_perm_bits(instance):
    """
    Returns a list of user permissions on a model instance.
    """
    user_bits = []
    if hasattr(instance, 'allow_user_view') and hasattr(instance, 'allow_user_edit'):
        if instance.allow_user_view:
            user_bits.append('allow_user_view')
        if instance.allow_user_edit:
            user_bits.append('allow_user_edit')
    return user_bits


def member_perm_bits(instance):
    """
    Returns a list of member permissions on a model instance.
    """
    member_bits = []
    if hasattr(instance, 'allow_member_view') and hasattr(instance, 'allow_member_edit'):
        if instance.allow_member_view:
            member_bits.append('allow_member_view')
        if instance.allow_member_edit:
            member_bits.append('allow_member_edit')
    return member_bits


def groups_with_perms(instance):
    """
        Return a list of groups that have permissions
        on a model instance.
    """
    group_perms = []
    content_type = ContentType.objects.get_for_model(instance)
    filters = {
        'group__in': Group.objects.filter(status=True, status_detail='active'),
        'content_type': content_type,
        'object_id': instance.pk
    }
    object_perms = ObjectPermission.objects.filter(**filters)
    for perm in object_perms:
        if 'view' in perm.codename:
            group_perms.append('%s_%s' % ('view', perm.group.pk))
        if 'change' in perm.codename:
            group_perms.append('%s_%s' % ('change', perm.group.pk))

    return list(set(group_perms))


def has_groups_perms(instance):
    """
        Return a boolean of whether or not the instance
        has group permissions
    """
    content_type = ContentType.objects.get_for_model(instance)
    filters = {
        'group__in': Group.objects.filter(status=True, status_detail='active'),
        'content_type': content_type,
        'object_id': instance.pk
    }
    object_perms = ObjectPermission.objects.filter(**filters)

    return object_perms


class UserPermissionWidget(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)

        # set up output attributes
        html = u''
        table_rows = u''

        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])

        # setup the id attr
        if has_id:
            id = attrs['id']
        else:
            id = u''

        # set up the html for output
        html += """
            <table border="0" cellspacing="0" cellpadding="0" id="%(id)s">
            <tr>
                <th class="header-col-1">&nbsp;</th>
                <th class="header-col-2">View</th>
                <th class="header-col-3">Change</th>
            </tr>
            %(table_rows)s
            </table>
        """
        for i, (user_label, user_perm) in enumerate(groupby(self.choices, lambda x: x[1])):
            view_input_value = force_unicode(user_perm.next()[0])
            change_input_value = force_unicode(user_perm.next()[0])

            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))

            cb_view = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            cb_change = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            rendered_cb_view = cb_view.render(name, view_input_value)
            rendered_cb_change = cb_change.render(name, change_input_value)

            if (i % 2) == 0:
                tr_class = ' class="alt" '
            else:
                tr_class = ''

            table_rows += """
                <tr%(tr_class)s>
                    <td>%(user_label)s</td>
                    <td>%(view_checkbox)s</td>
                    <td>%(change_checkbox)s</td>
                </tr>
            """ % {'tr_class': tr_class,
                   'user_label': conditional_escape(force_unicode(user_label)),
                   'view_checkbox': rendered_cb_view,
                   'change_checkbox': rendered_cb_change
                  }

        html = html % {
                'id': id,
                'table_rows': table_rows
                }
        return mark_safe(html)


class UserPermissionField(MultipleChoiceField):
    """
    Inherits from MultipleChoiceField and
    sets some default meta data
    """
    widget = UserPermissionWidget

    def __init__(self, *args, **kwargs):
        try:
            kwargs.update(user_perm_options)
        except:
            # in database setup we can't get database entries
            # when they do not exist
            pass
        super(UserPermissionField, self).__init__(*args, **kwargs)


class MemberPermissionWidget(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)

        # set up output attributes
        html = u''
        table_rows = u''

        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])

        # setup the id attr
        if has_id:
            id = attrs['id']
        else:
            id = u''

        # set up the html for output
        html += """
            <table border="0" cellspacing="0" cellpadding="0" id="%(id)s">
            <tr>
                <th class="header-col-1">&nbsp;</th>
                <th class="header-col-2">View</th>
                <th class="header-col-3">Change</th>
            </tr>
            %(table_rows)s
            </table>
        """
        for i, (member_label, member_perm) in enumerate(groupby(self.choices, lambda x: x[1])):
            view_input_value = force_unicode(member_perm.next()[0])
            change_input_value = force_unicode(member_perm.next()[0])

            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))

            cb_view = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            cb_change = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            rendered_cb_view = cb_view.render(name, view_input_value)
            rendered_cb_change = cb_change.render(name, change_input_value)

            if (i % 2) == 0:
                tr_class = ' class="alt" '
            else:
                tr_class = ''

            table_rows += """
                <tr%(tr_class)s>
                    <td>%(member_label)s</td>
                    <td>%(view_checkbox)s</td>
                    <td>%(change_checkbox)s</td>
                </tr>
            """ % {'tr_class': tr_class,
                   'member_label': conditional_escape(force_unicode(member_label)),
                   'view_checkbox': rendered_cb_view,
                   'change_checkbox': rendered_cb_change
                  }

        html = html % {
                'id': id,
                'table_rows': table_rows
                }
        return mark_safe(html)


class MemberPermissionField(MultipleChoiceField):
    """
    Inherits from MultipleChoiceField and
    sets some default meta data
    """
    widget = MemberPermissionWidget

    def __init__(self, *args, **kwargs):
        try:
            kwargs.update(member_perm_options)
        except:
            # in database setup we can't get database entries
            # when they do not exist
            pass
        super(MemberPermissionField, self).__init__(*args, **kwargs)


class GroupPermissionWidget(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)

        # set up output attributes
        html = u''
        table_rows = u''

        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])

        # setup the id attr
        if has_id:
            id = attrs['id']
        else:
            id = u''

        # set up the html for output
        html += """
            <table border="0" cellspacing="0" cellpadding="0" id="%(id)s">
            <tr>
                <th class="header-col-1">&nbsp;</th>
                <th class="header-col-2">View</th>
                <th class="header-col-3">Change</th>
            </tr>
            %(table_rows)s
            </table>
        """
        for i, (group_name, group) in enumerate(groupby(self.choices, lambda x: x[1])):
            view_input_value = force_unicode(group.next()[0])
            change_input_value = force_unicode(group.next()[0])

            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))

            cb_view = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            cb_change = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            rendered_cb_view = cb_view.render(name, view_input_value)
            rendered_cb_change = cb_change.render(name, change_input_value)

            if (i % 2) == 0:
                tr_class = ' class="alt" '
            else:
                tr_class = ''

            table_rows += """
                <tr%(tr_class)s>
                    <td>%(group_name)s</td>
                    <td>%(view_checkbox)s</td>
                    <td>%(change_checkbox)s</td>
                </tr>
            """ % {'tr_class': tr_class,
                   'group_name': conditional_escape(force_unicode(group_name)),
                   'view_checkbox': rendered_cb_view,
                   'change_checkbox': rendered_cb_change
                  }

        html = html % {
                'id': id,
                'table_rows': table_rows
                }
        return mark_safe(html)


class GroupPermissionField(MultipleChoiceField):
    """
    Inherits from MultipleChoiceField and
    sets some default meta data
    """
    widget = GroupPermissionWidget

    def __init__(self, *args, **kwargs):
        kwargs.update(group_perm_options)
        try:
            kwargs.update({'choices': group_choices()})
        except:
            # in database setup we can't get database entries
            # when they do not exist
            pass
        super(GroupPermissionField, self).__init__(*args, **kwargs)
