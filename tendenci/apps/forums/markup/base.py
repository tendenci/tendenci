# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from django.conf import settings
from django.utils.html import escape
from ..defaults import PYBB_SMILES, PYBB_SMILES_PREFIX
from django.forms import Textarea


def smile_it(s):
    for smile, url in PYBB_SMILES.items():
        s = s.replace(smile, '<img src="%s%s%s" alt="smile" />' % (settings.STATIC_URL, PYBB_SMILES_PREFIX, url))
    return s


def filter_blanks(user, str):
    """
    Replace more than 3 blank lines with only 1 blank line
    """
    if user.is_staff:
        return str
    return re.sub(r'\n{2}\n+', '\n', str)


def rstrip_str(user, str):
    """
    Replace strings with spaces (tabs, etc..) only with newlines
    Remove blank line at the end
    """
    if user.is_staff:
        return str
    return '\n'.join([s.rstrip() for s in str.splitlines()])


class BaseParser(object):
    widget_class = Textarea

    def format(self, text):
        return escape(text)

    def quote(self, text, username=''):
        return text

    @classmethod
    def get_widget_cls(cls, **kwargs):
        """
        Returns the form widget class to use with this parser
        It allows you to define your own widget with custom class Media to add your 
        javascript and CSS and/or define your custom "render" function
        which will allow you to add specific markup or javascript.
        """
        return cls.widget_class
