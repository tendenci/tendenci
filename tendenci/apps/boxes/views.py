from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.exports.utils import run_export_task


@is_enabled('boxes')
@login_required
def export(request, template_name="boxes/export.html"):
    """Export Boxes"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        fields = [
            'title',
            'content',
            'tags',
        ]
        export_id = run_export_task('boxes', 'box', fields)
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })
