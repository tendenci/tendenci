# coding=utf-8
from __future__ import absolute_import
import urllib, hashlib
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import defaults, util
from .compat import get_image_field_class, get_username_field
from tendenci.apps.site_settings.utils import get_setting


TZ_CHOICES = [(float(x[0]), x[1]) for x in (
    (-12, '-12'), (-11, '-11'), (-10, '-10'), (-9.5, '-09.5'), (-9, '-09'),
    (-8.5, '-08.5'), (-8, '-08 PST'), (-7, '-07 MST'), (-6, '-06 CST'),
    (-5, '-05 EST'), (-4, '-04 AST'), (-3.5, '-03.5'), (-3, '-03 ADT'),
    (-2, '-02'), (-1, '-01'), (0, '00 GMT'), (1, '+01 CET'), (2, '+02'),
    (3, '+03'), (3.5, '+03.5'), (4, '+04'), (4.5, '+04.5'), (5, '+05'),
    (5.5, '+05.5'), (6, '+06'), (6.5, '+06.5'), (7, '+07'), (8, '+08'),
    (9, '+09'), (9.5, '+09.5'), (10, '+10'), (10.5, '+10.5'), (11, '+11'),
    (11.5, '+11.5'), (12, '+12'), (13, '+13'), (14, '+14'),
)]


class PybbProfile(models.Model):
    """
    Abstract class for user profile, site profile should be inherted from this class
    """

    class Meta(object):
        abstract = True
        permissions = (
            ("block_users", "Can block any user"),
        )

    signature = models.TextField(_('Signature'), blank=True, max_length=defaults.PYBB_SIGNATURE_MAX_LENGTH)
    signature_html = models.TextField(_('Signature HTML Version'), blank=True,
                                      max_length=defaults.PYBB_SIGNATURE_MAX_LENGTH + 30)
    time_zone = models.FloatField(_('Time zone'), choices=TZ_CHOICES, default=float(defaults.PYBB_DEFAULT_TIME_ZONE))
    language = models.CharField(_('Language'), max_length=10, blank=True, choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)
    show_signatures = models.BooleanField(_('Show signatures'), blank=True, default=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    avatar = get_image_field_class()(_('Avatar'), blank=True, null=True,
                                     upload_to=util.FilePathGenerator(to='pybb/avatar'))
    autosubscribe = models.BooleanField(_('Automatically subscribe'),
                                        help_text=_('Automatically subscribe to topics that you answer'),
                                        default=defaults.PYBB_DEFAULT_AUTOSUBSCRIBE)

    def save(self, *args, **kwargs):
        self.signature_html = util._get_markup_formatter()(self.signature)
        super(PybbProfile, self).save(*args, **kwargs)

    @property
    def avatar_url(self):
        try:
            return self.avatar.url
        except:
            return defaults.PYBB_DEFAULT_AVATAR_URL

    def get_display_name(self):
        try:
            if hasattr(self, 'user'):  # we have OneToOne foreign key to user model
                return self.user.get_username()
            if not defaults.PYBB_PROFILE_RELATED_NAME:  # we now in user custom model itself
                return self.get_username()
        except Exception:
            return unicode(self)

    def getMD5(self):
        m = hashlib.md5()
        m.update(self.user.email)        
        return m.hexdigest()
    
    def get_gravatar_url(self):
        size = defaults.PYBB_AVATAR_WIDTH
        default = get_setting('site', 'global', 'siteurl') +  defaults.PYBB_DEFAULT_AVATAR_URL
        gravatar_url = "//www.gravatar.com/avatar/" + self.getMD5() + "?"
        gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
        return gravatar_url
        
        
        
