from datetime import datetime, timedelta
from PIL import Image

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.conf import settings

from tendenci.core.site_settings.utils import get_setting
from tendenci.core.base.http import Http403
from tendenci.core.base.views import file_display
from tendenci.core.perms.decorators import is_enabled
from tendenci.core.perms.utils import (get_notice_recipients,
    has_perm, has_view_perm, get_query_filters, update_perms_and_save)
from tendenci.core.event_logs.models import EventLog
from tendenci.core.meta.models import Meta as MetaTags
from tendenci.core.meta.forms import MetaForm
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.exports.utils import run_export_task

from tendenci.addons.directories.models import Directory, DirectoryPricing
from tendenci.addons.directories.forms import DirectoryForm, DirectoryPricingForm, DirectoryRenewForm
from tendenci.addons.directories.utils import directory_set_inv_payment
from tendenci.apps.notifications import models as notification
from tendenci.core.base.utils import send_email_notification
from tendenci.addons.directories.utils import resize_s3_image


@is_enabled('directories')
def details(request, slug=None, template_name="directories/view.html"):
    if not slug: return HttpResponseRedirect(reverse('directories'))
    directory = get_object_or_404(Directory, slug=slug)

    if has_view_perm(request.user,'directories.view_directory',directory):
        EventLog.objects.log(instance=directory)

        return render_to_response(template_name, {'directory': directory}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('directories')
def search(request, template_name="directories/search.html"):
    get = dict(request.GET)
    query = get.pop('q', [])
    get.pop('page', None)  # pop page query string out; page ruins pagination
    query_extra = ['%s:%s' % (k,v[0]) for k,v in get.items() if v[0].strip()]
    query = ' '.join(query)
    if query_extra:
        query = '%s %s' % (''.join(query), ' '.join(query_extra))

    if get_setting('site', 'global', 'searchindex') and query:
        directories = Directory.objects.search(query, user=request.user).order_by('headline_exact')
    else:
        filters = get_query_filters(request.user, 'directories.view_directory')
        directories = Directory.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            directories = directories.select_related()
    
        directories = directories.order_by('headline')


    EventLog.objects.log()
    category = request.GET.get('category')
    try:
        category = int(category)
    except:
        category = 0
    categories, sub_categories = Directory.objects.get_categories(category=category)

    return render_to_response(template_name, {
        'directories':directories,
        'categories':categories,
        'sub_categories':sub_categories,
        }, 
        context_instance=RequestContext(request))


def search_redirect(request):
    return HttpResponseRedirect(reverse('directories'))


@is_enabled('directories')
def print_view(request, slug, template_name="directories/print-view.html"):
    directory = get_object_or_404(Directory, slug=slug)    
    if has_view_perm(request.user,'directories.view_directory',directory):
        EventLog.objects.log(instance=directory)

        return render_to_response(template_name, {'directory': directory}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('directories')
@login_required
def add(request, form_class=DirectoryForm, template_name="directories/add.html"):
    can_add_active = has_perm(request.user,'directories.add_directory')
    
    if not any([request.user.profile.is_superuser,
               can_add_active,
               get_setting('module', 'directories', 'usercanadd'),
               (request.user.profile.is_member and get_setting('module', 'directories', 'directoriesrequiresmembership'))
               ]):
        raise Http403

    pricings = DirectoryPricing.objects.filter(status=True)
    if not pricings and has_perm(request.user, 'directories.add_directorypricing'):
        messages.add_message(request, messages.WARNING, 'You need to add a %s Pricing before you can add %s.' % (get_setting('module', 'directories', 'label_plural'),get_setting('module', 'directories', 'label')))
        return HttpResponseRedirect(reverse('directory_pricing.add'))     

    require_payment = get_setting('module', 'directories', 'directoriesrequirespayment')
    
    form = form_class(request.POST or None, request.FILES or None, user=request.user)
    
    if not require_payment:
        del form.fields['payment_method']
        del form.fields['list_type']

    if request.method == "POST":   
        if form.is_valid():           
            directory = form.save(commit=False)
            pricing = form.cleaned_data['pricing']
            
            if directory.payment_method: 
                directory.payment_method = directory.payment_method.lower()
            if not directory.requested_duration:
                directory.requested_duration = 30
            if not directory.list_type:
                directory.list_type = 'regular'
            
            if not directory.slug:
                directory.slug = '%s-%s' % (slugify(directory.headline), Directory.objects.count())
            
            if not can_add_active:
                directory.status = True
                directory.status_detail = 'pending'
            else:
                directory.activation_dt = datetime.now()
                # set the expiration date
                directory.expiration_dt = directory.activation_dt + timedelta(days=directory.requested_duration)

            # We set the logo to None temporarily because we need
            # the PK when we save to get the filepath of the file
            logo = directory.logo
            directory.logo = None

            directory = update_perms_and_save(request, form, directory)

            # directory now has a pk, so we can reassign the logo
            # and resave
            directory.logo = logo

            if directory.logo:
                directory.logo.file.seek(0)

                directory.save(log=False)

                if settings.USE_S3_STORAGE:
                    resize_s3_image(directory.logo.name)
                else:
                    try:
                        logo = Image.open(directory.logo.path)
                        logo.thumbnail((200,200),Image.ANTIALIAS)
                        logo.save(directory.logo.path)
                    except:
                        pass                
                        
            # create invoice
            directory_set_inv_payment(request.user, directory, pricing)

            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % directory)
            
            # send notification to administrators
            # get admin notice recipients
            recipients = get_notice_recipients('module', 'directories', 'directoryrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': directory,
                        'request': request,
                    }
                    notification.send_emails(recipients,'directory_added', extra_context)
                    
            if directory.payment_method.lower() in ['credit card', 'cc']:
                if directory.invoice and directory.invoice.balance > 0:
                    return HttpResponseRedirect(reverse('payment.pay_online', args=[directory.invoice.id, directory.invoice.guid])) 
            if can_add_active:  
                return HttpResponseRedirect(reverse('directory', args=[directory.slug])) 
            else:
                return HttpResponseRedirect(reverse('directory.thank_you'))             

    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))


