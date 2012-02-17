from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from base.http import Http403
from event_logs.models import EventLog
from perms.utils import has_perm, is_admin, update_perms_and_save, get_notice_recipients

from help_files.models import Topic, HelpFile, HelpFileMigration, Request
from help_files.forms import RequestForm, HelpFileForm

try:
    from notification import models as notification
except:
    notification = None


def index(request, template_name="help_files/index.html"):
    "List all topics and all links"
    topic_pks = []
    help_files = HelpFile.objects.search(None, user=request.user)

    # consolidate all the topics
    for hf in help_files:
        if hf.topic:
            topic_pks.extend(hf.topic)
    topic_pks = sorted(list(set(topic_pks)))

    topics = Topic.objects.filter(pk__in=topic_pks)
    m = len(topics)/2
    topics = topics[:m], topics[m:] # two columns
    most_viewed = HelpFile.objects.filter(allow_anonymous_view=True).order_by('-view_totals')[:5]
    featured = HelpFile.objects.filter(is_featured=True, allow_anonymous_view=True)[:5]
    faq = HelpFile.objects.filter(is_faq=True, allow_anonymous_view=True)[:3]

    return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))


def search(request, template_name="help_files/search.html"):
    """ Help Files Search """
    query = request.GET.get('q', None)
    help_files = HelpFile.objects.search(query, user=request.user)
    help_files = help_files.order_by('-create_dt')

    log_defaults = {
        'event_id' : 1000400,
        'event_data': '%s searched by %s' % ('Help File', request.user),
        'description': '%s searched' % 'Help File',
        'user': request.user,
        'request': request,
        'source': 'help_files'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'help_files':help_files}, 
        context_instance=RequestContext(request))


def topic(request, id, template_name="help_files/topic.html"):
    """ List of topic help files """
    topic = get_object_or_404(Topic, pk=id)
    query = None

    help_files = HelpFile.objects.search(query, user=request.user)
    help_files = help_files.filter(topic__in=[topic.pk])

    return render_to_response(template_name, {'topic':topic, 'help_files':help_files}, 
        context_instance=RequestContext(request))


def details(request, slug, template_name="help_files/details.html"):
    "Help file details"
    help_file = get_object_or_404(HelpFile, slug=slug)
    HelpFile.objects.filter(pk=help_file.pk).update(view_totals=help_file.view_totals+1)

    if has_perm(request.user, 'help_files.view_helpfile', help_file):
        log_defaults = {
            'event_id' : 1000500,
            'event_data': '%s (%d) viewed by %s' % (help_file._meta.object_name, help_file.pk, request.user),
            'description': '%s viewed' % help_file._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': help_file,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'help_file': help_file}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=HelpFileForm, template_name="help_files/add.html"):
    if has_perm(request.user,'help_files.add_helpfile'):
        if request.method == "POST":
            form = form_class(request.POST, user=request.user)
            if form.is_valid():           
                help_file = form.save(commit=False)

                # add all permissions and save the model
                help_file = update_perms_and_save(request, form, help_file)
                form.save_m2m()

                log_defaults = {
                    'event_id' : 1000100,
                    'event_data': '%s (%d) added by %s' % (help_file._meta.object_name, help_file.pk, request.user),
                    'description': '%s added' % help_file._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': help_file,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % help_file)
                
                # send notification to administrator(s) and module recipient(s)
                recipients = get_notice_recipients('module', 'help_files', 'helpfilerecipients')
                # if recipients and notification: 
#                     notification.send_emails(recipients,'help_file_added', {
#                         'object': help_file,
#                         'request': request,
#                     })

                return HttpResponseRedirect(reverse('help_file.details', args=[help_file.slug]))
        else:
            form = form_class(user=request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit(request, id=None, form_class=HelpFileForm, template_name="help_files/edit.html"):
    help_file = get_object_or_404(HelpFile, pk=id)
    if has_perm(request.user,'help_files.change_helpfile', help_file):
        if request.method == "POST":
            form = form_class(request.POST, instance=help_file, user=request.user)
            if form.is_valid():           
                help_file = form.save(commit=False)

                # add all permissions and save the model
                help_file = update_perms_and_save(request, form, help_file)
                form.save_m2m()

                log_defaults = {
                    'event_id' : 1000200,
                    'event_data': '%s (%d) edited by %s' % (help_file._meta.object_name, help_file.pk, request.user),
                    'description': '%s edited' % help_file._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': help_file,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.SUCCESS, 'Successfully edited %s' % help_file)
                
                # send notification to administrator(s) and module recipient(s)
                recipients = get_notice_recipients('module', 'help_files', 'helpfilerecipients')
                # if recipients and notification: 
#                     notification.send_emails(recipients,'help_file_added', {
#                         'object': help_file,
#                         'request': request,
#                     })

                return HttpResponseRedirect(reverse('help_file.details', args=[help_file.slug]))
        else:
            form = form_class(instance=help_file, user=request.user)
           
        return render_to_response(template_name, {'help_file': help_file, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def request_new(request, template_name="help_files/request_new.html"):
    "Request new file form"
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            instance = form.save()
            # send notification to administrators
            recipients = get_notice_recipients('module', 'help_files', 'helpfilerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': instance,
                        'request': request,
                    }
                    notification.send_emails(recipients,'help_file_requested', extra_context)
            messages.add_message(request, messages.INFO, 'Thanks for requesting a new help file!')
            return HttpResponseRedirect(reverse('help_files'))
    else:
        form = RequestForm()
        
    return render_to_response(template_name, {'form': form}, 
        context_instance=RequestContext(request))


def redirects(request, id):
    """
        Redirect old Tendenci 4 IDs to new Tendenci 5 slugs
    """
    try:
        help_file_migration = HelpFileMigration.objects.get(t4_id=id)
        try:
            help_file = HelpFile.objects.get(pk=help_file_migration.t5_id)
            return HttpResponsePermanentRedirect(help_file.get_absolute_url())
        except:
            return HttpResponsePermanentRedirect(reverse('help_files'))
    except:
        return HttpResponsePermanentRedirect(reverse('help_files'))

def requests(request, template_name="help_files/request_list.html"):
    """
        Display a list of help file requests
    """
    if not is_admin(request.user):
        raise Http403
    
    requests = Request.objects.all()
    
    return render_to_response(template_name, {
        'requests': requests,
        }, context_instance=RequestContext(request))
