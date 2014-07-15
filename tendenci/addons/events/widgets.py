from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

class UseCustomRegWidget(forms.MultiWidget):
    """This widget is for three fields on event add/edit under Registration:
            use_custom_reg_form
            reg_form
            bind_reg_form_to_conf_only
    """
    def __init__(self, attrs=None, reg_form_choices=None, event_id=None):
        self.attrs = attrs
        self.reg_form_choices = reg_form_choices
        self.event_id = event_id
        if not self.attrs:
            self.attrs = {'id':'use_custom_reg'}
        self.widgets = (forms.CheckboxInput(),
                        forms.Select(),
                        forms.RadioSelect())
        super(UseCustomRegWidget, self).__init__(self.widgets, attrs)

    def render(self, name, value, attrs=None):
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        use_custom_reg_form_widget = self.widgets[0]
        rendered_use_custom_reg_form = self.render_widget(
                                    use_custom_reg_form_widget,
                                    name, value, final_attrs,
                                    0, id_)

        reg_form_widget = self.widgets[1]
        reg_form_widget.choices = self.reg_form_choices
        #reg_form_widget.attrs = {'size':'8'}
        rendered_reg_form = '<div style="margin-left:2em;">%s</div>' % \
                            self.render_widget(reg_form_widget,
                                                name, value, final_attrs,
                                                1, id_)
        bind_reg_form_to_conf_only_widget = self.widgets[2]
        choices=(('1', mark_safe('Use one form for all pricings %s' \
                                 % rendered_reg_form)),)
        bind_reg_form_to_conf_only_widget.choices = choices
        rendered_bind_reg_form_to_conf_only = self.render_widget(
                                    bind_reg_form_to_conf_only_widget,
                                    name, value, final_attrs,
                                    2, id_)
        rendered_bind_reg_form_to_conf_only = rendered_bind_reg_form_to_conf_only.replace(
                               '%s</label>' % rendered_reg_form, "</label>%s" % rendered_reg_form
                                                                                          )
        if self.event_id:
            manage_custom_reg_link = """
                            <div style="margin: 1em 0 0 2em;"><a href="%s" target="_blank">Manage Custom Registration Form</a></div>
                                    """ % reverse('event.event_custom_reg_form_list', args=[self.event_id])
        else:
            manage_custom_reg_link = ''

        output_html = """
                      <div id="use-custom_reg-box">
                          <div id="use-custom-reg-checkbox">%s <label for="id_%s_%s">Use Custom Registration Form</label></div>

                          <div id="one-or-separate-form">%s</div>
                          %s
                      </div>
                    """ % (
                           rendered_use_custom_reg_form, name, '0',
                           rendered_bind_reg_form_to_conf_only,
                           manage_custom_reg_link
                           )
        return mark_safe(output_html)

    def render_widget(self, widget, name, value, attrs, index=0, id=None):
        i = index
        id_ = id
        if value:
            try:
                widget_value = value[i]
            except IndexError:
                self.fields['use_reg_form'].initial = None
        else:
            widget_value = None
        if id_:
            final_attrs = dict(attrs, id='%s_%s' % (id_, i))

        return widget.render(name+'_%s' %i, widget_value, final_attrs)


    def decompress(self, value):
        if value:
            data_list = value.split(',')
            if data_list[0] == '1':
                data_list[0] = 'on'
            return data_list
        return None
