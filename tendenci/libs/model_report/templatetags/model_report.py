# -*- coding: utf-8 -*-
from django import template
from django.template.loader import render_to_string


register = template.Library()


class ModelReportInlineNode(template.Node):
    def __init__(self, inline, row):
        self.inline = template.Variable(inline)
        self.row = template.Variable(row)

    def render(self, context):
        inline = self.inline.resolve(context)
        row = self.row.resolve(context)
        request = context.get('request')
        if row.is_value():
            inline_context = inline.get_render_context(request, by_row=row)
            if len(inline_context['report_rows']) > 0:
                return render_to_string('model_report/includes/report_inline.html', inline_context)
        return ''


@register.tag()
def model_report_render_inline(parser, token):
    try:
        tag_name, inline, row = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    return ModelReportInlineNode(inline, row)
