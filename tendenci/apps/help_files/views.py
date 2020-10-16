from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.exports.utils import run_export_task
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import has_perm, update_perms_and_save, get_notice_recipients, has_view_perm, get_query_filters
from tendenci.apps.help_files.models import Topic, HelpFile, HelpFileMigration, Request
from tendenci.apps.help_files.forms import RequestForm, HelpFileForm
from tendenci.apps.notifications import models as notification


@is_enabled('help_files')
def index(request, template_name="help_files/index.html"):
    """List all topics and all links"""
    topic_pks = []
    filters = get_query_filters(request.user, 'help_files.view_helpfile')

    topics = Topic.objects.filter(id__in=HelpFile.objects.values_list('topics')).order_by('title')
    m = int(len(topics) / 2)
    topics = topics[:m], topics[m:] # two columns
    most_viewed = HelpFile.objects.filter(filters).order_by('-view_totals').distinct()[:5]
    featured = HelpFile.objects.filter(filters).filter(is_featured=True).distinct()[:5]
    faq = HelpFile.objects.filter(filters).filter(is_faq=True).distinct()[:3]

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context=locals())


@is_enabled('help_files')
def search(request, template_name="help_files/search.html"):
    """ Help Files Search """
    query = request.GET.get('q', None)

    if get_setting('site', 'global', 'searchindex') and query:
        help_files = HelpFile.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'help_files.view_helpfile')
        help_files = HelpFile.objects.filter(filters).distinct()
        if not request.user.is_anonymous:
            help_files = help_files.select_related()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'help_files':help_files})


@is_enabled('help_files')
def topic(request, id, template_name="help_files/topic.html"):
    """ List of topic help files """
    topic = get_object_or_404(Topic, pk=id)

    filters = get_query_filters(request.user, 'help_files.view_helpfile')
    help_files = HelpFile.objects.filter(filters).filter(topics__in=[topic.pk]).distinct()
    if not request.user.is_anonymous:
        help_files = help_files.select_related()

    EventLog.objects.log(instance=topic)

    return render_to_resp(request=request, template_name=template_name,
        context={'topic':topic, 'help_files':help_files})

@is_enabled('help_files')
def faqs(request, template_name="help_files/faqs.html"):
    """ List of FAQ help files """
    filters = get_query_filters(request.user, 'help_files.view_helpfile')
    help_files = HelpFile.objects.filter(filters).filter(is_faq=True).distinct()
    if not request.user.is_anonymous:
        help_files = help_files.select_related()

    EventLog.objects.log(description="FAQs viewed")

    return render_to_resp(request=request, template_name=template_name,
        context={'help_files':help_files})

@is_enabled('help_files')
def detail(request, slug, template_name="help_files/details.html"):
    """Help file details"""
    help_file = get_object_or_404(HelpFile, slug=slug)

    if has_view_perm(request.user, 'help_files.view_helpfile', help_file):
        HelpFile.objects.filter(pk=help_file.pk).update(view_totals=help_file.view_totals+1)
        EventLog.objects.log(instance=help_file)
        return render_to_resp(request=request, template_name=template_name,
            context={'help_file': help_file})
    else:
        raise Http403


@is_enabled('help_files')
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
                msg_string = 'Successfully added %s' % help_file
                messages.add_message(request, messages.SUCCESS, _(msg_string))

#                # send notification to administrator(s) and module recipient(s)
#                recipients = get_notice_recipients('module', 'help_files', 'helpfilerecipients')
#                # if recipients and notification:
#                     notification.send_emails(recipients,'help_file_added', {
#                         'object': help_file,
#                         'request': request,
#                     })

                return HttpResponseRedirect(reverse('help_file.details', args=[help_file.slug]))
        else:
            form = form_class(user=request.user)

        return render_to_resp(request=request, template_name=template_name,
            context={'form':form})
    else:
        raise Http403


@is_enabled('help_files')
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
                msg_string = 'Successfully edited %s' % help_file
                messages.add_message(request, messages.SUCCESS, _(msg_string))

#                # send notification to administrator(s) and module recipient(s)
#                recipients = get_notice_recipients('module', 'help_files', 'helpfilerecipients')
#                # if recipients and notification:
#                     notification.send_emails(recipients,'help_file_added', {
#                         'object': help_file,
#                         'request': request,
#                     })

                return HttpResponseRedirect(reverse('help_file.details', args=[help_file.slug]))
        else:
            form = form_class(instance=help_file, user=request.user)

        return render_to_resp(request=request, template_name=template_name,
            context={'help_file': help_file, 'form':form})
    else:
        raise Http403


@is_enabled('help_files')
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
            messages.add_message(request, messages.INFO, _('Thanks for requesting a new help file!'))
            EventLog.objects.log()
            return HttpResponseRedirect(reverse('help_files'))
    else:
        form = RequestForm()

    return render_to_resp(request=request, template_name=template_name,
        context={'form': form})


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


@is_enabled('help_files')
def requests(request, template_name="help_files/request_list.html"):
    """
        Display a list of help file requests
    """
    if not has_perm(request.user, 'help_files.change_request'):
        raise Http403

    requests = Request.objects.all()
    EventLog.objects.log()
    return render_to_resp(request=request, template_name=template_name, context={
        'requests': requests,
        })


@is_enabled('help_files')
@login_required
def export(request, template_name="help_files/export.html"):
    """Export Help Files"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        fields = [
            'slug',
            'topics',
            'question',
            'answer',
            'level',
            'is_faq',
            'is_featured',
            'is_video',
            'syndicate',
            'view_totals',
        ]
        export_id = run_export_task('help_files', 'helpfile', fields)
        EventLog.objects.log()
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })
