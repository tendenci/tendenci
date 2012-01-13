from registry import site
from registry.base import PeopleRegistry, lazy_reverse
from models import Profile


class ProfileRegistry(PeopleRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'User Profiles.'
    icon = '/site_media/static/images/icons/users-color-64x64.png'
    
    event_logs = {
        'profile':{
            'base':('120000','3300FF'),
            'add':('121000','3300FF'),
            'edit':('122000', '3333FF'),
            'delete':('123000', '3366FF'),
            'search':('124000', '3366FF'),
            'view':('125000', '3399FF'),
        },
        'login':{
            'login':('125200':'66CCFF'),
        },
    }
    
    url = {
        'search': lazy_reverse('profile.search'),
        'add': lazy_reverse('profile.add'),
        'settings': lazy_reverse('settings.index', args=['module','users']),
    }

site.register(Profile, ProfileRegistry)
