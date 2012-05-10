import os
from datetime import datetime, date
import csv
import operator
from hashlib import md5

from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
from django.utils import simplejson
from django.db.models import Q

from imports.utils import render_excel

from base.http import Http403
from perms.utils import has_perm, is_admin, is_member
from event_logs.models import EventLog

from corporate_memberships.models import (CorpApp, CorpField, CorporateMembership,
                                          CorporateMembershipType,
                                          CorporateMembershipRep, 
                                          Creator,
                                          CorpMembRenewEntry, 
                                          IndivMembRenewEntry,
                                          CorpFieldEntry,
                                          AuthorizedDomain)
from corporate_memberships.forms import (CorpMembForm, 
                                         CreatorForm,
                                         CorpApproveForm,
                                         CorpMembRepForm, 
                                         RosterSearchForm, 
                                         CorpMembRenewForm,
                                         CSVForm,
                                         ExportForm)
from corporate_memberships.utils import (get_corporate_membership_type_choices,
                                         get_payment_method_choices,
                                         corp_memb_inv_add, 
                                         dues_rep_emails_list,
                                         corp_memb_update_perms,
                                         validate_import_file,
                                         new_corp_mems_from_csv,
                                         get_over_time_stats,
                                         get_summary)
#from memberships.models import MembershipType
from memberships.models import Membership

from perms.utils import get_notice_recipients
from base.utils import send_email_notification
from files.models import File
from profiles.models import Profile
from corporate_memberships.settings import use_search_index, allow_anonymous_search, allow_member_search
from site_settings.utils import get_setting


def add_pre(request, slug, template='corporate_memberships/add_pre.html'):
    corp_app = get_object_or_404(CorpApp, slug=slug)
    form = CreatorForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            creator = form.save()
            hash = md5('%d.%s' % (creator.id, creator.email)).hexdigest()
            creator.hash = hash
            creator.save()
            
            # redirect to add
            return HttpResponseRedirect(reverse('corp_memb.anonymous_add', args=[slug, hash]))
    
    context = {"form": form,
               'corp_app': corp_app}
    return render_to_response(template, context, RequestContext(request))
    
    
    

def add(request, slug=None, hash=None, template="corporate_memberships/add.html"):
    """
        add a corporate membership
        admin - active
        user - if paid, active, otherwise, pending 
    """ 
    corp_app = get_object_or_404(CorpApp, slug=slug)
    user_is_admin = is_admin(request.user)
    
    if not user_is_admin and corp_app.status <> 1 and corp_app.status_detail <> 'active':
        raise Http403

    creator = None
    if not request.user.is_authenticated():
