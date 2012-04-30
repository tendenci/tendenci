from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from theme.shortcuts import themed_response as render_to_response
from base.http import Http403
from perms.utils import is_admin
from exports.tasks import TendenciExportTask

from boxes.models import Box

@login_required
def export(request, template_name="boxes/export.html"):
    """Export Boxes"""
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == 'POST':
        # initilize initial values
        file_name = "boxs.xls"
        fields = [
            'title',
            'content',
            'tags',
        ]
        
        if not settings.CELERY_IS_ACTIVE:
            # if celery server is not present 
            # evaluate the result and render the results page
            result = TendenciExportTask()
            response = result.run(Box, fields, file_name)
            return response
        else:
            result = TendenciExportTask.delay(Box, fields, file_name)
            return redirect('export.status', result.task_id)
        
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
