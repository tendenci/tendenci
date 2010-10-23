from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from models import Topic, HelpFile
from forms import RequestForm

def index(request, template_name="help_files/index.html"):
    "List all topics and all links"
    
    topics = list(Topic.objects.all())
    m = len(topics)/2
    topics = topics[:m], topics[m:] # two columns
    most_viewed = HelpFile.objects.order_by('-view_totals')[:5]
    featured = HelpFile.objects.filter(is_featured=True)[:5]
    faq = HelpFile.objects.filter(is_faq=True)[:3]
    
    return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))

def search(request, template_name="help_files/search.html"):
    """ Help Files Search """
    query = request.GET.get('q', None)
    help_files = HelpFile.objects.search(query, user=request.user)

    return render_to_response(template_name, {'help_files':help_files}, 
        context_instance=RequestContext(request))

def topic(request, id, template_name="help_files/topic.html"):
    "List of topic help files"
    topic = get_object_or_404(Topic, pk=id)
    return render_to_response(template_name, {'topic':topic}, 
        context_instance=RequestContext(request))

def details(request, slug, template_name="help_files/details.html"):
    "Help file details"
    help_file = get_object_or_404(HelpFile, slug=slug)
    help_file.view_totals += 1
    help_file.save()

    return render_to_response(template_name, {'help_file': help_file}, 
        context_instance=RequestContext(request))

def request_new(request, template_name="help_files/request_new.html"):
    "Request new file form"
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Thanks for requesting a new help file!')
            return HttpResponseRedirect(reverse('help_files'))
    else:
        form = RequestForm()
        
    return render_to_response(template_name, {'form': form}, 
        context_instance=RequestContext(request))