# -*- coding: utf-8 -*-
from tendenci.apps.theme.templatetags.static import static

from markdown import Markdown
import bleach
from django.forms import Textarea
from django.template.loader import get_template
from ..markup.base import smile_it, BaseParser


class MarkdownWidget(Textarea):
    class Media:
        css = {
            'all': (
                static('markitup/skins/simple/style.css'),
                static('markitup/sets/markdown/style.css'),
            ),
        }
        js = (
            static('markitup/ajax_csrf.js'),
            static('markitup/jquery.markitup.js'),
            static('markitup/sets/markdown/set.js'),
            static('pybb/js/markitup.js'),
        )

    def render(self, *args, **kwargs):
        tpl = get_template('pybb/markup/markdown_widget.html')
        ctx = {'widget_output': super(MarkdownWidget, self).render(*args, **kwargs)}
        return tpl.render(context=ctx)


class MarkdownParser(BaseParser):
    widget_class = MarkdownWidget

    def __init__(self):
        self._parser = Markdown()

    def format(self, text):
        return smile_it(self._parser.convert(bleach.clean(text)))

    def quote(self, text, username=''):
        return '>' + text.replace('\n', '\n>').replace('\r', '\n>') + '\n'
