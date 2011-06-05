from datetime import datetime, date
#from django.conf import settings
#from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from base.http import Http403
from perms.utils import has_perm, is_admin
from site_settings.utils import get_setting

from event_logs.models import EventLog

from corporate_memberships.models import (CorpApp, CorpField, CorporateMembership,CorporateMembershipType,
                                          CorporateMembershipRep, 
                                          CorpMembRenewEntry, 
                                          IndivMembRenewEntry)
from corporate_memberships.forms import CorpMembForm, CorpMembRepForm, RosterSearchForm, CorpMembRenewForm
from corporate_memberships.utils import (get_corporate_membership_type_choices, 
                                         get_payment_method_choices,
                                         corp_memb_inv_add, 
                                         dues_rep_emails_list)
#from memberships.models import MembershipType
from memberships.models import Membership

from perms.utils import get_notice_recipients
from base.utils import send_email_notification


def add(request, slug, template="corporate_memberships/add.html"):
    """
        add a corporate membership
    """ 
    corp_app = get_object_or_404(CorpApp, slug=slug)
    user_is_admin = is_admin(request.user)
    
    # if app requires login and they are not logged in, 
    # prompt them to log in and redirect them back to this add page
    if not request.user.is_authenticated():
        messages.add_message(request, messages.INFO, 'Please log in or sign up to the site before signing up the corporate membership.')
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
            inv = corp_memb_inv_add(request.user, corporate_membership)
            # update corp_memb with inv
            corporate_membership.invoice = inv
            corporate_membership.save()
            
            # send notification to administrators
            recipients = get_notice_recipients('module', 'corporatememberships', 'corporatemembershiprecipients')
            extra_context = {
                'object': corporate_membership,
                'request': request,
            }
            send_email_notification('corp_memb_added', recipients, extra_context)
            
            
            # log an event
            log_defaults = {
                'event_id' : 681000,
                'event_data': '%s (%d) added by %s' % (corporate_membership._meta.object_name, 
                                                       corporate_membership.pk, request.user),
                'description': '%s added' % corporate_membership._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': corporate_membership,
            }
            EventLog.objects.log(**log_defaults)
            
            # handle online payment
            if corporate_membership.payment_method.lower() in ['credit card', 'cc']:
                if corporate_membership.invoice and corporate_membership.invoice.balance > 0:
                    return HttpResponseRedirect(reverse('payments.views.pay_online', args=[corporate_membership.invoice.id, corporate_membership.invoice.guid])) 
            
            return HttpResponseRedirect(reverse('corp_memb.add_conf', args=[corporate_membership.id]))
        
    context = {"corp_app": corp_app, "field_objs": field_objs, 'form':form}
    return render_to_response(template, context, RequestContext(request))

@login_required
def add_conf(request, id, template="corporate_memberships/add_conf.html"):
    """
        add a corporate membership
    """ 
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
#    if not has_perm(request.user,'corporate_memberships.view_corporatemembership',corporate_membership):
#        raise Http403
    
    context = {"corporate_membership": corporate_membership}
    return render_to_response(template, context, RequestContext(request))

