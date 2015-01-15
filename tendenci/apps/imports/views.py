import os
import time
import cPickle
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.conf import settings

from tendenci.apps.base.http import Http403
from tendenci.apps.base.decorators import password_required
from tendenci.apps.imports.forms import UserImportForm
from tendenci.apps.imports.utils import (extract_from_excel,
                render_excel, handle_uploaded_file,
                get_user_import_settings,
                user_import_process)
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.user_groups.models import GroupMembership

IMPORT_FOLDER_NAME = 'imports'


@login_required
@password_required
def user_upload_add(request):
    return HttpResponseRedirect(reverse('profiles.user_import'))


@login_required
def user_upload_preview(request, sid,
                        template_name="imports/users_preview.html"):
    if not request.user.profile.is_superuser:
        raise Http403

    sid = str(sid)

    import_dict = get_user_import_settings(request, sid)
    import_dict['folder_name'] = IMPORT_FOLDER_NAME

    if not default_storage.exists(os.path.join(import_dict['folder_name'],
                                               import_dict['file_name'])):
        return HttpResponseRedirect(reverse('import.user_upload_add'))

    users_list = user_import_process(request,
                                            import_dict,
                                            preview=True,
                                            id=sid)[0]
    import_dict['users_list'] = users_list
    import_dict['id'] = sid
    import_dict['total'] = request.session[sid].get('total', 0)

    return render_to_response(template_name, import_dict,
        context_instance=RequestContext(request))


@login_required
def user_upload_process(request, sid,
                template_name="imports/users_process.html"):
    if not request.user.profile.is_superuser:
        raise Http403   # admin only page

    sid = str(sid)
    import_dict = get_user_import_settings(request, sid)
    if not import_dict:
        return HttpResponseRedirect(reverse('import.user_upload_add'))

    import_dict['folder_name'] = IMPORT_FOLDER_NAME
    import_dict['id'] = sid

    if not default_storage.exists(os.path.join(import_dict['folder_name'],
                                               import_dict['file_name'])):
        return HttpResponseRedirect(reverse('import.user_upload_add'))

    #reset group - delete all members in the group
    if import_dict['clear_group_membership'] and import_dict['group']:
        GroupMembership.objects.filter(group=import_dict['group']).delete()

    d = request.session[sid]
    d.update({
        'is_completed': False,
        'count_insert': 0,
        'count_update': 0,
        'total_done': 0
    })

    request.session[sid] = d
    d = None

    return render_to_response(template_name, import_dict,
        context_instance=RequestContext(request))


@login_required
def user_upload_subprocess(request, sid,
                           template_name="imports/users_subprocess.html"):
    if not request.user.profile.is_superuser:
        raise Http403

    sid = str(sid)
    import_dict = get_user_import_settings(request, sid)
    if not import_dict:
        return HttpResponse('')

    import_dict['folder_name'] = IMPORT_FOLDER_NAME

    if not default_storage.exists(os.path.join(import_dict['folder_name'],
                                               import_dict['file_name'])):
        return HttpResponse('')

    users_list, invalid_list = user_import_process(request,
                                                   import_dict,
                                                   preview=False,
                                                   id=sid)
    import_dict['users_list'] = users_list

    # recalculate the total
    import_dict['total_done'] = request.session[sid]['total_done']
    import_dict['total_done'] += import_dict['count_insert'] + \
            import_dict['count_update']
    request.session[sid]['total_done'] = import_dict['total_done']

    d = request.session[sid]
    d.update({'total_done': import_dict['total_done']})
    request.session[sid] = d
    d = None

    import_dict['is_completed'] = request.session[sid]['is_completed']

    # store the recap - so we can retrieve it later
    recap_file_name = '%s_recap.txt' % sid
    recap_path = os.path.join(import_dict['folder_name'], recap_file_name)

    if default_storage.exists(recap_path):
        fd = default_storage.open(recap_path, 'r')
        content = fd.read()
        fd.close()
        recap_dict = cPickle.loads(content)
        recap_dict.update({'users_list': recap_dict['users_list'] + \
                                        import_dict['users_list'],
                           'invalid_list': recap_dict['invalid_list'] + \
                                            invalid_list,
                           'total': import_dict['total'],
                           'total_done': import_dict['total_done'],
                           'count_insert': recap_dict['count_insert'] + \
                                            import_dict['count_insert'],
                           'count_update': recap_dict['count_update'] + \
                                            import_dict['count_update'],
                           'count_invalid': recap_dict['count_invalid'] + \
                                            import_dict['count_invalid']
                           })
        import_dict['count_invalid'] = recap_dict['count_invalid']
    else:
        recap_dict = {'users_list': import_dict['users_list'],
                       'invalid_list': invalid_list,
                       'total': import_dict['total'],
                       'total_done': import_dict['total_done'],
                       'count_insert': import_dict['count_insert'],
                       'count_update': import_dict['count_update'],
                       'count_invalid': import_dict['count_invalid'],
                       'file_name': import_dict['file_name']}

    fd = default_storage.open(recap_path, 'w')
    cPickle.dump(recap_dict, fd)
    fd.close()
    # clear the recap_dict
    recap_dict = None

    if import_dict['is_completed']:
        # log an event
        EventLog.objects.log()

        # clear up the session
        del request.session[sid]

        # remove the imported file
        default_storage.delete(os.path.join(import_dict['folder_name'],
                                            import_dict['file_name']))

    import_dict['id'] = sid
    return render_to_response(template_name, import_dict,
        context_instance=RequestContext(request))


