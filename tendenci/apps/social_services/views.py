from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.social_services.forms import SkillSetForm, ReliefAssessmentForm, AddressForm
from tendenci.apps.social_services.models import SkillSet, ReliefAssessment
from tendenci.apps.social_services.utils import get_responder_skills_data
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.base.http import Http403
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.event_logs.models import EventLog


@login_required
def skill_list(request, username, edit=False, template_name="social_services/skills.html"):

    user_this = get_object_or_404(User, username=username)
    
    edit_mode = edit
    # check permissions
    allowed_perms = (request.user == user_this,
                     has_perm(request.user, 'social_services.change_skillset'),
                     not edit_mode and has_perm(request.user, 'social_services.view_skillset'))
    if not any(allowed_perms):
        raise Http403

    if not hasattr(user_this, 'skillset'):
        skills = SkillSet.objects.create(user=user_this)
    else:
        skills = user_this.skillset

    address_form = AddressForm(request.POST or None,
                               instance=user_this.profile)
    skills_form = SkillSetForm(request.POST or None,
                               edit=edit_mode,
                               instance=skills)
    forms = [address_form, skills_form]

    if request.method == 'POST':
        if all([form.is_valid() for form in forms]):
            address_form.save()
            skills_form.save()
            return redirect('user.skills', user_this.username)

    context = {'forms': forms,
               'skills_form': skills_form,
               'edit_mode': edit_mode,
               'user_this': user_this}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('social_services')
@login_required
def relief_form(request, template_name="social_services/relief_form.html"):
    form = ReliefAssessmentForm(request.POST or None)
    now = timezone.now()

    if request.method == 'POST' and form.is_valid():
        relief_assessment = form.save()
        EventLog.objects.log()
        return redirect('social-services.map')

    context = {'form': form, 'now': now}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('social_services')
@login_required
def relief_map(request, template_name="social_services/map.html"):
    if not has_perm(request.user, 'social_services.view_reliefassessment'):
        raise Http403

    responders = SkillSet.objects.filter(loc__isnull=False)

    center = 0
    if request.user.is_authenticated:
        try:
            skillset = request.user.skillset
            if skillset.is_first_responder:
                center = [skillset.loc.x, skillset.loc.y]
                responders = responders.exclude(user=request.user)
        except:
            pass

    b_points = [[r.loc.x, r.loc.y] for r in responders if r.is_first_responder]

    disaster_areas = ReliefAssessment.objects.filter(loc__isnull=False)
    r_points = [[r.loc.x, r.loc.y] for r in disaster_areas]

    context = {'b_points': b_points, 'r_points': r_points, 'center': center}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('social_services')
@login_required
def responders_list(request, template_name="social_services/responders.html"):
    if not has_perm(request.user, 'social_services.view_skillset'):
        raise Http403
 
    lon = request.GET.get('lon', None)
    lat = request.GET.get('lat', None)
    d = request.GET.get('d', 20)

    skillset = SkillSet.objects.all()

    if lon and lat:
        point = fromstr('POINT({} {})'.format(lon, lat), srid=4326)
        # Filter all responders within 20 miles of location given
        skillset = skillset.filter(loc__distance_lte=(point, D(mi=int(d))))

    [emergency_skills, transportation_skills,
     medical_skills, communication_skills,
     education_skills, military_skills] = get_responder_skills_data(skillset)

    responders = [x for x in skillset if x.is_first_responder]

    context = {'responders': responders,
               'emergency_skills': emergency_skills,
               'transportation_skills': transportation_skills,
               'medical_skills': medical_skills,
               'communication_skills': communication_skills,
               'education_skills': education_skills,
               'military_skills': military_skills,
               'lon': lon, 'lat': lat}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('social_services')
@login_required
def relief_areas_list(request, template_name="social_services/relief-areas.html"):
    if not has_perm(request.user, 'social_services.view_reliefassessment'):
        raise Http403

    lon = request.GET.get('lon', None)
    lat = request.GET.get('lat', None)
    d = request.GET.get('d', 20)

    relief_areas = ReliefAssessment.objects.all()

    if lon and lat:
        point = fromstr('POINT({} {})'.format(lon, lat), srid=4326)
        # Filter all relief areas within 20 miles of location given
        relief_areas = relief_areas.filter(loc__distance_lte=(point, D(mi=int(d))))

    stats = [relief_areas.filter(ssa=True).count(),
             relief_areas.filter(dhs=True).count(),
             relief_areas.filter(children_needs=True).count(),
             relief_areas.filter(toiletries=True).count(),
             relief_areas.filter(employment=True).count(),
             relief_areas.filter(training=True).count(),
             relief_areas.filter(food=True).count(),
             relief_areas.filter(gas=True).count(),
             relief_areas.filter(prescription=True).count()]

    EventLog.objects.log()
    context = {'relief_areas': relief_areas, 'stats': stats, 'lon': lon, 'lat': lat}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('social_services')
@login_required
def relief_area_detail(request, area_id, template_name="social_services/relief-area-detail.html"):
    if not has_perm(request.user, 'social_services.view_reliefassessment'):
        raise Http403

    area = get_object_or_404(ReliefAssessment, pk=area_id)

    form = ReliefAssessmentForm(edit=False, instance=area)

    context = {'form': form}
    EventLog.objects.log()
    return render_to_resp(request=request, template_name=template_name, context=context)
