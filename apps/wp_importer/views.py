import os.path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse 
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django import forms
from django.db import models
from wp_importer.forms import BlogImportForm
from wp_importer.models import BlogImport
from wp_importer.tasks import WPImportTask
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
from parse_uri import ParseUri
from djcelery.models import TaskMeta

from base.http import Http403
from perms.utils import has_perm, update_perms_and_save
from event_logs.models import EventLog

@login_required
def index(request, template_name="wp_importer/index.html"):
    if request.method == 'POST':
        form = BlogImportForm(request.POST, request.FILES)
        try:
            if form.is_valid() and request.FILES['blog'].name.endswith('xml') and request.FILES['blog'].size < 20*1024*1024 and request.user:
                upload = form.save(commit=False)
                upload.author = request.user
                upload = form.save()
                file_name = os.path.join(settings.MEDIA_ROOT, 'blogimport', request.FILES['blog'].name)
                
                result = WPImportTask.delay(file_name, request.user)
                #uncomment the next line if there is no celery server yet.
                #result.wait()
                
                return redirect("wp_importer.views.detail", result.task_id)
                
            elif not request.FILES['blog'].name.endswith('xml'):
                messages.add_message(
                    request,
                    messages.INFO,
                    _('Oops, only upload XML files!')
                )

            elif not request.FILES['blog'].size < 20*1024*1024:
                messages.add_message(
                    request,
                    messages.INFO,
                    _('Oops, only upload files smaller than 20 MB!')
                )
                
        except ValueError:
            messages.add_message(request, messages.INFO, 'Oops, please login before uploading a blog!')
            return redirect('auth_login')

    else:
        form = BlogImportForm()

    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))

@login_required
def detail(request, task_id, template_name="wp_importer/detail.html"):
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        #tasks database entries are not created at once.
        #instead of raising 404 we'll assume that there will be one for
        #the id.
        task = None
    
    if task and task.status == "SUCCESS":
        messages.add_message(
            request,
            messages.INFO,
            _('Your blog has been imported!')
        )
        return render_to_response(template_name, {},
            context_instance=RequestContext(request))
    
    messages.add_message(
        request,
        messages.INFO,
        _("Your site import is being processed. You will receive an email when the import is complete.")
    )
    
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))
