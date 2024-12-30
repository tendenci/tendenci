from datetime import datetime
import time
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from tendenci.apps.memberships.models import Notice, NoticeLog
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.base.http import Http403

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.memberships.notices.forms import NoticeLogSearchForm


@login_required
def membership_notice_log_search(request, template_name="memberships/notices/logs_search.html"):
    if not has_perm(request.user,'memberships.change_notice'): raise Http403

    form = NoticeLogSearchForm(request.GET or None)
    logs = NoticeLog.objects.all()
    if form.is_valid():
        try:
            notice_id = int(form.cleaned_data['notice_id'])
        except ValueError:
            notice_id = None
        if notice_id:
            notice = Notice.objects.get(id=notice_id)
            logs = logs.filter(notice=notice)
        start_dt = form.cleaned_data['start_dt']
        end_dt = form.cleaned_data['end_dt']
        if start_dt:
            #start_dt = datetime(*(time.strptime(start_dt, '%Y-%m-%d %H:%M')[0:6]))
            logs = logs.filter(notice_sent_dt__gte=start_dt)
        if end_dt:
            #end_dt = datetime(*(time.strptime(end_dt, '%Y-%m-%d %H:%M')[0:6]))
            logs = logs.filter(notice_sent_dt__lte=end_dt)
        logs = logs.order_by('-notice_sent_dt')
    else:
        logs = logs.none()

    return render_to_resp(request=request, template_name=template_name,
        context={'logs': logs, 'form':form})


@login_required
def membership_notice_log_view(request, id,
                               template_name="memberships/notices/log_view.html"):
    if not has_perm(request.user, 'memberships.change_notice'):
        raise Http403

    log = get_object_or_404(NoticeLog, id=id)

    log_records = log.default_log_records.all()

    return render_to_resp(request=request, template_name=template_name,
        context={'log': log,
                                              'log_records': log_records})