@login_required
def edit(request, id, template="corporate_memberships/edit.html"):
    """
        edit a corporate membership
    """ 
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corporate_membership):
        if not corporate_membership.allow_edit_by(request.user):
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
        field_obj.display_only = False
        
        # make corporate_membership_type and payment_method as the display_only fields
        # because we're not allowing them to edit those fields
        if field_obj.field_name in ['corporate_membership_type', 'payment_method']:
            field_obj.display_only = True
            if field_obj.field_name == 'corporate_membership_type':
                field_obj.display_content = corporate_membership.corporate_membership_type.name
                
            if field_obj.field_name == 'payment_method':
                field_obj.display_content = corporate_membership.payment_method
                if corporate_membership.invoice:
                    field_obj.display_content = '%s - <a href="%s">View Invoice</a>' % (field_obj.display_content,
                                                                                        corporate_membership.invoice.get_absolute_url)
        
    form = CorpMembForm(corporate_membership.corp_app, field_objs, request.POST or None, 
                        request.FILES or None, instance=corporate_membership)
    
    # add or delete fields based on the security level
    if user_is_admin:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', admin_only=1))
        field_objs.append(CorpField(label='Expiration Date', 
                                    field_name='expiration_dt', 
                                    admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', admin_only=1))
        field_objs.append(CorpField(label='status_detail', field_name='status_detail', admin_only=1))
    else:
        del form.fields['join_dt']
        del form.fields['expiration_dt']
        del form.fields['status']
        del form.fields['status_detail']
       
    
#    # corporate_membership_type choices
#    form.fields['corporate_membership_type'].choices = get_corporate_membership_type_choices(request.user, 
#                                                                                corp_app)
#    
#    form.fields['payment_method'].choices = get_payment_method_choices(request.user)
    
    # we don't need the captcha on edit because it requires login
    #del form.fields['captcha']
        
        
    if request.method == "POST":
        if form.is_valid():
            corporate_membership = form.save(request.user)
            
            # send notification to administrators
            if not user_is_admin:
                recipients = get_notice_recipients('module', 'corporate_membership', 'corporatemembershiprecipients')
                extra_context = {
                    'object': corporate_membership,
                    'request': request,
                }
                send_email_notification('corp_memb_edited', recipients, extra_context)
            
            # log an event
            log_defaults = {
                'event_id' : 682000,
                'event_data': '%s (%d) edited by %s' % (corporate_membership._meta.object_name, 
                                                       corporate_membership.pk, request.user),
                'description': '%s edited' % corporate_membership._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': corporate_membership,
            }
            EventLog.objects.log(**log_defaults)
            
            
            return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))
            
            
    
    context = {"corporate_membership": corporate_membership, 
               'corp_app': corp_app,
               'field_objs': field_objs, 
               'form':form}
    return render_to_response(template, context, RequestContext(request))

@login_required
def renew(request, id, template="corporate_memberships/renew.html"):
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corporate_membership):
        if not corporate_membership.allow_edit_by(request.user):
            raise Http403
        
    if corporate_membership.is_renewal_pending:
        messages.add_message(request, messages.INFO, 'The corporate membership "%s" has been renewed and is pending for admin approval.' % corporate_membership.name)
        return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))
        
    user_is_admin = is_admin(request.user)
    
    corp_app = corporate_membership.corp_app
    
    form = CorpMembRenewForm(request.POST or None, user=request.user, corporate_membership=corporate_membership)
    
    if request.method == "POST":
        if form.is_valid():
            if 'update_summary' in request.POST:
                pass
            else:
                
                members = form.cleaned_data['members']
                
                corp_renew_entry = form.save(commit=False)
                corp_renew_entry.corporate_membership = corporate_membership
                corp_renew_entry.creator = request.user
                corp_renew_entry.status_detail = 'pending'
                corp_renew_entry.save()
                
                # calculate the total price for invoice
                corp_renewal_price = corp_renew_entry.corporate_membership_type.renewal_price
                if not corp_renewal_price:
                    corp_renewal_price = 0
                indiv_renewal_price = corp_renew_entry.corporate_membership_type.membership_type.renewal_price
                if not indiv_renewal_price:
                    indiv_renewal_price = 0
                
                renewal_total = corp_renewal_price + indiv_renewal_price * len(members)
                opt_d = {'renewal':True, 
                         'renewal_total': renewal_total,
                         'renew_entry':corp_renew_entry}
                # create an invoice - invoice.object_type - use corporate_membership?
                inv = corp_memb_inv_add(request.user, corporate_membership, **opt_d)
                
                # update corp_renew_entry with inv
                corp_renew_entry.invoice = inv
                corp_renew_entry.save()
                
                corporate_membership.renew_entry_id = corp_renew_entry.id
                corporate_membership.save()
                
                # store individual members
                for id in members:
                    membership = Membership.objects.get(id=id)
                    ind_memb_renew_entry = IndivMembRenewEntry(corp_memb_renew_entry=corp_renew_entry,
                                                               membership=membership)
                    ind_memb_renew_entry.save()
                    
                # log an event
                log_defaults = {
                    'event_id' : 681001,
                    'event_data': '%s (%d) renewed by %s' % (corporate_membership._meta.object_name, 
                                                           corporate_membership.pk, request.user),
                    'description': '%s renewed' % corporate_membership._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': corporate_membership,
                }
                EventLog.objects.log(**log_defaults)
                
                
                # handle online payment
                if corp_renew_entry.payment_method.lower() in ['credit card', 'cc']:
                    if corp_renew_entry.invoice and corp_renew_entry.invoice.balance > 0:
                        return HttpResponseRedirect(reverse('payments.views.pay_online', 
                                                            args=[corp_renew_entry.invoice.id, 
                                                                  corp_renew_entry.invoice.guid]))
                        
                extra_context = {
                    'object': corporate_membership,
                    'request': request,
                    'corp_renew_entry': corp_renew_entry,
                    'invoice': inv,
                }
                if user_is_admin:
                    # admin: approve renewal
                    corporate_membership.approve_renewal(request)
                else:
                    # send a notice to admin
                    recipients = get_notice_recipients('module', 'corporatememberships', 'corporatemembershiprecipients')
                    
                    send_email_notification('corp_memb_renewed', recipients, extra_context)
                    
                   
                            
                # send an email to dues reps
                recipients = dues_rep_emails_list(corporate_membership)
                send_email_notification('corp_memb_renewed_user', recipients, extra_context)
                    
                    
                return HttpResponseRedirect(reverse('corp_memb.renew_conf', args=[corporate_membership.id]))
                
    
    
    summary_data = {'corp_price':0, 'individual_price':0, 'individual_count':0, 
                    'individual_total':0, 'total_amount':0}
    if request.method == "POST":
        cmt_id = request.POST.get('corporate_membership_type', 0)
        try:
            cmt = CorporateMembershipType.objects.get(id=cmt_id)
        except CorporateMembershipType.DoesNotExist:
            pass
        summary_data['individual_count'] = len(request.POST.getlist('members'))
    else:
        cmt = corporate_membership.corporate_membership_type
    
    if cmt:
        summary_data['corp_price'] = cmt.renewal_price
        if not summary_data['corp_price']:
            summary_data['corp_price'] = 0
        summary_data['individual_price'] = cmt.membership_type.renewal_price
        if not summary_data['individual_price']:
            summary_data['individual_price'] = 0
    summary_data['individual_total'] = summary_data['individual_count'] * summary_data['individual_price']
    summary_data['total_amount'] = summary_data['individual_total'] + summary_data['corp_price']
    
    context = {"corporate_membership": corporate_membership, 
               'corp_app': corp_app,
               'form': form,
               'summary_data': summary_data,
               }
    return render_to_response(template, context, RequestContext(request))

