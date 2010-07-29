import os
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from perms.utils import is_admin
from base.http import Http403
from imports.forms import UserImportForm, UserImportPreviewForm
from imports.utils import render_excel, handle_uploaded_file

@login_required
def user_upload_add(request, form_class=UserImportForm, template_name="imports/users.html"):
    if not is_admin(request.user):raise Http403   # admin only page
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            # save the uploaded file
            file_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
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
            if group:
                group_id = group.id
            else:
                group_id = 0
            
            # pass the query string to the preview
            qs = '?interactive=%s&override=%s&key=%s&group=%s&clear=%d&file_name=%s' % \
                (interactive, override, key, group_id, clear_group_membership, file_name)
            
            return HttpResponseRedirect(reverse('imports.views.user_upload_preview') + qs)
    else:
        form = form_class()
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def user_upload_preview(request, form_class=UserImportPreviewForm, template_name="imports/users_preview.html"):
    if not is_admin(request.user):raise Http403   # admin only page

    if request.method == 'POST':
        pass
    else:
        d = {}
        d['file_name'] = request.GET.get('file_name', '')
        d['interactive'] = request.GET.get('interactive', '0')
        d['override'] = request.GET.get('override', '0')
        d['key'] = request.GET.get('key', '')
        d['group'] = request.GET.get('group', '')
        d['clear_group_membership'] = request.GET.get('clear', '0')
        form = form_class(initial=d)
    return render_to_response(template_name, {'form': form}, 
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