#        # if app requires login and they are not logged in, 
#        # prompt them to log in and redirect them back to this add page
#        messages.add_message(request, messages.INFO, 'Please log in or sign up to the site before signing up the corporate membership.')
#        return HttpResponseRedirect('%s?next=%s' % (reverse('auth_login'), reverse('corp_memb.add', args=[corp_app.slug])))
        # anonymous user - check if they have entered contact info
        if hash:
            [creator] = Creator.objects.filter(hash=hash)[:1] or [None]
        if not creator:
            # anonymous user - redirect them to enter their contact email before processing
            return HttpResponseRedirect(reverse('corp_memb.add_pre', args=[slug]))

    field_objs = corp_app.fields.filter(visible=1)
    if not user_is_admin:
        field_objs = field_objs.filter(admin_only=0)
    
    field_objs = list(field_objs.order_by('order'))
    
    form = CorpMembForm(corp_app, field_objs, request.POST or None, request.FILES or None)
    
    # corporate_membership_type choices
    form.fields['corporate_membership_type'].choices = get_corporate_membership_type_choices(request.user, corp_app)
    
    form.fields['payment_method'].choices = get_payment_method_choices(request.user, corp_app)
    
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
            if creator:
                corporate_membership = form.save(request.user, creator=creator)
            else:
                corporate_membership = form.save(request.user)
            if creator:
                corporate_membership.anonymous_creator = creator
            
            # calculate the expiration
            corp_memb_type = corporate_membership.corporate_membership_type
            corporate_membership.expiration_dt = corp_memb_type.get_expiration_dt(join_dt=corporate_membership.join_dt)
            
            #if corp_app.authentication_method == 'secret_code':
            # assign a secret code for this corporate
            # secret code is a unique 6 characters long string
            corporate_membership.assign_secret_code()
            corporate_membership.save()
            
            # generate invoice
            inv = corp_memb_inv_add(request.user, corporate_membership)
            # update corp_memb with inv
            corporate_membership.invoice = inv
            corporate_membership.save()
            
            # assign object permissions
            if not creator:
                corp_memb_update_perms(corporate_membership)
            
            # email to user who created the corporate membership
            # include the secret code in the email if authentication_method == 'secret_code'
            
            # send notification to user
            if creator:
                recipients = [creator.email]
            else:
                recipients = [request.user.email]
            extra_context = {
                'object': corporate_membership,
                'request': request,
                'invoice': inv,
            }
            send_email_notification('corp_memb_added_user', recipients, extra_context)
                        
            # send notification to administrators
            recipients = get_notice_recipients('module', 'corporatememberships', 'corporatemembershiprecipients')
            extra_context = {
                'object': corporate_membership,
                'request': request,
                'creator': creator
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
            #if corporate_membership.payment_method.lower() in ['credit card', 'cc']:
            if corporate_membership.payment_method.is_online:
                if corporate_membership.invoice and corporate_membership.invoice.balance > 0:
                    return HttpResponseRedirect(reverse('payments.views.pay_online', args=[corporate_membership.invoice.id, corporate_membership.invoice.guid])) 
            
            return HttpResponseRedirect(reverse('corp_memb.add_conf', args=[corporate_membership.id]))
        
    context = {"corp_app": corp_app, "field_objs": field_objs, 'form':form}
    return render_to_response(template, context, RequestContext(request))


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
                                                                                        corporate_membership.invoice.get_absolute_url())
        
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
#    form.fields['payment_method'].choices = get_payment_method_choices(request.user, corp_app)
    
    # we don't need the captcha on edit because it requires login
    #del form.fields['captcha']
    
    status_info_before_edit = {'corporate_membership_type': corporate_membership.corporate_membership_type,
                               'status': corporate_membership.status,
                               'status_detail': corporate_membership.status_detail}
    old_corp_memb = CorporateMembership.objects.get(pk=corporate_membership.pk)
        
    if request.method == "POST":
        if form.is_valid():
            corporate_membership = form.save(request.user, commit=False)
            # archive the corporate membership if any of these changed:
            # corporate_membership_type, status, status_detail
            need_archive = False
            for key in status_info_before_edit:
                value = getattr(corporate_membership, key)

                if value != status_info_before_edit[key]:
                    need_archive = True
                    break
            if need_archive:
                old_corp_memb.archive(request.user)
            corporate_membership.save()
            corp_memb_update_perms(corporate_membership)
            
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
                if corp_renew_entry.get_payment_method().is_online:
                #if corp_renew_entry.payment_method.lower() in ['credit card', 'cc']:
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
        corp_membership_type = renew_entry.corporate_membership_type
        new_expiration_dt = corp_membership_type.get_expiration_dt(renewal=True,
                                                join_dt=corporate_membership.join_dt,
                                                renew_dt=renew_entry.create_dt)
    else:
        indiv_renew_entries = None
        corp_membership_type = corporate_membership.corporate_membership_type
        new_expiration_dt = corp_membership_type.get_expiration_dt(renewal=False,
                                                join_dt=corporate_membership.join_dt,
                                                renew_dt=corporate_membership.create_dt)
        
    approve_form = CorpApproveForm(request.POST or None, corporate_membership=corporate_membership)
    if request.method == "POST":
        if approve_form.is_valid():
            msg = ''
            if 'approve' in request.POST:
                if renew_entry:
                    # approve the renewal
                    corporate_membership.approve_renewal(request)
                   
                    msg = 'Corporate membership "%s" renewal has been APPROVED.' % corporate_membership.name
                    
                    event_id = 682002
                    event_data = '%s (%d) renewal approved by %s' % (corporate_membership._meta.object_name, 
                                                                     corporate_membership.pk, request.user)
                    event_description = '%s renewal approved' % corporate_membership._meta.object_name
                    
                else:
                    # approve join
                    params = {'create_new': True,
                              'assign_to_user': None}
                    if approve_form.fields and corporate_membership.anonymous_creator:
                        user_pk = int(approve_form.cleaned_data['users'])
                        if user_pk:
                            try:
                                params['assign_to_user'] = User.objects.get(pk=user_pk)
                                params['create_new'] = False
                            except User.DoesNotExist:
                                pass  

                    corporate_membership.approve_join(request, **params)
                    
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
                messages.add_message(request, messages.SUCCESS, msg)
                
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
               'approve_form': approve_form,
               }
    return render_to_response(template, context, RequestContext(request))
    
    

