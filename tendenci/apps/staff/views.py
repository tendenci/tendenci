from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import get_query_filters, has_view_perm
from tendenci.apps.staff.models import Staff, Department
from tendenci.apps.staff.forms import StaffSearchForm


@is_enabled('staff')
def detail(request, slug=None, cv=None):
    """Staff plugin details view"""
    staff = get_object_or_404(Staff, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (staff.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

    if cv:
        template_name="staff/cv.html"
    else:
        template_name="staff/view.html"

    if has_view_perm(request.user, 'staff.view_staff', staff):
        EventLog.objects.log(instance=staff)

        return render_to_resp(request=request, template_name=template_name,
            context={'staff': staff})
    else:
        raise Http403


@is_enabled('staff')
def search(request, slug=None, template_name="staff/search.html"):
    """Staff plugin search list view"""
    if slug:
        department = get_object_or_404(Department, slug=slug)
    else:
        department = None
     
    query = ''
    department_id = 0
    position = 0
   
    form = StaffSearchForm(request.GET)
    if department:
        del form.fields['department']

    if form.is_valid():
        query = form.cleaned_data['q']
        department_id = form.cleaned_data.get('department', 0)
        position = form.cleaned_data['position']

    try:
        department_id = int(department_id)
    except:
        pass
    try:
        position = int(position)
    except:
        pass

    filters = get_query_filters(request.user, 'staff.view_staff')
    staff = Staff.objects.filter(filters).distinct()
    if not request.user.is_anonymous:
        staff = staff.select_related()

    if query:
        staff = staff.filter(Q(name__icontains=query) | Q(department__name__icontains=query))

    if department:
        staff = staff.filter(department__id=department.id)
    else:
        if department_id:
            staff = staff.filter(department__id=department_id)
            [department] = Department.objects.filter(id=department_id)[:1] or [None]
            
    if position:
        staff = staff.filter(positions__in=[position])

    staff = staff.order_by('-position', 'name', '-status', 'status_detail')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'staff_members':staff, 'department': department,
                 'form': form})


@is_enabled('staff')
def search_redirect(request):
    return HttpResponseRedirect(reverse('staff'))
