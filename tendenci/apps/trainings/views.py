from urllib.parse import urlparse
#from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
#from django.db.models import Q

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from .models import (TeachingActivity, OutsideSchool, Transcript,
             CertCat, Certification)        
from .forms import (TeachingActivityForm,
                    OutsideSchoolForm,
                    ParticipantsForm,
                    CoursesInfoForm)
from .utils import generate_transcripts_pdf


class TeachingActivityCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'trainings/teaching_activities/add.html'
    form_class = TeachingActivityForm
    model = TeachingActivity
    #success_url = reverse('trainings.teaching_activities')
    success_message = _('Teaching Activity was added successfully')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.creator = self.request.user
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('trainings.teaching_activities')


class TeachingActivityListView(LoginRequiredMixin, ListView):
    template_name = 'trainings/teaching_activities/list.html'

    def get_queryset(self):
        sort_by = ''
        # sort by field
        sort = self.request.GET.get('s', '')
        # desc or asc
        if self.request.GET.get('o', '') == 'desc':
            order = '-'
        else:
            order = ''
        if sort in ['activity_name', 'date', 'status_detail']:
            sort_by = order + sort
        if sort_by:
            return TeachingActivity.objects.filter(
                user=self.request.user).order_by(sort_by)
        return TeachingActivity.objects.filter(
                user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TeachingActivityListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o', '')
        context['s'] = self.request.GET.get('s', '')
        if context['o'] == 'desc':
            context['next_order'] = 'asc'
        else:
            context['next_order'] = 'desc'
        return context


class OutsideSchoolCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'trainings/outside_schools/add.html'
    form_class = OutsideSchoolForm
    model = OutsideSchool
    #success_url = reverse('trainings.teaching_activities')
    success_message = _('Outside School was added successfully')

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     return super().form_valid(form)

    def get_success_url(self):
        return reverse('trainings.outside_schools')

    def get_form_kwargs(self):
        kwargs = super(OutsideSchoolCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class OutsideSchoolListView(LoginRequiredMixin, ListView):
    template_name = 'trainings/outside_schools/list.html'

    def get_queryset(self):
        queryset = OutsideSchool.objects.filter(user=self.request.user)
        sort_by = ''
        # sort by field
        sort = self.request.GET.get('s', '')
        # desc or asc
        if self.request.GET.get('o', '') == 'desc':
            order = '-'
        else:
            order = ''
        if sort in ['school_name', 'date', 'credits', 'status_detail']:
            sort_by = order + sort
        if sort_by:
            return queryset.order_by(sort_by)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(OutsideSchoolListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o', '')
        context['s'] = self.request.GET.get('s', '')
        if context['o'] == 'desc':
            context['next_order'] = 'asc'
        else:
            context['next_order'] = 'desc'
        return context


@login_required
def transcripts(request, user_id=None, corp_profile_id=None,
                generate_pdf=False,
                template_name="trainings/transcripts.html"):
    """
    Display transcripts
    """
    from tendenci.apps.corporate_memberships.models import CorpProfile
    corp_profile = None
    participants_form = None
    hidden_participants_form = None
    courses_info_form = None
    participants = None
    online_courses = None
    onsite_courses = None
    include_outside_schools = False
    include_teaching_activities = False
    users = None
    step = 'step2'

    if corp_profile_id:
        corp_profile = get_object_or_404(CorpProfile, pk=corp_profile_id)
        if request.user.is_superuser or corp_profile.is_rep(request.user):
            participants_form = ParticipantsForm(request.GET,
                                         request=request,
                                         corp_profile=corp_profile)
            if participants_form.is_valid():
                participants = participants_form.cleaned_data['participants']
        else:
            raise Http403
    else:
        if user_id:
            user_this = get_object_or_404(User, pk=user_id)
        else:
            user_this = request.user

        if not (request.user.is_superuser or user_this == request.user):
            # TODO: check if request.user is a corp rep
            profile_this = user_this.profile
            if not profile_this.allow_edit_by(request.user):
                raise Http403

        participants = [user_this.id]

    if participants:
        courses_info_form = CoursesInfoForm(request.GET,
                                            request=request,
                                            participants=participants)

        if courses_info_form.is_valid():
            online_courses = courses_info_form.cleaned_data['online_courses']
            onsite_courses = courses_info_form.cleaned_data['onsite_courses']
            include_outside_schools = courses_info_form.cleaned_data['include_outside_schools']
            include_teaching_activities = courses_info_form.cleaned_data['include_teaching_activities']

            if 'step2' in request.GET:
                step = 'step3'

                users = User.objects.filter(id__in=participants)

    if participants_form:
        if not courses_info_form:
            step = 'step1'
        if step != 'step1':
            hidden_participants_form = ParticipantsForm(request.GET,
                                         request=request,
                                         corp_profile=corp_profile,
                                         hidden=True)
  
    certs = Certification.objects.all()
    for cert in certs:
        cert.certcats = []
        cats = cert.categories.all()
        for cat in cats:
            [certcat] = CertCat.objects.filter(certification=cert, category=cat)[:1] or [None]
            if certcat:
                cert.certcats.append(certcat)

    params={'certs': certs,
         'users': users,
         'corp_profile': corp_profile,
         'participants_form': participants_form,
         'hidden_participants_form': hidden_participants_form,
         'courses_info_form': courses_info_form,
         'online_courses': online_courses,
         'onsite_courses': onsite_courses,
         'include_outside_schools': include_outside_schools,
         'include_teaching_activities': include_teaching_activities,
         'step': step}

    if generate_pdf:
        params['customer'] = get_object_or_404(User, pk=user_id)
        return generate_transcripts_pdf(request, **params)
    
    params['qs'] = urlparse(request.get_full_path()).query   
    return render_to_resp(request=request,
                          template_name=template_name,
            context=params)