def view(request, id, template="corporate_memberships/view.html"):
    """
        view a corporate membership
    """  
    corporate_membership = get_object_or_404(CorporateMembership, id=id)
    corporate_membership.status_detail = corporate_membership.real_time_status_detail
    
    if not has_perm(request.user, 'corporate_memberships.view_corporatemembership', corporate_membership):
        if not corporate_membership.allow_view_by(request.user):
            raise Http403
    
    can_edit = False
    if has_perm(request.user, 'corporate_memberships.change_corporatemembership', corporate_membership):
        can_edit = True
    
    user_is_admin = is_admin(request.user)
    
    field_objs = corporate_membership.corp_app.fields.filter(visible=1)
    if not user_is_admin:
        field_objs = field_objs.filter(admin_only=0)
    if not can_edit:
        field_objs = field_objs.exclude(field_name='corporate_membership_type')
    
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
    if not request.user.is_authenticated() and not allow_anonymous_search:
        raise Http403
    
    query = request.GET.get('q', None)
    
    filter_and, filter_or = CorporateMembership.get_search_filter(request.user)
    q_obj = None
    if filter_and:
        q_obj = Q(**filter_and)
    if filter_or:
        q_obj_or = reduce(operator.or_, [Q(**{key: value}) for key, value in filter_or.items()])
        if q_obj:
            q_obj = reduce(operator.and_, [q_obj, q_obj_or])
        else:
            q_obj = q_obj_or
    
    if get_setting('site', 'global', 'searchindex') and query:
        corp_members = CorporateMembership.objects.search(query, user=request.user)
        if q_obj:
            corp_members = corp_members.filter(q_obj)
        corp_members = corp_members.order_by('name_exact')
    else:
        if q_obj:
            corp_members = CorporateMembership.objects.filter(q_obj)
        else:
            corp_members = CorporateMembership.objects.all()
    
#        if request.user.is_authenticated():
#            corp_members = corp_members.select_related()
            
        
        corp_members = corp_members.order_by('name')
    
    log_defaults = {
        'event_id': 684000,
        'event_data': '%s searched by %s' % ('Corporate memberships', request.user),
        'description': '%s searched' % 'Corporate memberships',
        'user': request.user,
        'request': request,
        'source': 'corporatemembership'
    }
    EventLog.objects.log(**log_defaults)
    
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
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % corp_memb)
            
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
            
            corp_memb_update_perms(corp_memb)
            
            # this is to update the search index for corporate memberships
            if use_search_index:
                corp_memb.save()
            
            # log an event here
            
            if (request.POST.get('submit', '')).lower() == 'save':
                return HttpResponseRedirect(reverse('corp_memb.view', args=[corp_memb.id]))
    
    if use_search_index:        
        memberships = Membership.objects.corp_roster_search(None, 
                                                user=request.user).filter(
                                            corporate_membership_id=corp_memb.id)
    else:
        memberships = Membership.objects.filter(
                                            corporate_membership_id=corp_memb.id)
    try:
        page = int(request.GET.get('page', 0))
    except:
        page = 0
    
    return render_to_response(template_name, {'corp_memb': corp_memb, 
                                              'form': form,
                                              'reps': reps,
                                              'memberships': memberships,
                                              'page': page}, 
        context_instance=RequestContext(request))
    
