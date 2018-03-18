from django import forms
from django.utils.encoding import force_text
from django.utils import formats

class Output(forms.Widget):
    """
    Base class for all <output> widgets (e.g. titles and paragraphs).
    These are fake-fields; they do not take input.
    """

    def format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        return force_text(self.format_value(value))

class Header(Output):
    """
    Outputs text.  Using class name to identify the type
    of text that is being output.
    """

class Description(Output):
    """
    Outputs text.  Using class name to identify the type
    of text that is being output.
    """
