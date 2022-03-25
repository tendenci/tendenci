# Copyright (c) 2008 Joost Cassee
# Licensed under the terms of the MIT License (see LICENSE.txt)

"""
This TinyMCE widget was copied and extended from this code by John D'Agostino:
http://code.djangoproject.com/wiki/CustomWidgetsTinyMCE
"""
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.admin import widgets as admin_widgets
from django.urls import reverse
from django.forms.utils import flatatt
from django.utils.html import escape
try:
    from collections import OrderedDict as SortedDict
except ImportError:
    from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext as _
from django.utils.encoding import smart_str
import json
import tendenci.libs.tinymce.settings as tinymce_settings
from tendenci.apps.theme.templatetags.static import static


class TinyMCE(forms.Textarea):
    """
    TinyMCE widget. Set settings.TINYMCE_JS_URL to set the location of the
    javascript file. Default is "MEDIA_URL + 'js/tiny_mce/tiny_mce.js'".
    You can customize the configuration with the mce_attrs argument to the
    constructor.

    In addition to the standard configuration you can set the
    'content_language' parameter. It takes the value of the 'language'
    parameter by default.

    In addition to the default settings from settings.TINYMCE_DEFAULT_CONFIG,
    this widget sets the 'language', 'directionality' and
    'spellchecker_languages' parameters by default. The first is derived from
    the current Django language, the others from the 'content_language'
    parameter.
    """
    def __init__(self, content_language=None, attrs=None, mce_attrs=None):
        super(TinyMCE, self).__init__(attrs)
        mce_attrs = mce_attrs or {}
        mce_attrs['language'] = settings.TINYMCE_DEFAULT_CONFIG.get('language', None)
        self.mce_attrs = mce_attrs
        if 'mode' not in self.mce_attrs:
            self.mce_attrs['mode'] = 'exact'
        self.mce_attrs['strict_loading_mode'] = 1
        if content_language is None:
            content_language = mce_attrs.get('language', None)
        self.content_language = content_language

    def get_mce_config(self, attrs):
        mce_config = tinymce_settings.DEFAULT_CONFIG.copy()
        mce_config.update(get_language_config(self.content_language))
        if tinymce_settings.USE_FILEBROWSER:
            mce_config['file_browser_callback'] = "tendenciFileManager"
        if self.mce_attrs.get('fullpage', False):
            mce_config['plugins'] = mce_config['plugins'] + ' fullpage'
            mce_config['fullpage_default_doctype'] = '<!DOCTYPE html>'
        mce_config.update(self.mce_attrs)
        if mce_config['mode'] == 'exact':
            mce_config['elements'] = attrs['id']
        return mce_config

    def get_mce_json(self, mce_config):
        # Fix for js functions
        js_functions = {}
        for k in ('paste_preprocess', 'paste_postprocess'):
            if k in mce_config:
                js_functions[k] = mce_config[k]
                del mce_config[k]
        mce_json = json.dumps(mce_config)
        for k in js_functions:
            index = mce_json.rfind('}')
            mce_json = mce_json[:index]+', '+k+':'+js_functions[k].strip()+mce_json[index:]
        return mce_json

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        value = smart_str(value)
        final_attrs = attrs.copy()
        final_attrs['name'] = name
        final_attrs['class'] = 'tinymce'
        assert 'id' in final_attrs, "TinyMCE widget attributes must contain 'id'"
        mce_config = self.get_mce_config(final_attrs)
        mce_json = self.get_mce_json(mce_config)
        if tinymce_settings.USE_COMPRESSOR:
            compressor_config = {
                'plugins': mce_config.get('plugins', ''),
                'themes': mce_config.get('theme', 'advanced'),
                'languages': mce_config.get('language', ''),
                'diskcache': True,
                'debug': False,
            }
            final_attrs['data-mce-gz-conf'] = json.dumps(compressor_config)
        final_attrs['data-mce-conf'] = mce_json
        html = ['<textarea%s>%s</textarea>' % (flatatt(final_attrs), escape(value))]
        return mark_safe('\n'.join(html))

    def _media(self):
        if tinymce_settings.USE_COMPRESSOR:
            js = [reverse('tinymce-compressor')]
        else:
            js = [tinymce_settings.JS_URL]
        if tinymce_settings.USE_FILEBROWSER:
            js.append(reverse('tinymce-filebrowser'))
        js.append(static('tiny_mce/init_tinymce.js'))
        css = {'all': (static('tiny_mce/custom.css'),)}
        return forms.Media(js=js, css=css)
    media = property(_media)


class AdminTinyMCE(TinyMCE, admin_widgets.AdminTextareaWidget):
    pass


def get_language_config(content_language=None):
    language = get_language()[:2]
    if content_language:
        content_language = content_language[:2]
    else:
        content_language = language

    config = {}
    config['language'] = language

    lang_names = SortedDict()
    for lang, name in settings.LANGUAGES:
        if lang[:2] not in lang_names:
            lang_names[lang[:2]] = []
        lang_names[lang[:2]].append(_(name))
    sp_langs = []
    for lang, names in lang_names.items():
        if lang == content_language:
            default = '+'
        else:
            default = ''
        sp_langs.append('%s%s=%s' % (default, ' / '.join(names), lang))

    config['spellchecker_languages'] = ','.join(sp_langs)

    if content_language in settings.LANGUAGES_BIDI:
        config['directionality'] = 'rtl'
    else:
        config['directionality'] = 'ltr'

    if tinymce_settings.USE_SPELLCHECKER:
        config['spellchecker_rpc_url'] = reverse('tinymce-spellcheck')

    return config
