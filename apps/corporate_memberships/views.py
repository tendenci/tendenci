#from django.conf import settings
#from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from base.http import Http403
from perms.utils import has_perm, is_admin

from corporate_memberships.models import CorpApp, CorpField, CorporateMembership
from corporate_memberships.forms import CorpMembForm
from corporate_memberships.utils import get_corporate_membership_type_choices, get_payment_method_choices


@login_required
def add(request, slug, template="corporate_memberships/add.html"):
    """
        add a corporate membership
    """ 
    corp_app = get_object_or_404(CorpApp, slug=slug)
    user_is_admin = is_admin(request.user)

    #if not has_perm(request.user,'corporate_memberships.view_corpapp',corp_app):
    #    raise Http403
    
    field_objs = corp_app.fields.filter(visible=1)
    if not user_is_admin:
        field_objs = field_objs.filter(admin_only=0)
    
    field_objs = list(field_objs.order_by('order'))
    
    form = CorpMembForm(corp_app, field_objs, request.POST or None, request.FILES or None)
    
    # corporate_membership_type choices
    form.fields['corporate_membership_type'].choices = get_corporate_membership_type_choices(request.user, corp_app)
    
    form.fields['payment_method'].choices = get_payment_method_choices(request.user)
    
    if user_is_admin:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', admin_only=1))
        field_objs.append(CorpField(label='status_detail', field_name='status_detail', admin_only=1))
    else:
        del form.fields['join_dt']
        del form.fields['status']
        del form.fields['status_detail']
    
    if corp_app.use_captcha and (not user_is_admin):
        field_objs.append(CorpField(label='Type the code below', field_name='captcha'))
    else:
        del form.fields['captcha']
    #print form.fields['corporate_membership_type'].choices 
    if request.method == "POST":
        if form.is_valid():
            corporate_membership = form.save(request.user)
            
            return HttpResponseRedirect(reverse('corp_memb.add_conf', args=[corporate_membership.id]))
        
    context = {"corp_app": corp_app, "field_objs": field_objs, 'form':form}
    return render_to_response(template, context, RequestContext(request))

@login_required
def add_conf(request, id, template="corporate_memberships/add_conf.html"):
    """
        add a corporate membership
    """ 
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    context = {"corporate_membership": corporate_membership}
    return render_to_response(template, context, RequestContext(request))
    


