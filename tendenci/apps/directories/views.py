from datetime import datetime, timedelta
import subprocess
import time
import string
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.contrib import messages
from django.template.defaultfilters import slugify
import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from tendenci.libs.utils import python_executable
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.decorators import password_required
from tendenci.apps.base.http import Http403
from tendenci.apps.base.views import file_display
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import (get_notice_recipients,
    has_perm, has_view_perm, get_query_filters, update_perms_and_save)
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp

from tendenci.apps.directories.models import Directory, DirectoryPricing
from tendenci.apps.directories.models import Category as DirectoryCategory
from tendenci.apps.directories.forms import (DirectoryForm, DirectoryPricingForm,
                                               DirectoryRenewForm, DirectoryExportForm)
from tendenci.apps.directories.utils import directory_set_inv_payment, is_free_listing
from tendenci.apps.notifications import models as notification
from tendenci.apps.base.utils import send_email_notification
from tendenci.apps.directories.forms import DirectorySearchForm


@is_enabled('directories')
def details(request, slug=None, template_name="directories/view.html"):
    if not slug: return HttpResponseRedirect(reverse('directories'))
    directory = get_object_or_404(Directory, slug=slug)

    if has_view_perm(request.user, 'directories.view_directory', directory) \
         or directory.has_membership_with(request.user):
        EventLog.objects.log(instance=directory)

        return render_to_resp(request=request, template_name=template_name,
            context={'directory': directory})

    raise Http403


@is_enabled('directories')
def search(request, template_name="directories/search.html"):
    filters = get_query_filters(request.user, 'directories.view_directory')
    directories = Directory.objects.filter(filters).distinct()
    cat = None

    if not request.user.is_anonymous:
        directories = directories.select_related()

    query = request.GET.get('q', None)

    form = DirectorySearchForm(request.GET, is_superuser=request.user.is_superuser)

    if form.is_valid():
        search_category = form.cleaned_data['search_category']
        query = form.cleaned_data.get('q')
        search_method = form.cleaned_data['search_method']
        cat = form.cleaned_data.get('cat')
        sub_cat = form.cleaned_data.get('sub_cat')
        region = form.cleaned_data.get('region')

        if cat:
            directories = directories.filter(cats__in=[cat])
        if sub_cat:
            directories = directories.filter(sub_cats__in=[sub_cat])

        if region:
            directories = directories.filter(region=region)

        if query and 'tag:' in query:
            tag = query.strip('tag:')
            directories = directories.filter(tags__icontains=tag)
        elif query and search_category:
            search_type = '__iexact'
            if search_method == 'starts_with':
                search_type = '__istartswith'
            elif search_method == 'contains':
                search_type = '__icontains'

            search_filter = {'%s%s' % (search_category, search_type): query}
            directories = directories.filter( **search_filter)

    directories = directories.order_by('headline')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'directories': directories,
        'form' : form,
        'a_to_z': string.ascii_lowercase})


def search_redirect(request):
    return HttpResponseRedirect(reverse('directories'))


@is_enabled('directories')
def print_view(request, slug, template_name="directories/print-view.html"):
    directory = get_object_or_404(Directory, slug=slug)
    if has_view_perm(request.user,'directories.view_directory',directory):
        EventLog.objects.log(instance=directory)

        return render_to_resp(request=request, template_name=template_name,
            context={'directory': directory})
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
        msg_string = 'You need to add a %s Pricing before you can add %s.' % (get_setting('module', 'directories', 'label_plural'),get_setting('module', 'directories', 'label'))
        messages.add_message(request, messages.WARNING, _(msg_string))
        return HttpResponseRedirect(reverse('directory_pricing.add'))

    require_payment = get_setting('module', 'directories', 'directoriesrequirespayment')

    form = form_class(request.POST or None, request.FILES or None, user=request.user)

    if not require_payment:
        del form.fields['payment_method']
        del form.fields['list_type']

    if request.method == "POST":
        if require_payment:
            is_free = is_free_listing(request.user,
                               request.POST.get('pricing', 0),
                               request.POST.get('list_type'))
            if is_free:
                del form.fields['payment_method']

        if form.is_valid():
            directory = form.save(commit=False)
            pricing = form.cleaned_data['pricing']

            if require_payment and is_free:
                directory.payment_method = 'paid - cc'
            if directory.payment_method:
                directory.payment_method = directory.payment_method.lower()
            if not directory.requested_duration:
                directory.requested_duration = 30
            if not directory.list_type:
                directory.list_type = 'regular'

            if not directory.slug:
                directory.set_slug()

            if not can_add_active:
                directory.status = True
                directory.status_detail = 'pending'
            else:
                directory.activation_dt = datetime.now()
                # set the expiration date
                directory.expiration_dt = directory.activation_dt + timedelta(days=directory.requested_duration)

            directory = update_perms_and_save(request, form, directory)
            form.save_m2m()

            # create invoice
            directory_set_inv_payment(request.user, directory, pricing)
            msg_string = 'Successfully added %s' % directory
            messages.add_message(request, messages.SUCCESS, _(msg_string))

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

    return render_to_resp(request=request, template_name=template_name,
        context={'form': form,
                               'require_payment': require_payment})


