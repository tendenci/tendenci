from django.shortcuts import get_object_or_404

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.tendenci_guide.models import Guide


def guide_page(request, slug=None, template_name="tendenci_guide/detail.html"):
    guide = get_object_or_404(Guide, slug=slug)
    section_guides = Guide.objects.filter(section=guide.section).order_by('position')
    remaining = Guide.objects.filter(section=guide.section, position__gt=guide.position).order_by('position')
    if remaining:
        next = remaining[0]
    if request.user.profile.is_superuser:

        EventLog.objects.log(instance=guide)
        return render_to_resp(request=request, template_name=template_name, context=locals())
    else:
        raise Http403
