import os.path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django import forms
from django.db import models
from wp_importer.forms import BlogImportForm
from wp_importer.models import BlogImport
from wp_importer.utils import run
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
from parse_uri import ParseUri

from base.http import Http403
from perms.utils import has_perm, update_perms_and_save
from event_logs.models import EventLog

def index(request, template_name="wp_importer/index.html"):
    if request.method == 'POST':
        form = BlogImportForm(request.POST, request.FILES)
        if form.is_valid() and request.FILES['blog'].name.endswith('xml') and request.FILES['blog'].size < 20*1024*1024:
            upload = form.save(commit=False)
            upload.author = request.user
            upload = form.save()

            file_name = 'site_media/media/blogimport/' + request.FILES['blog'].name
            run(file_name, request)

            messages.add_message(
                request,
                messages.INFO,
                _('Your blog has been imported!')
            )

            return HttpResponseRedirect('detail/')
    
    else:
        form = BlogImportForm()

    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))

def detail(request, template_name="wp_importer/detail.html"):
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))