def reps_lookup(request):
    q = request.REQUEST['term']
    
    if use_search_index:
        profiles = Profile.objects.search(
                            q, 
                            user=request.user
                            ).order_by('last_name_exact')
    else:
        # they don't have search index, probably just check username only for performance sake
        profiles = Profile.objects.filter(Q(user__first_name__istartswith=q) \
                                       | Q(user__last_name__istartswith=q) \
                                       | Q(user__username__istartswith=q) \
                                       | Q(user__email__istartswith=q))
        profiles  = profiles.order_by('user__last_name')
        
    if profiles and len(profiles) > 10:
        profiles = profiles[:10]

    if use_search_index:
        users = [p.object.user for p in profiles]
    else:
        users = [p.user for p in profiles]
         
    results = []
    for u in users:
        value = '%s, %s (%s) - %s' % (u.last_name, u.first_name, u.username, u.email)
        u_dict = {'id': u.id, 'label': value, 'value': value}
        results.append(u_dict)
    return HttpResponse(simplejson.dumps(results),mimetype='application/json')
    
@login_required
def delete_rep(request, id, template_name="corporate_memberships/delete_rep.html"):
    rep = get_object_or_404(CorporateMembershipRep, pk=id)
    corp_memb = rep.corporate_membership

    if corp_memb.allow_edit_by(request.user) or \
         has_perm(request.user,'corporate_memberships.edit_corporatemembership'):   
        if request.method == "POST":
            
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % rep)
            
            rep.delete()
            corp_memb_update_perms(corp_memb)
            
            # this is to update the search index for corporate memberships
            if use_search_index:
                corp_memb.save()
                
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
    if use_search_index:
        memberships = Membership.objects.corp_roster_search(query, user=request.user).filter(corporate_membership_id=corp_memb.id)
    else:
        memberships = Membership.objects.filter(
                                            corporate_membership_id=corp_memb.id)
        
    if is_admin(request.user) or corp_memb.is_rep(request.user):
        pass
    else:
        memberships = memberships.filter(status=1, status_detail='active')
        
    # a list of corporate memberships for the drop down
    #corp_members = CorporateMembership.objects.search(None, user=request.user).order_by('name_exact')
    #name_choices = ((corp_member.name, corp_member.name) for corp_member in corp_members)
    form = RosterSearchForm(request.GET or None)
    #form.fields['name'].choices = name_choices
    form.fields['name'].initial = corp_memb.name
        
    return render_to_response(template_name, {'corp_memb': corp_memb,
                                              'memberships': memberships, 
                                              'form': form}, 
            context_instance=RequestContext(request))
    
    
