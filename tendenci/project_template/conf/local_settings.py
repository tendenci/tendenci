

# Method that pulls settings from the standard settings.py
# file so that you can append or override items.
def get_setting(setting):
    import settings
    return getattr(settings, setting)

INSTALLED_APPS = get_setting('INSTALLED_APPS')

INSTALLED_APPS += (
    'videos',
    #'other_app_here',
    'case_studies',
    'committees',
    'donations',
    'speakers',
    'staff',
    'studygroups',
)