@login_required
def renew_conf(request, id, template="corporate_memberships/renew_conf.html"):
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corporate_membership):
        if not corporate_membership.allow_edit_by(request.user):
            raise Http403
        
    #user_is_admin = is_admin(request.user)
    
    corp_app = corporate_membership.corp_app
    
    try:
        renew_entry = CorpMembRenewEntry.objects.get(pk=corporate_membership.renew_entry_id)
    except CorpMembRenewEntry.DoesNotExist:
        renew_entry = None
    
    context = {"corporate_membership": corporate_membership, 
               'corp_app': corp_app,
               'renew_entry': renew_entry,
               }
    return render_to_response(template, context, RequestContext(request))


@login_required
def approve(request, id, template="corporate_memberships/approve.html"):
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    user_is_admin = is_admin(request.user)
    if not user_is_admin:
        raise Http403
    
    # if not in pending, go to view page
    if not (corporate_membership.is_pending):
        return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))

    try:
        renew_entry = CorpMembRenewEntry.objects.get(pk=corporate_membership.renew_entry_id)
    except CorpMembRenewEntry.DoesNotExist:
        renew_entry = None
        
    if renew_entry:
        indiv_renew_entries = renew_entry.indiv_memb_renew_entries()
        membership_type = renew_entry.corporate_membership_type.membership_type
        new_expiration_dt = membership_type.get_expiration_dt(renewal=True,
                                                join_dt=corporate_membership.join_dt,
                                                renew_dt=renew_entry.create_dt)
    else:
        indiv_renew_entries = None
        membership_type = corporate_membership.corporate_membership_type.membership_type
        new_expiration_dt = membership_type.get_expiration_dt(renewal=False,
                                                join_dt=corporate_membership.join_dt,
                                                renew_dt=corporate_membership.create_dt)
        
    if request.method == "POST":
        msg = ''
        if 'approve' in request.POST:
            if renew_entry:
                # approve the renewal
                corporate_membership.approve_renewal(request)
                # send an email to dues reps
                recipients = dues_rep_emails_list(corporate_membership)
                extra_context = {
                    'object': corporate_membership,
                    'request': request,
                    'corp_renew_entry': renew_entry,
                    'invoice': renew_entry.invoice,
                }
                send_email_notification('corp_memb_renewed_user', recipients, extra_context)
                msg = 'Corporate membership "%s" renewal has been APPROVED.' % corporate_membership.name
                
                event_id = 682002
                event_data = '%s (%d) renewal approved by %s' % (corporate_membership._meta.object_name, 
                                                                 corporate_membership.pk, request.user)
                event_description = '%s renewal approved' % corporate_membership._meta.object_name
                
            else:
                # approve join
                corporate_membership.approve_join(request)
                msg = 'Corporate membership "%s" has been APPROVED.' % corporate_membership.name
                event_id = 682001
                event_data = '%s (%d) approved by %s' % (corporate_membership._meta.object_name, 
                                                        corporate_membership.pk, request.user)
                event_description = '%s approved' % corporate_membership._meta.object_name
        else:
            if 'disapprove' in request.POST:
                if renew_entry:
                    # deny the renewal
                    corporate_membership.disapprove_renewal(request)
                    
                    msg = 'Corporate membership "%s" renewal has been DENIED.' % corporate_membership.name
                    event_id = 682004
                    event_data = '%s (%d) renewal denied by %s' % (corporate_membership._meta.object_name, 
                                                                 corporate_membership.pk, request.user)
                    event_description = '%s renewal denied' % corporate_membership._meta.object_name
                else:
                    # deny join
                    corporate_membership.disapprove_join(request)
                    msg = 'Corporate membership "%s" has been DENIED.' % corporate_membership.name
                    event_id = 682003
                    event_data = '%s (%d) denied by %s' % (corporate_membership._meta.object_name, 
                                                        corporate_membership.pk, request.user)
                    event_description = '%s denied' % corporate_membership._meta.object_name
                
        if msg:      
            messages.add_message(request, messages.INFO, msg)
            
            # log an event
            log_defaults = {
                'event_id' : event_id,
                'event_data': event_data,
                'description': event_description,
                'user': request.user,
                'request': request,
                'instance': corporate_membership,
            }
            EventLog.objects.log(**log_defaults)
                
        return HttpResponseRedirect(reverse('corp_memb.view', args=[corporate_membership.id]))
    
    
    context = {"corporate_membership": corporate_membership,
               'renew_entry': renew_entry,
               'indiv_renew_entries': indiv_renew_entries,
               'new_expiration_dt': new_expiration_dt,
               }
    return render_to_response(template, context, RequestContext(request))
    
    

