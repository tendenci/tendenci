#from django.conf import settings
#from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required

from base.http import Http403
from perms.utils import has_perm

from corporate_memberships.models import CorpApp
#from corporate_memberships.forms import CorpAppPreviewForm


@login_required
def preview(request, slug, template="corporate_memberships/preview.html"):
    """
        preview the built form
    """ 
    corp_app = get_object_or_404(CorpApp, slug=slug)

    if not has_perm(request.user,'corporate_memberships.view_corpapp',corp_app):
        raise Http403
    
    #form = CorpAppPreviewForm(corp_app)
    fields = corp_app.fields.filter(visible=1).order_by('order')
    
    context = {"corp_app": corp_app, "fields": fields}
    return render_to_response(template, context, RequestContext(request))