@staff_member_required
def corp_import(request, step=None):
    """
    Corporate membership import.
    """
    #if not is_admin(request.user):  # admin only page
    #    raise Http403

    if not step:  # start from beginning
        return redirect('corp_memb_import_upload_file')
    
    request.session.set_expiry(0)  # expire when browser is closed
    step_numeral, step_name = step

    if step_numeral == 1:  # upload-file
        template_name = 'corporate_memberships/import/upload_file.html'
        err_msg = ""
        if request.method == 'POST':
            form = CSVForm(request.POST, request.FILES, step=step)
            if form.is_valid():
                cleaned_data = form.save(step=step)
                corp_app = cleaned_data['corp_app']

                # check import requirements
                saved_files = File.objects.save_files_for_instance(request, CorporateMembership)
                file_path = os.path.join(settings.MEDIA_ROOT, str(saved_files[0].file))
                is_valid_import, missing_required_fields = validate_import_file(file_path)
                
                if is_valid_import:
                    # store session info
                    request.session['corp_memb.import.corp_app'] = corp_app
                    request.session['corp_memb.import.file_path'] = file_path
                    request.session['corp_memb.import.update_option'] = cleaned_data['update_option']
    
                    # move to next wizard page
                    return redirect('corp_memb_import_map_fields')
                else:
                    err_msg = 'The CSV File is missing required field(s): %s' % (', '.join(missing_required_fields))
        else:  # if not POST
            form = CSVForm(step=step)

        return render_to_response(template_name, {
            'form':form,
            'datetime':datetime,
            'err_msg': err_msg
            }, context_instance=RequestContext(request))
        
    if step_numeral == 2:  # map-fields
        template_name = 'corporate_memberships/import/map_fields.html'
        file_path = request.session.get('corp_memb.import.file_path')
        corp_app = request.session.get('corp_memb.import.corp_app')
        update_option = request.session.get('corp_memb.import.update_option')
        
        if not all([corp_app, file_path, update_option]):
            return redirect('corp_memb_import_upload_file')

        if request.method == 'POST':
            form = CSVForm(
                request.POST,
                request.FILES,
                step=step,
                corp_app=corp_app,
                file_path=file_path
            )

            if form.is_valid():
                cleaned_data = form.save(step=step)
                file_path = request.session.get('corp_memb.import.file_path')

                corp_membs = new_corp_mems_from_csv(request, file_path, corp_app, cleaned_data, update_option)

                request.session['corp_memb.import.corp_membs'] = corp_membs
                request.session['corp_memb.import.fields'] = cleaned_data

                return redirect('corp_memb_import_preview')

        else:  # if not POST
            form = CSVForm(step=step, corp_app=corp_app, file_path=file_path)

        return render_to_response(template_name, {
            'form':form,
            'datetime':datetime,
            }, context_instance=RequestContext(request))
        
    if step_numeral == 3:  # preview
        template_name = 'corporate_memberships/import/preview.html'
        corp_membs = request.session.get('corp_memb.import.corp_membs')
        update_option = request.session.get('corp_memb.import.update_option')
        if not all([corp_membs, update_option]):
            return redirect('corp_memb_import_upload_file')

        added, skipped, updated, updated_override, invalid_skipped = [], [], [], [], []
        for corp_memb in corp_membs:
            if not corp_memb.is_valid:
                invalid_skipped.append(corp_memb)
            else:
                if corp_memb.pk:
                    if update_option == 'skip': 
                        skipped.append(corp_memb)
                    else:
                        if update_option == 'update':
                            updated.append(corp_memb)
                        else:
                            updated_override.append(corp_memb)
                else: 
                    added.append(corp_memb)

        return render_to_response(template_name, {
        'corp_membs':corp_membs,
        'added': added,
        'update_option': update_option,
        'invalid_skipped': invalid_skipped,
        'skipped': skipped,
        'updated': updated,
        'updated_override': updated_override,
        'datetime': datetime,
        }, context_instance=RequestContext(request))
        
    if step_numeral == 4:  # confirm
        template_name = 'corporate_memberships/import/confirm.html'

        corp_app = request.session.get('corp_memb.import.corp_app')
        corp_membs = request.session.get('corp_memb.import.corp_membs')
        fields_dict = request.session.get('corp_memb.import.fields')
        update_option = request.session.get('corp_memb.import.update_option')
        file_path = request.session.get('corp_memb.import.file_path')

        if not all([corp_app, corp_membs, fields_dict]):
            return redirect('corp_memb_import_upload_file')

        added, skipped, updated, updated_override, invalid_skipped = [], [], [], [], []
        field_keys = [item[0] for item in fields_dict.items() if item[1]]
        
        for corp_memb in corp_membs:
            if not corp_memb.is_valid:
                invalid_skipped.append(corp_memb)
                
                continue
            
            is_insert = False
            if not corp_memb.pk: 
                corp_memb.save()  # create pk
                is_insert = True
                added.append(corp_memb)
            else:
                if update_option == 'skip': 
                    skipped.append(corp_memb)
                else:
                    if update_option == 'update':
                        updated.append(corp_memb)
                    else:
                        updated_override.append(corp_memb)
                        
                    corp_memb.save()
                        
            if not is_insert and update_option == 'skip':
                continue
                
            # take care of authorized_domains and dues_rep
            # and add custom fields to the field entry
            for field_key in field_keys:
                if not hasattr(corp_memb, field_key):
                    if field_key in ['authorized_domains', 'dues_rep']:
                        if field_key == 'authorized_domains':
                            # if auth domains exist for this corp memb
                            #     if update_option == 'update', skip
                            #     if update_option == 'override',
                            #            1) delete existing auth domains
                            if not is_insert:
                                existing_auth_domains = AuthorizedDomain.objects.filter(
                                                        corporate_membership=corp_memb)
                                if existing_auth_domains:
                                    if update_option == 'update':
                                        continue
                                    elif update_option == 'override':
                                        # delete existing auth domains
                                        for auth_domain in existing_auth_domains:
                                            auth_domain.delete()
                                    
                            # add new auth domains
                            domains = (corp_memb.cm[field_key]).split(',')
                            domains = [domain.strip() for domain in domains]
                            for domain in domains:
                                AuthorizedDomain.objects.create(
                                         corporate_membership=corp_memb,
                                         name= domain      
                                                            )
                        if field_key == 'dues_rep':
                            # same as auth domains, check for existing dues reps
                            if not is_insert:
                                existing_dues_reps = CorporateMembershipRep.objects.filter(
                                                                corporate_membership=corp_memb,
                                                                is_dues_rep=True
                                                                    )
                                if existing_dues_reps:
                                    if update_option == 'update':
                                        continue
                                    elif update_option == 'override':
                                        # delete existing auth domains
                                        for dues_rep in existing_dues_reps:
                                            dues_rep.delete()
                            
                            # add new dues_reps
                            usernames = (corp_memb.cm[field_key]).split(',')
                            usernames = [username.strip() for username in usernames]
                            for username in usernames:
                                try:
                                    tmp_user = User.objects.get(username=username)
                                except User.DoesNotExist:
                                    continue
                                
                                CorporateMembershipRep.objects.create(
                                                            corporate_membership=corp_memb,
                                                            user=tmp_user,
                                                            is_dues_rep=True
                                                                      )
                            
                    else:
                        # custom field - field_key should have the pattern field_id
                        field_id = field_key.replace('field_', '')
                        try:
                            field_id = int(field_id)
                        except:
                            continue # skip if field doesn't exist
                        
                        try:
                            corp_field = CorpField.objects.get(pk=field_id)
                        except CorpField.DoesNotExist:
                            continue    # skip if field doesn't exist
                        
                        
                        # if this custom field entry exists
                        #     if update_option == 'update', skip
                        #     if update_option == 'override',
                        #            1) override the value
                        add_custom_field = False
                        if is_insert:
                            add_custom_field = True
                        else: # not is_insert:
                            try:
                                cfe = CorpFieldEntry.objects.get(
                                        corporate_membership=corp_memb,
                                        field=corp_field          
                                                                 )
                                if update_option == 'update' and cfe.value:
                                    continue
                                else:
                                    cfe.value =corp_memb.cm[field_key]
                                    cfe.save() 
                                    
                            except CorpFieldEntry.DoesNotExist:
                                add_custom_field = True
                                
                        if add_custom_field:
                            CorpFieldEntry.objects.create(
                                        corporate_membership=corp_memb,
                                        field=corp_field,
                                        value=corp_memb.cm[field_key]               
                                                         )
                            
        if invalid_skipped:
            request.session['corp_memb.import.invalid_skipped'] = invalid_skipped
            
        
        # we're done. clear the session variables related to this import
        del request.session['corp_memb.import.corp_app']
        del request.session['corp_memb.import.corp_membs']
        del request.session['corp_memb.import.fields']
        del request.session['corp_memb.import.update_option']
        
        total_added = len(added)
        total_updated = len(updated) + len(updated_override)
        totals = total_added + total_updated
        
        # log an event here
        log_defaults = {
            'event_id' : 689005,
            'event_data': 'corporate membership imported by %s - INSERTS: %d, UPDATES: %d, TOTAL: %d ' \
                                % (request.user, total_added, total_updated, totals),
            'description': 'corporate membership import',
            'user': request.user,
            'request': request,
            'source': 'corporate_memberships',
        }
        
        EventLog.objects.log(**log_defaults)

        return render_to_response(template_name, {
            'corp_membs': corp_membs,
            'update_option': update_option,
            'invalid_skipped': invalid_skipped,
            'added': added,
            'skipped': skipped,
            'updated': updated,
            'updated_override': updated_override,
            'datetime': datetime,
        }, context_instance=RequestContext(request))
        