def view(request, id, template="corporate_memberships/view.html"):
    """
        view a corporate membership
    """  
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    
    if not has_perm(request.user,'corporate_memberships.view_corporatemembership',corporate_membership):
        if not corporate_membership.allow_view_by(request.user):
            raise Http403
    
    can_edit = False
    if has_perm(request.user,'corporate_memberships.edit_corporatemembership',corporate_membership):
        can_edit = True
    
    user_is_admin = is_admin(request.user)
    
    field_objs = corporate_membership.corp_app.fields.filter(visible=1)
    if not user_is_admin:
        field_objs = field_objs.filter(admin_only=0)
    
    field_objs = list(field_objs.order_by('order'))
    
    if can_edit:
        field_objs.append(CorpField(label='Representatives', field_type='section_break', admin_only=0))
        field_objs.append(CorpField(label='Reps', field_name='reps', object_type='corporate_membership', admin_only=0))
        
        
    if user_is_admin:
        field_objs.append(CorpField(label='Admin Only', field_type='section_break', admin_only=1))
        field_objs.append(CorpField(label='Join Date', field_name='join_dt', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Expiration Date', field_name='expiration_dt', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Status', field_name='status', object_type='corporate_membership', admin_only=1))
        field_objs.append(CorpField(label='Status Detail', field_name='status_detail', object_type='corporate_membership', admin_only=1))
        
    for field_obj in field_objs:
        field_obj.value = field_obj.get_value(corporate_membership)
        if isinstance(field_obj.value, datetime) or isinstance(field_obj.value, date):
            field_obj.is_date = True
        else:
            field_obj.is_date = False
            
    
    context = {"corporate_membership": corporate_membership, 'field_objs': field_objs}
    return render_to_response(template, context, RequestContext(request))


