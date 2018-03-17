from tendenci.apps.theme.shortcuts import themed_response as render_to_resp

from tendenci.apps.versions.models import Version


def version_list(request, ct=None, object_id=None, template_name="versions/version_list.html"):
    versions = Version.objects.filter(object_id=object_id, content_type=ct).order_by('create_dt')

    return render_to_resp(request=request, template_name=template_name,
        context={'versions': versions})