@is_enabled('directories')
@login_required
def edit(request, id, form_class=DirectoryForm, template_name="directories/edit.html"):
    directory = get_object_or_404(Directory, pk=id)

    if not has_perm(request.user,'directories.change_directory', directory):
        raise Http403
    
    form = form_class(request.POST or None, request.FILES or None, 
                      instance=directory, 
                      user=request.user)
    
    del form.fields['payment_method']
    if not request.user.profile.is_superuser:
        del form.fields['pricing']
        del form.fields['list_type']
    
    if request.method == "POST":
        if form.is_valid():
            directory = form.save(commit=False)
            
            if directory.logo:
                directory.logo.file.seek(0)
            # update all permissions and save the model
            directory = update_perms_and_save(request, form, directory)

            # resize the image that has been uploaded
            if directory.logo:
                if settings.USE_S3_STORAGE:
                    resize_s3_image(directory.logo.name)
                else:
                    try:
                        logo = Image.open(directory.logo.path)
                        logo.thumbnail((200,200),Image.ANTIALIAS)
                        logo.save(directory.logo.path)
                    except:
                        pass

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % directory)
                                                                         
            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))             
        else:
            form = form_class(instance=directory, user=request.user)

        return render_to_response(template_name, {'directory': directory, 'form':form}, 
            context_instance=RequestContext(request))


    return render_to_response(template_name, {'directory': directory, 'form':form}, 
        context_instance=RequestContext(request))


@is_enabled('directories')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="directories/edit-meta.html"):
    defaults = {
        'title': directory.get_title(),
        'description': directory.get_description(),
        'keywords': directory.get_keywords(),
        'canonical_url': directory.get_canonical_url(),
    }
    directory.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=directory.meta)
        if form.is_valid():
            directory.meta = form.save() # save meta
            directory.save() # save relationship
            
            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % directory)
             
            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))
    else:
        form = form_class(instance=directory.meta)

    return render_to_response(template_name, {'directory': directory, 'form':form}, 
        context_instance=RequestContext(request))


@is_enabled('directories')
def logo_display(request, id):
    directory = get_object_or_404(Directory, pk=id)

    if not has_view_perm(request.user,
                        'directories.view_directory',
                        directory):
        raise Http403

    return file_display(request, directory.logo.name)


