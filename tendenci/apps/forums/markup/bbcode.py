# -*- coding: utf-8 -*-
, absolute_import

from tendenci.apps.theme.templatetags.static import static
from bbcode import Parser
from django.forms import Textarea
from django.template.loader import get_template
from ..markup.base import smile_it, BaseParser


class BBCodeWidget(Textarea):
    class Media:
        css = {
            'all': (
                static('markitup/skins/simple/style.css'),
                static('markitup/sets/bbcode/style.css'),
            ),
        }
        js = (
            static('markitup/ajax_csrf.js'),
            static('markitup/jquery.markitup.js'),
            static('markitup/sets/bbcode/set.js'),
            static('pybb/js/markitup.js'),
        )

    def render(self, *args, **kwargs):
        tpl = get_template('pybb/markup/bbcode_widget.html')
        ctx = {'widget_output': super(BBCodeWidget, self).render(*args, **kwargs)}
        return tpl.render(context=ctx)


class BBCodeParser(BaseParser):
    widget_class = BBCodeWidget

    def _render_quote(self, name, value, options, parent, context):
        if options and 'quote' in options:
            origin_author_html = '<em>%s</em><br>' % options['quote']
        else:
            origin_author_html = ''
        return '<blockquote>%s%s</blockquote>' % (origin_author_html, value)

    def __init__(self):
        self._parser = Parser()
        self._parser.add_simple_formatter('img', '<img src="%(value)s">', replace_links=False)
        self._parser.add_simple_formatter('code', '<pre><code>%(value)s</code></pre>',
                                          render_embedded=False, transform_newlines=False,
                                          swallow_trailing_newline=True)
        self._parser.add_formatter('quote', self._render_quote, strip=True, swallow_trailing_newline=True)

    def format(self, text):
        return smile_it(self._parser.format(text))

    def quote(self, text, username=''):
        return '[quote="%s"]%s[/quote]\n' % (username, text)
