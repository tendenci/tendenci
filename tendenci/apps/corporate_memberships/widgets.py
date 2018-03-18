from django import forms
from django.utils.safestring import mark_safe

from tendenci.apps.corporate_memberships.models import NOTICE_TYPES

class NoticeTimeTypeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        self.attrs = attrs
        self.pos_d = {'num_days': (0, forms.TextInput()),
                      'notice_time': (1, forms.Select()),
                      'notice_type':(2, forms.Select()),
                       }
        self.widgets = ()
        if self.pos_d:
            items = list(self.pos_d.values())
            items.sort()
            self.widgets = [item[1] for item in items]

        super(NoticeTimeTypeWidget, self).__init__(self.widgets, attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if not isinstance(value, list):
            value = self.decompress(value)

        id_ = attrs.get('id', None)

        # num_days
        num_days_widget = self.pos_d['num_days'][1]
        num_days_widget.attrs = {'size':'8'}
        rendered_num_days = self.render_widget(num_days_widget, name, value, attrs,
                                             self.pos_d['num_days'][0], id_)

        # notice_time
        notice_time_widget = self.pos_d['notice_time'][1]
        notice_time_widget.choices = (('after','After'),
                                      ('before','Before'),
                                      ('attimeof','At Time Of'))
        rendered_notice_time = self.render_widget(notice_time_widget,
                                                  name, value, attrs, self.pos_d['notice_time'][0], id_)

        # notice_type
        notice_type_widget = self.pos_d['notice_type'][1]
        notice_type_widget.choices = NOTICE_TYPES
        rendered_notice_type = self.render_widget(
            notice_type_widget, name, value, attrs,
            self.pos_d['notice_type'][0], id
        )

        output_html = """
                        <div id="notice-time-type">
                            %s day(s) %s %s
                        </div>
                      """ % (rendered_num_days,
                             rendered_notice_time,
                             rendered_notice_type
                             )

        return mark_safe(output_html)

    def render_widget(self, widget, name, value, attrs, index=0, id=None):
        i = index
        id_ = id
        if value:
            try:
                widget_value = value[i]
            except IndexError:
                self.fields['notice_time_type'].initial = None
        else:
            widget_value = None
        if id_:
            final_attrs = dict(attrs, id='%s_%s' % (id_, i))

        return widget.render(name+'_%s' %i, widget_value, final_attrs)

    def decompress(self, value):
        if value:
            return value.split(",")
        return None