@is_enabled('directories')
@login_required
def delete(request, id, template_name="directories/delete.html"):
    directory = get_object_or_404(Directory, pk=id)

    if has_perm(request.user,'directories.delete_directory'):   
        if request.method == "POST":

            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % directory)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'directories', 'directoryrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': directory,
                        'request': request,
                    }
                    notification.send_emails(recipients,'directory_deleted', extra_context)

            directory.delete()

            return HttpResponseRedirect(reverse('directory.search'))

        return render_to_response(template_name, {'directory': directory}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('directories')
@login_required
def pricing_add(request, form_class=DirectoryPricingForm, template_name="directories/pricing-add.html"):
    if has_perm(request.user,'directories.add_directorypricing'):
        if request.method == "POST":
            form = form_class(request.POST, user=request.user)
            if form.is_valid():           
                directory_pricing = form.save(commit=False)
                directory_pricing.status = 1
                directory_pricing.save(request.user)
                
                return HttpResponseRedirect(reverse('directory_pricing.view', args=[directory_pricing.id]))
        else:
            form = form_class(user=request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('directories')
@login_required
def pricing_edit(request, id, form_class=DirectoryPricingForm, template_name="directories/pricing-edit.html"):
    directory_pricing = get_object_or_404(DirectoryPricing, pk=id)
    if not has_perm(request.user,'directories.change_directorypricing',directory_pricing): Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=directory_pricing, user=request.user)
        if form.is_valid():           
            directory_pricing = form.save(commit=False)
            directory_pricing.save(request.user)
            
            return HttpResponseRedirect(reverse('directory_pricing.view', args=[directory_pricing.id]))
    else:
        form = form_class(instance=directory_pricing, user=request.user)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))


@is_enabled('directories')
@login_required
def pricing_view(request, id, template_name="directories/pricing-view.html"):
    directory_pricing = get_object_or_404(DirectoryPricing, id=id)
    
    if has_perm(request.user,'directories.view_directorypricing',directory_pricing):        
        EventLog.objects.log(instance=directory_pricing)

        return render_to_response(template_name, {'directory_pricing': directory_pricing}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('directories')
@login_required
def pricing_delete(request, id, template_name="directories/pricing-delete.html"):
    directory_pricing = get_object_or_404(DirectoryPricing, pk=id)

    if not has_perm(request.user,'directories.delete_directorypricing'): raise Http403
       
    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % directory_pricing)
        
        #directory_pricing.delete()
        # soft delete
        directory_pricing.status = False
        directory_pricing.save()
            
        return HttpResponseRedirect(reverse('directory_pricing.search'))
    
    return render_to_response(template_name, {'directory_pricing': directory_pricing}, 
        context_instance=RequestContext(request))


@is_enabled('directories')
def pricing_search(request, template_name="directories/pricing-search.html"):
    directory_pricing = DirectoryPricing.objects.filter(status=True).order_by('duration')
    EventLog.objects.log()

    return render_to_response(template_name, {'directory_pricings':directory_pricing}, 
        context_instance=RequestContext(request))


@is_enabled('directories')
@login_required
def pending(request, template_name="directories/pending.html"):
    can_view_directories = has_perm(request.user, 'directories.view_directory')
    can_change_directories = has_perm(request.user, 'directories.change_directory')
    
    if not all([can_view_directories, can_change_directories]):
        raise Http403

    directories = Directory.objects.filter(status_detail__contains='pending')
    EventLog.objects.log()

    return render_to_response(template_name, {'directories': directories},
            context_instance=RequestContext(request))


@is_enabled('directories')
@login_required
def approve(request, id, template_name="directories/approve.html"):
    can_view_directories = has_perm(request.user, 'directories.view_directory')
    can_change_directories = has_perm(request.user, 'directories.change_directory')
    
    if not all([can_view_directories, can_change_directories]):
        raise Http403
    
    directory = get_object_or_404(Directory, pk=id)

    if request.method == "POST":
        directory.activation_dt = datetime.now()
        directory.expiration_dt = directory.activation_dt + timedelta(days=directory.requested_duration)
        directory.allow_anonymous_view = True
        directory.status = True
        directory.status_detail = 'active'

        if not directory.creator:
            directory.creator = request.user
            directory.creator_username = request.user.username

        if not directory.owner:
            directory.owner = request.user
            directory.owner_username = request.user.username

        directory.save()
        
        # send email notification to user
        recipients = [directory.creator.email]
        if recipients:
            extra_context = {
                'object': directory,
                'request': request,
            }
            try:
                send_email_notification('directory_approved_user_notice', recipients, extra_context)
            except:
                pass


        messages.add_message(request, messages.SUCCESS, 'Successfully approved %s' % directory)

        return HttpResponseRedirect(reverse('directory', args=[directory.slug]))

    return render_to_response(template_name, {'directory': directory},
            context_instance=RequestContext(request))

