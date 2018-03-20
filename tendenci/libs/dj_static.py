# -*- coding: utf-8 -*-

# To use:
# * Run `pip install dj-static`
# * Make sure STATIC_ROOT, STATIC_URL, MEDIA_ROOT, MEDIA_URL, and THEMES_DIR are
#   configured appropriately in settings.py or local_settings.py
# * In wsgi.py:
#    from django.core.wsgi import get_wsgi_application
#    from dj_static import Cling, MediaCling
#    from tendenci.libs.dj_static import ThemeCling
#    application = Cling(ThemeCling(MediaCling(get_wsgi_application())))


from django.conf import settings
from dj_static import MediaCling


class ThemeCling(MediaCling):

    def get_base_dir(self):
        return settings.THEMES_DIR

    def get_base_url(self):
        return "/themes/"