@csrf_exempt
@login_required
def query_price(request):
    """
    Get the price for user with the selected list type.
    """
    pricing_id = request.POST.get('pricing_id', 0)
    list_type = request.POST.get('list_type', '')
    pricing = get_object_or_404(DirectoryPricing, pk=pricing_id)
    price = pricing.get_price_for_user(request.user, list_type=list_type)
    return HttpResponse(simplejson.dumps({'price': price}))


@is_enabled('directories')
@login_required
def edit(request, id, form_class=DirectoryForm, template_name="directories/edit.html"):
    directory = get_object_or_404(Directory, pk=id)

    if not (has_perm(request.user,'directories.change_directory', directory) \
            or directory.has_membership_with(request.user)):
        raise Http403

    if request.user.is_superuser:
        if not directory.activation_dt:
            # auto-populate activation_dt
            directory.activation_dt = datetime.now()

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
                try:
                    directory.logo.file.seek(0)
                except IOError:
                    directory.logo = None
            # update all permissions and save the model
            directory = update_perms_and_save(request, form, directory)
            form.save_m2m()
            msg_string = 'Successfully updated %s' % directory
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))

    return render_to_resp(request=request, template_name=template_name,
        context={'directory': directory, 'form':form})


@is_enabled('directories')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="directories/edit-meta.html"):
    directory = get_object_or_404(Directory, pk=id)

    if not has_perm(request.user, 'directories.change_directory', directory):
        raise Http403

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
            msg_string = 'Successfully updated meta for %s' % directory
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))
    else:
        form = form_class(instance=directory.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'directory': directory, 'form':form})


@is_enabled('directories')
@login_required
def get_subcategories(request):
    if request.is_ajax() and request.method == "POST":
        categories = request.POST.get('categories', None)
        categories = [int(cat) for cat in categories.split(',') if cat.isdigit()]
        count = 0
        sub_categories = []
        if categories:
            for cat in categories:
                sub_cats = list(DirectoryCategory.objects.filter(parent_id=cat).values_list('id', 'name'))
                if len(sub_cats) > 0:
                    count += len(sub_cats)
                    cat_name = DirectoryCategory.objects.filter(id=cat).values_list('name', flat=True)[0]
                    sub_categories.append({'cat_name': cat_name,  'sub_cats': sub_cats})

            data = json.dumps({"error": False,
                               "sub_categories": sub_categories,
                               "count": count})
        else:
            data = json.dumps({"error": True})

        return HttpResponse(data, content_type="text/plain")
    raise Http404


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
            msg_string = 'Successfully deleted %s' % directory
            messages.add_message(request, messages.SUCCESS, _(msg_string))

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

        return render_to_resp(request=request, template_name=template_name,
            context={'directory': directory})
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

                if "_popup" in request.POST:
                    return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % (escape(directory_pricing.pk), escape(directory_pricing)))

                return HttpResponseRedirect(reverse('directory_pricing.view', args=[directory_pricing.id]))
        else:
            form = form_class(user=request.user)

        if "_popup" in request.GET:
            template_name="directories/pricing-add-popup.html"

        return render_to_resp(request=request, template_name=template_name,
            context={'form':form})
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

    return render_to_resp(request=request, template_name=template_name,
        context={'form':form})


