#from django.conf import settings
#from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required

from base.http import Http403
from perms.utils import has_perm

from corporate_memberships.models import CorpApp, CorpField
from corporate_memberships.forms import CorpMembForm
from corporate_memberships.utils import get_corporate_membership_type_choices, get_payment_method_choices


@login_required
def add(request, slug, template="corporate_memberships/add.html"):
    """
        add a corporate membership
    """ 
    corp_app = get_object_or_404(CorpApp, slug=slug)

    if not has_perm(request.user,'corporate_memberships.view_corpapp',corp_app):
        raise Http403
    
    field_objs = list(corp_app.fields.filter(visible=1).order_by('order'))
    
    form = CorpMembForm(corp_app, field_objs, request.POST or None, request.FILES or None)
    
    if request.method == "POST":
        pass
    # corporate_membership_type choices
    form.fields['corporate_membership_type'].choices = get_corporate_membership_type_choices(request.user, corp_app)
    
    form.fields['payment_method'].choices = get_payment_method_choices(request.user)
    
    if not corp_app.use_captcha:
        del form.fields['captcha']
    else:
        field_objs.append(CorpField(label='Type the code below', field_name='captcha'))

    context = {"corp_app": corp_app, "field_objs": field_objs, 'form':form}
    return render_to_response(template, context, RequestContext(request))