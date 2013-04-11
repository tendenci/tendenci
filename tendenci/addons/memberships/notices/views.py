from datetime import datetime
import time
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from tendenci.addons.memberships.models import Notice, NoticeLog, NoticeLogRecord
from tendenci.core.perms.utils import has_perm
from tendenci.core.base.http import Http403

from tendenci.addons.memberships.notices.forms import NoticeLogSearchForm


@login_required
def membership_notice_log_search(request, template_name="memberships/notices/logs_search.html"):
    if not has_perm(request.user,'memberships.change_notice'): raise Http403
    
    form = NoticeLogSearchForm(request.GET or None)
    logs = NoticeLog.objects.all()
    if form.is_valid():
        notice_id = form.cleaned_data['notice_id']
        if notice_id:
            notice = Notice.objects.get(id=notice_id)
            logs = logs.filter(notice=notice)
        start_dt = form.cleaned_data['start_dt']
        end_dt = form.cleaned_data['end_dt']
        if start_dt:
            start_dt = datetime(*(time.strptime(start_dt, '%Y-%m-%d %H:%M')[0:6]))
            logs = logs.filter(notice_sent_dt__gte=start_dt)
        if end_dt:
            end_dt = datetime(*(time.strptime(end_dt, '%Y-%m-%d %H:%M')[0:6]))
            logs = logs.filter(notice_sent_dt__lte=end_dt)
       
    logs = logs.order_by('-notice_sent_dt')
    
    return render_to_response(template_name, {'logs': logs, 'form':form},
        context_instance=RequestContext(request))


@login_required
def membership_notice_log_view(request, id,
                               template_name="memberships/notices/log_view.html"):
    if not has_perm(request.user, 'memberships.change_notice'):
        raise Http403

    log = get_object_or_404(NoticeLog, id=id)

    log_records = log.default_log_records.all()
    if not log_records:
        log_records = log.log_records.all()

    return render_to_response(template_name, {'log': log,
                                              'log_records': log_records},
        context_instance=RequestContext(request))