@is_enabled('directories')
@login_required
def pricing_view(request, id, template_name="directories/pricing-view.html"):
    directory_pricing = get_object_or_404(DirectoryPricing, id=id)

    if has_perm(request.user,'directories.view_directorypricing',directory_pricing):
        EventLog.objects.log(instance=directory_pricing)

        return render_to_resp(request=request, template_name=template_name,
            context={'directory_pricing': directory_pricing})
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

    return render_to_resp(request=request, template_name=template_name,
        context={'directory_pricing': directory_pricing})


@is_enabled('directories')
@login_required
def pricing_search(request, template_name="directories/pricing-search.html"):
    if not has_perm(request.user,'directories.view_directorypricing'):
        raise Http403

    directory_pricing = DirectoryPricing.objects.filter(status=True).order_by('duration')
    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'directory_pricings':directory_pricing})


@is_enabled('directories')
@login_required
def pending(request, template_name="directories/pending.html"):
    can_view_directories = has_perm(request.user, 'directories.view_directory')
    can_change_directories = has_perm(request.user, 'directories.change_directory')

    if not all([can_view_directories, can_change_directories]):
        raise Http403

    directories = Directory.objects.filter(status_detail__contains='pending')
    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
            context={'directories': directories})


# @is_enabled('directories')
# @login_required
# def publish(request, id):
#     directory = get_object_or_404(Directory, pk=id)
#     if directory.has_membership_with(request.user):
#         if not directory.activation_dt:
#             directory.activation_dt = datetime.now()
#         directory.status = True
#         directory.status_detail = 'active'
#         directory.allow_anonymous_view = True
#         directory.save()
# 
#         msg_string = 'Successfully published %s' % directory
#         messages.add_message(request, messages.SUCCESS, _(msg_string))
# 
#     return HttpResponseRedirect(reverse('directory', args=[directory.slug]))


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

        msg_string = 'Successfully approved %s' % directory
        messages.add_message(request, messages.SUCCESS, _(msg_string))

        return HttpResponseRedirect(reverse('directory', args=[directory.slug]))

    return render_to_resp(request=request, template_name=template_name,
            context={'directory': directory})

def thank_you(request, template_name="directories/thank-you.html"):
    return render_to_resp(request=request, template_name=template_name)


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
            msg_string = 'Successfully renewed %s' % directory
            messages.add_message(request, messages.SUCCESS, _(msg_string))

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

    return render_to_resp(request=request, template_name=template_name,
        context={'directory':directory, 'form':form})


@is_enabled('directories')
@login_required
@password_required
def directory_export(request, template_name="directories/export.html"):
    """Export Directories"""
    if not request.user.profile.is_superuser:
        raise Http403

    form = DirectoryExportForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        export_fields = form.cleaned_data['export_fields']
        export_status_detail = form.cleaned_data['export_status_detail']
        identifier = int(time.time())
        temp_file_path = 'export/directories/%s_temp.csv' % identifier
        default_storage.save(temp_file_path, ContentFile(''))

        # start the process
        subprocess.Popen([python_executable(), "manage.py",
                          "directory_export_process",
                          '--export_fields=%s' % export_fields,
                          '--export_status_detail=%s' % export_status_detail,
                          '--identifier=%s' % identifier,
                          '--user=%s' % request.user.id])
        # log an event
        EventLog.objects.log()
        return HttpResponseRedirect(reverse('directory.export_status', args=[identifier]))

    context = {'form': form}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('directories')
@login_required
@password_required
def directory_export_status(request, identifier, template_name="directories/export_status.html"):
    """Display export status"""
    if not request.user.profile.is_superuser:
        raise Http403

    export_path = 'export/directories/%s.csv' % identifier
    download_ready = False
    if default_storage.exists(export_path):
        download_ready = True
    else:
        temp_export_path = 'export/directories/%s_temp.csv' % identifier
        if not default_storage.exists(temp_export_path) and \
                not default_storage.exists(export_path):
            raise Http404

    context = {'identifier': identifier,
               'download_ready': download_ready}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('directories')
@login_required
@password_required
def directory_export_download(request, identifier):
    """Download the directories export."""
    if not request.user.profile.is_superuser:
        raise Http403

    file_name = '%s.csv' % identifier
    file_path = 'export/directories/%s' % file_name
    if not default_storage.exists(file_path):
        raise Http404

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="directory_export_%s"' % file_name
    response.content = default_storage.open(file_path).read()
    return response
