from builtins import str
import operator
from functools import reduce

from django import forms
from django.apps import apps
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth.models import User

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.registry.sites import site as registry_site
from tendenci.apps.event_logs.models import EventLog
try:
    from tendenci.apps.corporate_memberships.models import CorpMembership as CorpMemb
except:
    CorpMemb = None

import haystack
from haystack.query import SearchQuerySet

apps_not_to_search = [
    'discount',
    'donation',
    'file',
    'form',
    'box',
    'event_log',
    'invoice',
    'redirect',
    'user',
    'story',
    'member',
    'nav',
]

registered_apps = registry_site.get_registered_apps()
registered_apps_names = [app['model']._meta.model_name for app in registered_apps
                        if app['verbose_name'].lower() not in apps_not_to_search]
registered_apps_models = [app['model'] for app in registered_apps
                         if app['verbose_name'].lower() not in apps_not_to_search]


def model_choices(site=None):
    if site is None:
        site = haystack.connections['default'].unified_index()

    choices = []
    for m in site.get_indexed_models():
        if m._meta.model_name.lower() in registered_apps_names:
            if get_setting("module", m._meta.app_label, "enabled") is not False:
                choices.append(("%s.%s" % (m._meta.app_label, m._meta.model_name),
                                capfirst(str(m._meta.verbose_name_plural))))

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

    def search(self, order_by='newest'):
        self.clean()
        sqs = SearchQuerySet()
        if self.is_valid():
            query = self.cleaned_data['q']
        else:
            query = ''
        
        if not query:
            return sqs.none()
        
        if not order_by:
            order_by = 'newest'

        sqs = sqs.filter(status=True)
        user = self.user

        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user

        is_an_admin = user.profile.is_superuser

        # making a special case for corp memb because it needs to utilize two settings
        # (anonymoussearchcorporatemembers and membersearchcorporatemembers)
        if CorpMemb and self.cleaned_data['models'] == ["%s.%s" % (CorpMemb._meta.app_label,
                                                                   CorpMemb._meta.model_name)]:
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
                        if not user.is_anonymous:
                        # if b/w admin and anon

                            # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                            anon_query = Q(**{'allow_anonymous_view':True,})
                            user_query = Q(**{'allow_user_view':True,})
                            sec1_query = Q(**{
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
                            sqs = sqs.filter(status_detail='active')
                            sqs = sqs.filter(allow_anonymous_view=True)
                else:
                    # if anonymous
                    sqs = sqs.filter(status_detail='active')
                    sqs = sqs.filter(allow_anonymous_view=True)
            else:
                if user:
                    if is_an_admin:
                        sqs = sqs.all()
                    else:
                        if not user.is_anonymous:
                            # (status+status_detail+anon OR who_can_view__exact)
                            sec1_query = Q(**{
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
                            sqs = sqs.filter(status_detail='active')
                            sqs = sqs.filter(allow_anonymous_view=True)
                else:
                    # if anonymous
                    sqs = sqs.filter(status_detail='active')
                    sqs = sqs.filter(allow_anonymous_view=True)

            # for solr,
            # order_by can only called once so we have to do it here
            if order_by == 'newest':
                # changed order_by from create_dt to order because the order field
                # is a common field in search indexes and used by other modules(news)
                sqs = sqs.order_by('-order')
            else:
                sqs = sqs.order_by('order')

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
    SORT_CHOICES = (
        ('newest',_('Newest')),
        ('oldest', _('Oldest'))
        #('most_viewed', 'Most Viewed')
    )
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(ModelSearchForm, self).__init__(*args, **kwargs)

        # Check to see if users should be included in global search
        include_users = False

        if kwargs['user'].profile.is_superuser or get_setting('module', 'users', 'allowanonymoususersearchuser') \
        or (kwargs['user'].is_authenticated and get_setting('module', 'users', 'allowusersearch')):
            include_users = True

        if include_users:
            for app in registered_apps:
                if app['verbose_name'].lower() == 'user':
                    registered_apps_models.append(app['model'])
                    registered_apps_names.append(app['model']._meta.model_name)
        else:
            for app in registered_apps:
                if app['verbose_name'].lower() in ['user', 'membership']:
                    try:
                        models_index = registered_apps_models.index(app['model'])
                        registered_apps_models.pop(models_index)
                        names_index = registered_apps_names.index(app['model']._meta.model_name)
                        registered_apps_names.pop(names_index)
                    except Exception:
                        pass

        self.models = registered_apps_models
        self.fields['models'] = forms.MultipleChoiceField(choices=model_choices(), required=False, label=_('Search In'), widget=forms.CheckboxSelectMultiple)

    def get_models(self):
        """Return an alphabetical list of model classes in the index."""
        search_models = self.models
        if self.cleaned_data.get('models', []):
            search_models = []
            for model in self.cleaned_data['models']:
                class_model = apps.get_model(*model.split('.'))
                #if class_model._meta.model_name in INCLUDED_APPS:
                search_models.append(class_model)
        return search_models

    def search(self, order_by=None):
        if not order_by:
            order_by = self.cleaned_data['sort_by']
        sqs = super(ModelSearchForm, self).search(order_by=order_by)
        sqs = sqs.models(*self.get_models())
        if order_by == 'most_viewed':
            # we need to query for number of views
            for s in sqs:
                instance = s.object
                ct = ContentType.objects.get_for_model(instance)
                views = EventLog.objects.filter(
                            content_type=ct,
                            action__icontains='detail',
                            object_id=instance.pk).count()
                s.views = views
            # We need to do this unless we
            # we have a 'view count' field for each model
            sqs = sorted(sqs, key=lambda s: s.views, reverse=True) # no longer an sqs
        return sqs


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
