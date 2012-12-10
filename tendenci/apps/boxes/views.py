from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.base.http import Http403
from tendenci.core.exports.utils import run_export_task
from tendenci.apps.redirects.models import Redirect
from tendenci.core.site_settings.utils import get_setting


@login_required
def export(request, template_name="boxes/export.html"):
    if not get_setting('module', 'boxes', 'enabled'):
        redirect = get_object_or_404(Redirect, from_app='boxes')
        return HttpResponseRedirect('/' + redirect.to_url)

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

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