@staff_member_required
def download_csv_import_template(request, file_ext='.csv'):
    from django.db.models.fields import AutoField
    #if not is_admin(request.user):raise Http403   # admin only page
    
    filename = "corporate_memberships_import.csv"
    
    corp_memb_field_names = [smart_str(field.name) for field in CorporateMembership._meta.fields 
                             if field.editable and (not field.__class__==AutoField)]
   
    fields_to_exclude = ['guid',
                         'allow_anonymous_view',
                         'allow_user_view',
                         'allow_member_view',
                         'allow_anonymous_edit',
                         'allow_user_edit',
                         'allow_member_edit',
                         'creator_username',
                         'owner',
                         'owner_username',
                         'renew_entry_id',
                         'approved_denied_dt',
                         'approved_denied_user',
                         'payment_method',
                         'invoice',
                         'corp_app',
                         'status',
                         'status_detail'
                         ]
    for field in fields_to_exclude:
        if field in corp_memb_field_names:
            corp_memb_field_names.remove(field)
            
    corp_memb_field_names.extend(['authorized_domains', 'dues_rep'])
    
            
    data_row_list = []
    
    return render_excel(filename, corp_memb_field_names, data_row_list, file_ext)

@staff_member_required
def corp_import_invalid_records_download(request):
    
    #if not is_admin(request.user):raise Http403   # admin only page
    
    file_path = request.session.get('corp_memb.import.file_path')
    invalid_corp_membs = request.session.get('corp_memb.import.invalid_skipped')
    #print invalid_corp_membs
    
    if not file_path or not invalid_corp_membs:
        raise Http403
    
    data = csv.reader(open(file_path))
    title_fields = data.next()
    title_fields = [smart_str(field) for field in title_fields]
    
    item_list = []
    for corp_memb in invalid_corp_membs:
        item = []
        for field in title_fields:
            value = corp_memb.cm.get(field)
            if not value: value = ' '
            item.append(value)
            
        if item:
            item.append('\n')
            item.insert(0, corp_memb.err_msg)
            item_list.append(item)
            
    title_fields.append('\n')
    title_fields.insert(0, 'Invalid Reason?')
    
    filebase, filename = os.path.split(file_path)
    filename = "Invalid_records_%s" % filename
    
    # clear the session now
    #del request.session['corp_memb.import.file_path']
    #del request.session['corp_memb.import.invalid_skipped']
    
    return render_excel(filename, title_fields, item_list, '.csv')

