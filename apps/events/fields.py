from itertools import groupby
from django.forms import MultipleChoiceField, CheckboxInput
from django.contrib.contenttypes.models import ContentType
from django.forms.widgets import CheckboxSelectMultiple

from django.forms import DateTimeField
from django.forms.widgets import DateTimeInput

from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape

from perms.models import ObjectPermission
from user_groups.models import Group


def reg8n_dt_choices():
    """
    Return a tuple of 2-tuples.
    Registration datetimes (machine_name, human_name).
    """
    return (
        ('early_dt','Early registration'),
        ('regular_dt','Regular registration'),
        ('late_dt','Late registration'),
        ('end_dt','Registration ends'),
    )

def reg8n_dt_set(instance):
    """
    Return the list of registrant dates
    for this one event. i.e. (early_dt, regular_dt, late_dt, end_dt)
    """
    if not instance:
        return []

    return [
        instance.early_dt,
        instance.regular_dt,
        instance.late_dt,
        instance.end_dt,
    ]

class Reg8nDtWidget(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        
        # checking for value down here
        # forces 'value' to be required in the method call
        if value is None: value = []

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

        print 'self.choices', self.choices

        html = u''
        for machine_name, human_name in self.choices:

            if machine_name != 'end_dt':
                html += """
                    <div>%s starts %s</div>
                    """ %   (
                                human_name, 
                                DateTimeInput().render(machine_name, u'')
                            )

            print 'final_attrs', final_attrs
            print 'attrs', attrs

            # $12.00 after 3/20/2011
            # $20.00 after 3/25/2011
            # $30.00 after 3/30/2011
            # registration ends 4/5/2011
            
            # make new widget that inherits directly from widget (input?)
            # eventually we're passing in 7 different names/values
            # choices works but seems hacky
            # think widget with multiple fields
            # Reg8nDt(fields=((early_dt, regular_dt, late_dt)))

        return mark_safe(html)

        # for i, (user_label, user_perm) in enumerate(groupby(self.choices,lambda x: x[1])):
        # 
        #     view_input_value = force_unicode(user_perm.next()[0])
        #     change_input_value = force_unicode(user_perm.next()[0])
        # 
        #     if has_id:
        #         final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
        # 
        #     cb_view = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
        #     cb_change = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
        #     rendered_cb_view = cb_view.render(name, view_input_value)
        #     rendered_cb_change = cb_change.render(name, change_input_value)
        # 
        #     if (i % 2) == 0:
        #         tr_class = ' class="alt" '
        #     else:
        #         tr_class = ''
        # 
        #     table_rows += """
        #         <tr%(tr_class)s>
        #             <td>%(user_label)s</td>
        #             <td>%(view_checkbox)s</td>
        #             <td>%(change_checkbox)s</td>
        #         </tr>
        #     """ % {'tr_class':tr_class,  
        #            'user_label': conditional_escape(force_unicode(user_label)),
        #            'view_checkbox': rendered_cb_view,
        #            'change_checkbox': rendered_cb_change
        #           }
        # 
        # html = html % { 
        #         'id': id, 
        #         'table_rows': table_rows
        #         }
        # return mark_safe(html)


class Reg8nDtField(MultipleChoiceField): 
    """
        Inherits from MultipleChoiceField and
        sets some default meta data
    """    
    widget = Reg8nDtWidget
    def __init__(self, *args, **kwargs):
        try:
            kwargs.update(user_perm_options)
        except:
            # in database setup we can't get database entries
            # when they do not exist           
            pass
        super(Reg8nDtField, self).__init__(*args, **kwargs)