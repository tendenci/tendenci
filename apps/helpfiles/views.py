from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from models import Topic, HelpFile
from forms import RequestForm
from haystack.query import SearchQuerySet

def render_to(template):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1] or template, output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer


@render_to('helpfiles/home.html')
def home(request):
    "List all topics and all links"
    topics = list(Topic.objects.all())
    m = len(topics)/2
    topics = topics[:m], topics[m:] # two columns
    most_viewed = HelpFile.objects.order_by('-view_totals')[:5]
    featured = HelpFile.objects.filter(is_featured=True)[:5]
    faq = HelpFile.objects.filter(is_faq=True)[:3]
    return locals()

@render_to('helpfiles/topic.html')
def topic(request, id):
    "List of topic help files"
    topic = get_object_or_404(Topic, pk=id)
    return {'topic': topic}

@render_to('helpfiles/details.html')
def details(request, id):
    "Help file details"
    helpfile = get_object_or_404(HelpFile, pk=id)
    helpfile.view_totals += 1
    helpfile.save()
    return {'helpfile': helpfile}


@render_to('helpfiles/search.html')
def search(request):
    sqs = SearchQuerySet().models(HelpFile).auto_query(request.GET.get('q', ''))
    return {'results': sqs.load_all()}

@render_to('helpfiles/request_new.html')
def request_new(request):
    "Request new file form"
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = RequestForm()
    return {'form': form}
