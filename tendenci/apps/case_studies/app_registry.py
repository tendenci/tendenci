from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.case_studies.models import CaseStudy


class CaseStudyRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create case studies of clients'
    
    event_logs = {
        'case_study':{
            'base':('1000000','EE8877'),
            'add':('1000100','119933'),
            'edit':('1000200','EEDD55'),
            'delete':('1000300','AA2222'),
            'search':('1000400','CC55EE'),
            'view':('1000500','55AACC'),
        }
    }

site.register(CaseStudy, CaseStudyRegistry)
