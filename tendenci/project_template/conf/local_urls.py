from django.conf.urls.defaults import include, patterns

# Add additional url patterns for additional apps
# here and they will be included in the main urls.py
extrapatterns = patterns('',
    ('^', include('videos.urls')),
)
