from datetime import datetime, date
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
from memberships.models import MembershipType


def add(request, slug, template="corporate_memberships/add.html"):
    """
        add a corporate membership
    """ 
    corp_app = get_object_or_404(CorpApp, slug=slug)
    user_is_admin = is_admin(request.user)
    
    # if app requires login and they are not logged in, 
    # prompt them to log in and redirect them back to this add page
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (reverse('auth_login'), reverse('corp_memb.add', args=[corp_app.slug])))
    
    if not user_is_admin and corp_app.status <> 1 and corp_app.status_detail <> 'active':
        raise Http403

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
    
    # add an admin only block for admin
    if user_is_admin:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', admin_only=1))
        field_objs.append(CorpField(label='status_detail', field_name='status_detail', admin_only=1))
    else:
        del form.fields['join_dt']
        del form.fields['status']
        del form.fields['status_detail']
    del form.fields['expiration_dt']
    
    # captcha
    #if corp_app.use_captcha and (not request.user.is_authenticated()):
    #    field_objs.append(CorpField(label='Type the code below', field_name='captcha'))
    #else:
    #    del form.fields['captcha']
    
    if request.method == "POST":
        if form.is_valid():
            corporate_membership = form.save(request.user)
            
            # calculate the expiration
            memb_type = corporate_membership.corporate_membership_type.membership_type
            corporate_membership.expiration_dt = memb_type.get_expiration_dt(join_dt=corporate_membership.join_dt)
            corporate_membership.save()
            
            # generate invoice
            
            # email admin
            
            # log an event
            
            # handle online payment
            
            return HttpResponseRedirect(reverse('corp_memb.add_conf', args=[corporate_membership.id]))
        
    context = {"corp_app": corp_app, "field_objs": field_objs, 'form':form}
    return render_to_response(template, context, RequestContext(request))

def add_conf(request, id, template="corporate_memberships/add_conf.html"):
    """
        add a corporate membership
    """ 
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.view_corporatemembership',corporate_membership):
        raise Http403
    
    context = {"corporate_membership": corporate_membership}
    return render_to_response(template, context, RequestContext(request))

@login_required
def edit(request, id, template="corporate_memberships/edit.html"):
    """
        edit a corporate membership
    """ 
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corporate_membership):
        raise Http403
    
    user_is_admin = is_admin(request.user)
    
    corp_app = corporate_membership.corp_app
    
    # get the list of field objects for this corporate membership
    field_objs = corp_app.fields.filter(visible=1)
    if not user_is_admin:
        field_objs = field_objs.filter(admin_only=0)
    
    field_objs = list(field_objs.order_by('order'))
    
    # get the field entry for each field_obj if exists
    for field_obj in field_objs:
        field_obj.entry = field_obj.get_entry(corporate_membership)
        
    form = CorpMembForm(corporate_membership.corp_app, field_objs, request.POST or None, 
                        request.FILES or None, instance=corporate_membership)
    
    # add or delete fields based on the security level
    if user_is_admin:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', admin_only=1))
        field_objs.append(CorpField(label='Expiration Date', field_name='expiration_dt', admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', admin_only=1))
        field_objs.append(CorpField(label='status_detail', field_name='status_detail', admin_only=1))
    else:
        del form.fields['join_dt']
        del form.fields['expiration_dt']
        del form.fields['status']
        del form.fields['status_detail']
       
    
    # corporate_membership_type choices
    form.fields['corporate_membership_type'].choices = get_corporate_membership_type_choices(request.user, 
                                                                                corp_app)
    
    form.fields['payment_method'].choices = get_payment_method_choices(request.user)
    
    # we don't need the captcha on edit because it requires login
    #del form.fields['captcha']
        
        
    if request.method == "POST":
        if form.is_valid():
            corporate_membership = form.save(request.user)
            
            # email admin
            
            # log an event
            
            
            return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))
            
            
    
    context = {"corporate_membership": corporate_membership, 
               'corp_app': corp_app,
               'field_objs': field_objs, 
               'form':form}
    return render_to_response(template, context, RequestContext(request))



def view(request, id, template="corporate_memberships/view.html"):
    """
        view a corporate membership
    """  
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.view_corporatemembership',corporate_membership):
        raise Http403
    
    user_is_admin = is_admin(request.user)
    
    field_objs = corporate_membership.corp_app.fields.filter(visible=1)
    if not user_is_admin:
        field_objs = field_objs.filter(admin_only=0)
    
    field_objs = list(field_objs.order_by('order'))
    
    if user_is_admin:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Expiration Date', field_name='expiration_dt', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='status_detail', field_name='status_detail', object_type='corporate_membership', admin_only=1))
        
    for field_obj in field_objs:
        field_obj.value = field_obj.get_value(corporate_membership)
        if isinstance(field_obj.value, datetime) or isinstance(field_obj.value, date):
            field_obj.is_date = True
        else:
            field_obj.is_date = False
    
    context = {"corporate_membership": corporate_membership, 'field_objs': field_objs}
    return render_to_response(template, context, RequestContext(request))
    


