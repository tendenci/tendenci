import os
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from perms.utils import is_admin
from base.http import Http403
from imports.forms import UserImportForm
from imports.utils import render_excel, handle_uploaded_file, get_user_import_settings, user_import_process
from event_logs.models import EventLog

IMPORT_DIR = os.path.join(settings.MEDIA_ROOT, 'imports')


@login_required
def user_upload_add(request, form_class=UserImportForm, template_name="imports/users.html"):
    if not is_admin(request.user):raise Http403   # admin only page
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            # save the uploaded file
            file_dir = IMPORT_DIR
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            f = request.FILES['file']
            file_name = f.name.replace('&', '')
            handle_uploaded_file(f, os.path.join(file_dir, file_name))
            
            interactive = form.cleaned_data['interactive']
            override = form.cleaned_data['override']
            key = form.cleaned_data['key']
            group = form.cleaned_data['group']
            clear_group_membership = form.cleaned_data['clear_group_membership']
            
            # store in the session to pass to the next page
            request.session['file_name'] = file_name
            request.session['interactive'] = interactive
            request.session['override'] = override
            request.session['key'] = key
            request.session['group'] = group
            request.session['clear_group_membership'] = clear_group_membership
            
            return HttpResponseRedirect(reverse('imports.views.user_upload_preview'))
    else:
        form = form_class()
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def user_upload_preview(request, template_name="imports/users_preview.html"):
    if not is_admin(request.user):raise Http403   # admin only page

    import_dict = get_user_import_settings(request)
    import_dict['file_dir'] = IMPORT_DIR
    
    if not os.path.isfile(os.path.join(import_dict['file_dir'], import_dict['file_name'])):
        return HttpResponseRedirect(reverse('imports.views.user_upload_add'))

    users_list = user_import_process(request, import_dict, preview=True)
    import_dict['users_list'] = users_list
    
    return render_to_response(template_name, import_dict, 
        context_instance=RequestContext(request))
    
    
@login_required
def user_upload_process(request, template_name="imports/users_process.html"):
    if not is_admin(request.user):raise Http403   # admin only page

    import_dict = get_user_import_settings(request)
    import_dict['file_dir'] = IMPORT_DIR
    
    if not os.path.isfile(os.path.join(import_dict['file_dir'], import_dict['file_name'])):
        return HttpResponseRedirect(reverse('imports.views.user_upload_add'))

    users_list = user_import_process(request, import_dict, preview=False)
    import_dict['users_list'] = users_list
    # recalculate the total
    import_dict['total'] = import_dict['count_insert'] + import_dict['count_update']
    
    # log an event
    log_defaults = {
        'event_id' : 129005,
        'event_data': 'User import: %s<br>INSERTS:%d<br>UPDATES:%d<br>TOTAL:%d' % (import_dict['file_name'], 
                                                                                   import_dict['count_insert'],
                                                                                   import_dict['count_update'], 
                                                                                   import_dict['total']),
        'description': 'user import',
        'user': request.user,
        'request': request,
    }
    EventLog.objects.log(**log_defaults)
    
    
    return render_to_response(template_name, import_dict, 
        context_instance=RequestContext(request))
    
    
@login_required
def download_user_upload_template_xls(request):
    if not is_admin(request.user):raise Http403   # admin only page
    
    filename = "import-users.xls"
    import_field_list = ['salutation', 'first_name', 'last_name', 'initials', 'display_name',
                         'email', 'address', 'address2', 'city', 'state', 'zipcode', 'country', 
                         'company', 'position_title', 'department', 'phone', 'phone2', 'home_phone', 
                         'work_phone', 'mobile_phone', 'fax', 'url', 'notes', 'admin_notes', 
                         'username', 'password']
    data_row_list = []
    
    return render_excel(filename, import_field_list, data_row_list)