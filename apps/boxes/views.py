from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from theme.shortcuts import themed_response as render_to_response
from base.http import Http403
from perms.utils import is_admin
from exports.utils import run_export_task

from boxes.models import Box

@login_required
def export(request, template_name="boxes/export.html"):
    """Export Boxes"""
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == 'POST':
        # initilize initial values
        file_name = "boxes.csv"
        fields = [
            'title',
            'content',
            'tags',
        ]
        export_id = run_export_task('boxes', 'box', fields)
        return redirect('export.status', export_id)
        
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
