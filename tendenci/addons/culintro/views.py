from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from tendenci.core.base.http import Http403
from tendenci.core.event_logs.models import EventLog
from haystack.query import SQ
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import (get_notice_recipients, update_perms_and_save, has_perm, get_query_filters,
    has_view_perm)
from tendenci.core.categories.forms import CategoryForm, CategoryForm2
from tendenci.core.categories.models import Category
from tendenci.core.theme.shortcuts import themed_response as render_to_response

from tendenci.addons.culintro.models import CulintroJob
from tendenci.addons.culintro.forms import CulintroJobForm, CulintroSearchForm

def detail(request, slug=None, template_name="culintro/view.html"):
    if not slug:
        return HttpResponseRedirect(reverse('culintro_jobs'))
    job = get_object_or_404(CulintroJob.objects.select_related(), slug=slug)

    can_view = has_view_perm(request.user, 'culintro_jobs.view_job', job)
    
    print job.categories.all().values()

    if can_view:
        EventLog.objects.log(instance=job)
        # Pass both job as job and culintro_job to avoid conflicts with meta.html
        return render_to_response(template_name, {'job': job, 'culintro_job': job},
            context_instance=RequestContext(request))
    else:
        raise Http403
    
def search(request, template_name="culintro/search.html"):
    query = request.GET.get('q', None)
    open_call = None
    locations = []
    categories = []

    if get_setting('site', 'global', 'searchindex') and query:
        jobs = CulintroJob.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'jobs.view_job')
        jobs = CulintroJob.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            jobs = jobs.select_related()
            
    form = CulintroSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('q')
        open_call = form.cleaned_data.get('open_call')
        locations = form.cleaned_data.get('location')
        categories = form.cleaned_data.get('categories')
    
    # Filter open_call
    if open_call is not None:
        jobs = jobs.filter(open_call=open_call)
    # Filter locations
    if locations:
        sqs = None
        for location in locations:
            if sqs is None:
                sqs = SQ(location_2=location)
            else:
                sqs = sqs | SQ(location_2=location)
        jobs = jobs.filter(sqs)

    jobs = jobs.order_by('status_detail', 'list_type', '-post_dt')
    
    # Filter categories
    if categories:
        jobs_list = []
        for job in jobs:
            if hasattr(job, "object"): # since we don't always use haystack
                job = job.object
            cat = Category.objects.get_for_object(job, 'category')
            sub_cat = Category.objects.get_for_object(job, 'sub_category')
            for category in categories:
                if cat == category[0] and sub_cat == category[1]:
                    jobs_list.append(job)
                    break
        jobs = jobs_list

    EventLog.objects.log()

    return render_to_response(template_name, {'jobs': jobs, 'form': form},
        context_instance=RequestContext(request))
