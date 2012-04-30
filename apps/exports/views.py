from datetime import datetime
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from djcelery.models import TaskMeta
from perms.utils import is_admin
from base.http import Http403

@login_required
def status(request, task_id, template_name='exports/export_status.html'):
    """Checks if an export is completed.
    """
    if not is_admin(request.user):
        raise Http403
    
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        # task's database entries are not created at once
        # so we do not raise an Http404, we just assume they exist.
        task = None
    
    return render_to_response(template_name, {
        'task': task,
        'datetime':datetime,
    }, context_instance=RequestContext(request))

@login_required
def download(request, task_id):
    """Returns the export file if it exists"""
    
    if not is_admin(request.user):
        raise Http403
    
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        return redirect("export.download", task_id)
        
    if task and task.status == "SUCCESS":
        response = task.result
        return response
    
    return redirect("export.download", task_id)