@login_required
def corp_export(request):
    if not is_admin(request.user):raise Http403   # admin only page
    
    template_name = 'corporate_memberships/export.html'
    form = ExportForm(request.POST or None, user=request.user)
    
    if request.method == 'POST':
        if form.is_valid():
            corp_app = form.cleaned_data['corp_app']
            
            filename = "corporate_memberships_%d_export.csv" % corp_app.id
            
            corp_fields = CorpField.objects.filter(corp_app=corp_app).exclude(field_type__in=('section_break', 
                                                               'page_break')).order_by('order')
            label_list = [corp_field.label for corp_field in corp_fields]
            extra_field_labels = ['Dues reps', 'Join Date', 'Expiration Date', 'Status', 'Status Detail']
            extra_field_names = ['dues_reps', 'join_dt', 'expiration_dt', 'status', 'status_detail']
            
            label_list.extend(extra_field_labels)
            label_list.append('\n')
            
            data_row_list = []
            corp_membs = CorporateMembership.objects.all()
            for corp_memb in corp_membs:
                data_row = []
                field_entries = CorpFieldEntry.objects.filter(corporate_membership=corp_memb).values('field', 'value')
                field_entries_d = {}
                for entry in field_entries:
                    field_entries_d[entry['field']] = entry['value']
                for corp_field in corp_fields:
                    value = ''
                    if corp_field.field_name and corp_field.object_type == 'corporate_membership':
                        if corp_field.field_name in ['corporate_membership_type',
                                                     'authorized_domains',
                                                     'payment_method']:
                            if corp_field.field_name == "corporate_membership_type":
                                value = corp_memb.corporate_membership_type.name
                            elif corp_field.field_name == "authorized_domains":
                                auth_domains = AuthorizedDomain.objects.filter(corporate_membership=corp_memb)
                                value = '; '.join([auth_domain.name for auth_domain in auth_domains])
                            elif corp_field.field_name == 'payment_method':
                                if corp_memb.payment_method:
                                    value = corp_memb.payment_method.human_name
                                
                        else:
                            value = getattr(corp_memb, corp_field.field_name)
                        
                    else:
                        if field_entries_d.has_key(corp_field.id):
                            value = field_entries_d[corp_field.id]
                        
                    if value == None:
                        value = ''
                    value_type = type(value)
                    if (value_type is bool) or (value_type is long) or (value_type is int):
                        value = str(value)
                    data_row.append(value.replace(',', ' '))
                
                for field in extra_field_names:
                    value = ''
                    if field == 'dues_reps':
                        dues_reps = CorporateMembershipRep.objects.filter(corporate_membership=corp_memb,
                                                                        is_dues_rep=True)
                        if dues_reps:
                            value = '; '.join(['%s (%s)' % (dues_rep.user.get_full_name(), dues_rep.user.username) for dues_rep in dues_reps])
                    else:
                        value = getattr(corp_memb, field)
                        if field == 'expiration_dt' and (not corp_memb.expiration_dt):
                            value = 'never expire'
                    value_type = type(value)
                    if (value_type is bool) or (value_type is long) or (value_type is int):
                        value = str(value)
                    data_row.append(value)
                    
                data_row.append('\n')
                data_row_list.append(data_row)
                
            return render_excel(filename, label_list, data_row_list, '.csv')
                    
    return render_to_response(template_name, {
            'form':form
            }, context_instance=RequestContext(request))

@staff_member_required             
def new_over_time_report(request, template_name='reports/corp_mems_over_time.html'):
    """
    Shows a report of corp memberships over time.
    1 report for 1 month, 2 months, 3 months, 6 months, and 1 year
    """
    
    stats = get_over_time_stats()
    
    return render_to_response(template_name, {
        'stats':stats,
        }, context_instance=RequestContext(request))

@staff_member_required 
def corp_mems_summary(request, template_name='reports/corp_mems_summary.html'):
    """
    Shows a report of corporate memberships per corporate membership type.
    """
    
    summary,total = get_summary()
    
    return render_to_response(template_name, {
        'summary':summary,
        'total':total,
        }, context_instance=RequestContext(request))
