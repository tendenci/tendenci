from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from tendenci.apps.memberships.widgets import NoticeTimeTypeWidget

from .models import NOTICE_TYPES

class ChapterNoticeTimeTypeWidget(NoticeTimeTypeWidget):
    def render(self, name, value, attrs=None, renderer=None):
        if not isinstance(value, list):
            value = self.decompress(value)

        id_ = attrs.get('id', None)
        attrs.update({'class': 'form-control'})

        # num_days
        num_days_widget = self.pos_d['num_days'][1]
        num_days_widget.attrs = {'size':'8'}
        rendered_num_days = self.render_widget(num_days_widget, name, value, attrs,
                                             self.pos_d['num_days'][0], id_)

        # notice_time
        notice_time_widget = self.pos_d['notice_time'][1]
        notice_time_widget.choices = (('after',_('After')),
                                      ('before',_('Before')),
                                      ('attimeof',_('At Time Of')))
        rendered_notice_time = self.render_widget(notice_time_widget,
                                                  name, value, attrs, self.pos_d['notice_time'][0], id_)

        # notice_type
        notice_type_widget = self.pos_d['notice_type'][1]
        notice_type_widget.choices = NOTICE_TYPES
        rendered_notice_type = self.render_widget(
            notice_type_widget,name,value,attrs,
            self.pos_d['notice_type'][0],id
        )

        output_html = f"""
                        <div id="notice-time-type">
                            {rendered_num_days} day(s) {rendered_notice_time} {rendered_notice_type}
                        </div>
                      """

        return mark_safe(output_html)