def thank_you(request, template_name="directories/thank-you.html"):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))


@is_enabled('directories')
@login_required
def export(request, template_name="directories/export.html"):
    """Export Directories"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        file_name = "directories.csv"
        fields = [
            'guid',
            'slug',
            'timezone',
            'headline',
            'summary',
            'body',
            'source',
            'logo',
            'first_name',
            'last_name',
            'address',
            'address2',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'phone2',
            'fax',
            'email',
            'email2',
            'website',
            'list_type',
            'requested_duration',
            'pricing',
            'activation_dt',
            'expiration_dt',
            'invoice',
            'payment_method',
            'syndicate',
            'design_notes',
            'admin_notes',
            'tags',
            'enclosure_url',
            'enclosure_type',
            'enclosure_length',
            'entity',
        ]
        export_id = run_export_task('directories', 'directory', fields)
        EventLog.objects.log()
        return redirect('export.status', export_id)
        
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))


@is_enabled('directories')
def renew(request, id, form_class=DirectoryRenewForm, template_name="directories/renew.html"):
    can_add_active = has_perm(request.user,'directories.add_directory')
    require_approval = get_setting('module', 'directories', 'renewalrequiresapproval')
    directory = get_object_or_404(Directory, pk=id)
    
    if not has_perm(request.user,'directories.change_directory', directory) or not request.user == directory.creator:
        raise Http403
    
    # pop payment fields if not required
    require_payment = get_setting('module', 'directories', 'directoriesrequirespayment')
    form = form_class(request.POST or None, request.FILES or None, instance=directory, user=request.user)
    if not require_payment:
        del form.fields['payment_method']
        del form.fields['list_type']
    
    if request.method == "POST":
        if form.is_valid():           
            directory = form.save(commit=False)
            pricing = form.cleaned_data['pricing']
            
            if directory.payment_method: 
                directory.payment_method = directory.payment_method.lower()
            if not directory.requested_duration:
                directory.requested_duration = 30
            if not directory.list_type:
                directory.list_type = 'regular'
            
            if not directory.slug:
                directory.slug = '%s-%s' % (slugify(directory.headline), Directory.objects.count())
            
            if not can_add_active and require_approval:
                directory.status = True
                directory.status_detail = 'pending'
            else:
                directory.activation_dt = datetime.now()
                # set the expiration date
                directory.expiration_dt = directory.activation_dt + timedelta(days=directory.requested_duration)
                # mark renewal as not sent for new exp date
                directory.renewal_notice_sent = False
            # update all permissions and save the model
            directory = update_perms_and_save(request, form, directory)             
                        
            # create invoice
            directory_set_inv_payment(request.user, directory, pricing)

            messages.add_message(request, messages.SUCCESS, 'Successfully renewed %s' % directory)
            
            # send notification to administrators
            # get admin notice recipients
            recipients = get_notice_recipients('module', 'directories', 'directoryrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': directory,
                        'request': request,
                    }
                    notification.send_emails(recipients,'directory_renewed', extra_context)
                    
            if directory.payment_method.lower() in ['credit card', 'cc']:
                if directory.invoice and directory.invoice.balance > 0:
                    return HttpResponseRedirect(reverse('payments.views.pay_online', args=[directory.invoice.id, directory.invoice.guid])) 
            if can_add_active:  
                return HttpResponseRedirect(reverse('directory', args=[directory.slug])) 
            else:
                return HttpResponseRedirect(reverse('directory.thank_you'))  
        
    
    return render_to_response(template_name, {'directory':directory, 'form':form}, 
        context_instance=RequestContext(request))
