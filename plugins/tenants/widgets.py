from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe


class ColorPickerWidget(forms.TextInput):
    class Media:
        css = {
            'all': (
                settings.MEDIA_URL + 'cssjs/colorPicker.css',
            )
        }
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.2.6/jquery.min.js',
            settings.MEDIA_URL + 'cssjs/jquery.colorPicker.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(ColorPickerWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(ColorPickerWidget, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            $('#id_%s').colorPicker();
            </script>''' % name)
