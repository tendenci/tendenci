from django.conf.urls.defaults import include, patterns

# Add additional url patterns for additional apps
# here and they will be included in the main urls.py
extrapatterns = patterns('',
    ('^', include('committees.urls')),
    ('^', include('case_studies.urls')),
    ('^', include('donations.urls')),
    ('^', include('speakers.urls')),
    ('^', include('staff.urls')),
    ('^', include('studygroups.urls')),
    ('^', include('videos.urls')),
)
