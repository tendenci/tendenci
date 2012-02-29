import operator

from django import forms
from django.db import models
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User

from perms.utils import is_admin
from site_settings.utils import get_setting
from registry import site as registry_site
try:
    from corporate_memberships.models import CorporateMembership as CorpMemb
except:
    CorpMemb = None

import haystack
from haystack.query import SearchQuerySet

apps_not_to_search = [
    'donation',
    'file',
    'form',
    'box',
    'event_log',
    'invoice',
    'redirect',
    'user',
]

registered_apps = registry_site.get_registered_apps()
registered_apps_names = [app['model']._meta.module_name for app in registered_apps \
                        if app['verbose_name'].lower() not in apps_not_to_search]
registered_apps_models = [app['model'] for app in registered_apps \
                         if app['verbose_name'].lower() not in apps_not_to_search]


def model_choices(site=None):
    if site is None:
        site = haystack.sites.site

    choices = []
    for m in site.get_indexed_models():
        if m._meta.module_name.lower() in registered_apps_names:
            choices.append(("%s.%s" % (m._meta.app_label, m._meta.module_name), 
                                capfirst(unicode(m._meta.verbose_name_plural))))
            
    return sorted(choices, key=lambda x: x[1])


class SearchForm(forms.Form):
    q = forms.CharField(required=False, label=_('Search'), max_length=255)
    
    def __init__(self, *args, **kwargs):
        self.searchqueryset = kwargs.get('searchqueryset', None)
        self.load_all = kwargs.get('load_all', False)
        self.user = kwargs.get('user', None)
        
        if self.searchqueryset is None:
            self.searchqueryset = SearchQuerySet()
        
        try:
            del(kwargs['searchqueryset'])
        except KeyError:
            pass
        
        try:
            del(kwargs['load_all'])
        except KeyError:
            pass

        try:
            del(kwargs['user'])
        except KeyError:
            pass
                
        super(SearchForm, self).__init__(*args, **kwargs)
    
    def search(self):
        self.clean()

        sqs = SearchQuerySet()
        user = self.user
        query = self.cleaned_data['q']

        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user
                
        is_an_admin = is_admin(user)
        
        # making a special case for corp memb because it needs to utilize two settings
        # (anonymoussearchcorporatemembers and membersearchcorporatemembers)
        if CorpMemb and self.cleaned_data['models'] == ["%s.%s" % (CorpMemb._meta.app_label, 
                                                                   CorpMemb._meta.module_name)]:
            filter_and, filter_or = CorpMemb.get_search_filter(user)
            q_obj = None
            if filter_and:
                q_obj = Q(**filter_and)
            if filter_or:
                q_obj_or = reduce(operator.or_, [Q(**{key: value}) for key, value in filter_or.items()])
                if q_obj:
                    q_obj = reduce(operator.and_, [q_obj, q_obj_or])
                else:
                    q_obj = q_obj_or
            if q_obj:
                sqs = sqs.filter(q_obj)
            
            if query:
                sqs = sqs.auto_query(sqs.query.clean(query)) 
        else:
            
            if query:
                sqs = sqs.auto_query(sqs.query.clean(query)) 
                if user:
                    if not is_an_admin:
                        if not user.is_anonymous():
                        # if b/w admin and anon
    
                            # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                            anon_query = Q(**{'allow_anonymous_view':True,})
                            user_query = Q(**{'allow_user_view':True,})
                            sec1_query = Q(**{
                                'status':1,
                                'status_detail':'active',
                            })
                            sec2_query = Q(**{
                                'owner__exact':user.username
                            })
                            query = reduce(operator.or_, [anon_query, user_query])
                            query = reduce(operator.and_, [sec1_query, query])
                            query = reduce(operator.or_, [query, sec2_query])
    
                            sqs = sqs.filter(query)
                        else:
                        # if anonymous
                            sqs = sqs.filter(status=1).filter(status_detail='active')
                            sqs = sqs.filter(allow_anonymous_view=True)
                else:
                    # if anonymous
                    sqs = sqs.filter(status=1).filter(status_detail='active')
                    sqs = sqs.filter(allow_anonymous_view=True)
            else:
                if user:
                    if is_an_admin:
                        sqs = sqs.all()
                    else:
                        if not user.is_anonymous():
                            # (status+status_detail+anon OR who_can_view__exact)
                            sec1_query = Q(**{
                                'status':1,
                                'status_detail':'active',
                                'allow_anonymous_view':True,
                            })
                            sec2_query = Q(**{
                                'owner__exact':user.username
                            })
                            query = reduce(operator.or_, [sec1_query, sec2_query])
                            sqs = sqs.filter(query)
                        else:
                            # if anonymous
                            sqs = sqs.filter(status=1).filter(status_detail='active')
                            sqs = sqs.filter(allow_anonymous_view=True)               
                else:
                    # if anonymous
                    sqs = sqs.filter(status=1).filter(status_detail='active')
                    sqs = sqs.filter(allow_anonymous_view=True)

            sqs = sqs.order_by('-create_dt')
        
        if self.load_all:
            sqs = sqs.load_all()
        
        return sqs


class HighlightedSearchForm(SearchForm):
    def search(self):
        return super(HighlightedSearchForm, self).search().highlight()


class FacetedSearchForm(SearchForm):
    selected_facets = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def search(self):
        sqs = super(FacetedSearchForm, self).search()
        
        if self.cleaned_data['selected_facets']:
            sqs = sqs.narrow(self.cleaned_data['selected_facets'])
        
        return sqs


class ModelSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(ModelSearchForm, self).__init__(*args, **kwargs)

        # Check to see if users should be included in global search
        include_users = False

        if is_admin(kwargs['user']) or get_setting('module', 'users', 'allowanonymoususersearchuser') \
        or (kwargs['user'].is_authenticated() and get_setting('module', 'users', 'allowusersearch')):
            include_users = True

        if include_users:
            for app in registered_apps:
                if app['verbose_name'].lower() == 'user':
                    registered_apps_models.append(app['model'])
                    registered_apps_names.append(app['model']._meta.module_name)

        self.models = registered_apps_models
        self.fields['models'] = forms.MultipleChoiceField(choices=model_choices(), required=False, label=_('Search In'), widget=forms.CheckboxSelectMultiple)

    def get_models(self):
        """Return an alphabetical list of model classes in the index."""
        search_models = self.models
        if self.cleaned_data['models']:
            search_models = []
            for model in self.cleaned_data['models']:
                class_model = models.get_model(*model.split('.'))
                #if class_model._meta.module_name in INCLUDED_APPS:
                search_models.append(class_model)
        return search_models
    
    def search(self):
        sqs = super(ModelSearchForm, self).search()
        return sqs.models(*self.get_models())


class HighlightedModelSearchForm(ModelSearchForm):
    def search(self):
        return super(HighlightedModelSearchForm, self).search().highlight()


class FacetedModelSearchForm(ModelSearchForm):
    selected_facets = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def search(self):
        sqs = super(FacetedModelSearchForm, self).search()
        
        if self.cleaned_data['selected_facets']:
            sqs = sqs.narrow(self.cleaned_data['selected_facets'])
        
        return sqs.models(*self.get_models())