@login_required
def user_upload_recap(request, sid):
    if not request.user.profile.is_superuser:
        raise Http403

    recap_file_name = '%s_recap.txt' % str(sid)
    recap_path = os.path.join(IMPORT_FOLDER_NAME, recap_file_name)

    if default_storage.exists(recap_path):
        import StringIO
        from django.template.defaultfilters import slugify
        from xlwt import Workbook

        # restore the recap_dict
        fd = default_storage.open(recap_path, 'r')
        content = fd.read()
        fd.close()

        recap_dict = cPickle.loads(content)

        output = StringIO.StringIO()
        export_wb = Workbook()
        sheet1 = export_wb.add_sheet('Recap')
        # title
        sheet1.write(0, 0, 'action')
        sheet1.write(0, 1, 'original row#')
        sheet1.write(0, 2, 'username')
        sheet1.write(0, 3, 'frist_name')
        sheet1.write(0, 4, 'last_name')
        sheet1.write(0, 5, 'email')

        # data
        row_idx = 1
        for item_dict in recap_dict['users_list']:
            sheet1.write(row_idx, 0, '%s' % item_dict['ACTION'])
            sheet1.write(row_idx, 1, str(item_dict['ROW_NUM']))
            sheet1.write(row_idx, 2, item_dict['user'].username)
            sheet1.write(row_idx, 3, item_dict['user'].first_name)
            sheet1.write(row_idx, 4, item_dict['user'].last_name)
            sheet1.write(row_idx, 5, item_dict['user'].email)

            row_idx += 1

        # create another sheet for invalid list
        if recap_dict['invalid_list']:
            sheet2 = export_wb.add_sheet('Invalid records')
            # title
            sheet2.write(0, 0, 'invalid?')
            sheet2.write(0, 1, 'original row#')
            sheet2.write(0, 2, 'reason')

        row_idx = 1
        for invalid_dict in recap_dict['invalid_list']:
            sheet2.write(row_idx, 0, 'invalid')
            sheet2.write(row_idx, 1, invalid_dict['ROW_NUM'])
            sheet2.write(row_idx, 2, invalid_dict['ERROR'])
            row_idx += 1

        export_wb.save(output)
        output.seek(0)
        str_out = output.getvalue()
        response = HttpResponse(str_out)
        response['Content-Type'] = 'application/vnd.ms-excel'
        if recap_dict['file_name'] and len(recap_dict['file_name']) > 5:
            recap_name = '%s_recap.xls' % \
                    slugify((recap_dict['file_name'])[:-4])
        else:
            recap_name = "user_import_recap.xls"
        response['Content-Disposition'] = 'attachment; filename=%s' % \
                                         (recap_name)

        recap_dict = None
        return response
    else:
        raise Http404


@login_required
def download_user_upload_template(request, file_ext='.xls'):
    if not request.user.profile.is_superuser:
        raise Http403

    if file_ext == '.csv':
        filename = "import-users.csv"
    else:
        filename = "import-users.xls"
    import_field_list = ['salutation', 'first_name', 'last_name',
                         'initials', 'display_name', 'email',
                          'email2', 'address', 'address2',
                          'city', 'state', 'zipcode', 'country',
                         'company', 'position_title', 'department',
                         'phone', 'phone2', 'home_phone',
                         'work_phone', 'mobile_phone',
                         'fax', 'url', 'dob', 'spouse',
                         'direct_mail', 'notes', 'admin_notes',
                         'username', 'member_number', ]

    data_row_list = []

    return render_excel(filename, import_field_list, data_row_list, file_ext)