def search(request, template_name="corporate_memberships/search.html"):
    allow_anonymous_search = get_setting('module', 'corporatememberships', 'allowanonymoussearchcorporatemember')
    if request.user.is_anonymous() and not allow_anonymous_search:
        raise Http403
    
    query = request.GET.get('q', None)
    corp_members = CorporateMembership.objects.search(query, user=request.user)
    
    corp_members = corp_members.order_by('name_exact')
    
    return render_to_response(template_name, {'corp_members': corp_members}, 
        context_instance=RequestContext(request))
    
    
@login_required
def delete(request, id, template_name="corporate_memberships/delete.html"):
    corp_memb = get_object_or_404(CorporateMembership, pk=id)

    if has_perm(request.user,'corporate_memberships.delete_corporatemembership'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 683000,
                'event_data': '%s (%d) deleted by %s' % (corp_memb._meta.object_name, corp_memb.pk, request.user),
                'description': '%s deleted' % corp_memb._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': corp_memb,
            }
            
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % corp_memb)
            
#            # send notification to administrators
#            recipients = get_notice_recipients('module', 'corporate_membership', 'corporatemembershiprecipients')
#            if recipients:
#                if notification:
#                    extra_context = {
#                        'object': corp_memb,
#                        'request': request,
#                    }
#                    notification.send_emails(recipients,'corp_memb_deleted', extra_context)
#            
            corp_memb.delete()
                
            return HttpResponseRedirect(reverse('corp_memb.search'))
    
        return render_to_response(template_name, {'corp_memb': corp_memb}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
    
def index(request, template_name="corporate_memberships/index.html"):
    corp_apps = CorpApp.objects.filter(status=1, status_detail='active').order_by('name')
    #cm_types = CorporateMembershipType.objects.filter(status=1, status_detail='active').order_by('-price')
    
    return render_to_response(template_name, {'corp_apps': corp_apps}, 
        context_instance=RequestContext(request))
    
    
def edit_reps(request, id, form_class=CorpMembRepForm, template_name="corporate_memberships/edit_reps.html"):
    corp_memb = get_object_or_404(CorporateMembership, pk=id)
    
    if not has_perm(request.user,'corporate_memberships.change_corporatemembership',corp_memb):
        raise Http403
    
    reps = CorporateMembershipRep.objects.filter(corporate_membership=corp_memb).order_by('user')
    form = form_class(corp_memb, request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            rep = form.save(commit=False)
            rep.corporate_membership = corp_memb
            rep.save()
            
            # log an event here
            
            if (request.POST.get('submit', '')).lower() == 'save':
                return HttpResponseRedirect(reverse('corp_memb.view', args=[corp_memb.id]))

    
    return render_to_response(template_name, {'corp_memb': corp_memb, 
                                              'form': form,
                                              'reps': reps}, 
        context_instance=RequestContext(request))
    
    
@login_required
def delete_rep(request, id, template_name="corporate_memberships/delete_rep.html"):
    rep = get_object_or_404(CorporateMembershipRep, pk=id)
    corp_memb = rep.corporate_membership

    if has_perm(request.user,'corporate_memberships.edit_corporatemembership'):   
        if request.method == "POST":
            
            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % rep)
            
            rep.delete()
                
            return HttpResponseRedirect(reverse('corp_memb.edit_reps', args=[corp_memb.pk]))
    
        return render_to_response(template_name, {'corp_memb': corp_memb}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required    
def roster_search(request, template_name='corporate_memberships/roster_search.html'):
    name = request.GET.get('name', None)
    corp_memb = get_object_or_404(CorporateMembership, name=name)
    
    query = request.GET.get('q', None)
    memberships = Membership.objects.corp_roster_search(query, user=request.user).filter(corporate_membership_id=corp_memb.id)
    
    if is_admin(request.user) or corp_memb.is_rep(request.user):
        pass
    else:
        memberships = memberships.filter(status=1, status_detail='active')
        
    # a list of corporate memberships for the drop down
    corp_members = CorporateMembership.objects.search(None, user=request.user).order_by('name_exact')
    name_choices = ((corp_member.name, corp_member.name) for corp_member in corp_members)
    form = RosterSearchForm(request.GET or None)
    form.fields['name'].choices = name_choices
    form.fields['name'].initial = corp_memb.name
        
    return render_to_response(template_name, {'corp_memb': corp_memb,
                                              'memberships': memberships, 
                                              'form': form}, 
            context_instance=RequestContext(request))
    
    


