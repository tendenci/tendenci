from urllib.parse import urlparse
from wsgiref.util import FileWrapper
import subprocess
import json
#from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404
#from django.db.models import Q
from django.contrib import messages
from django.utils.decorators import method_decorator

from tendenci.libs.utils import python_executable
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.decorators import is_enabled
from .models import (TeachingActivity, OutsideSchool,
             CertCat, Certification, CorpTranscriptsZipFile, Course)        
from .forms import (TeachingActivityForm,
                    OutsideSchoolForm,
                    ParticipantsForm,
                    CoursesInfoForm)
from .utils import generate_transcript_pdf


@method_decorator(is_enabled('trainings'), name="dispatch")
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

        # log an event
        EventLog.objects.log(action='teaching_activity_add')
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('trainings.teaching_activities')


@method_decorator(is_enabled('trainings'), name="dispatch")
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


@method_decorator(is_enabled('trainings'), name="dispatch")
class OutsideSchoolCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'trainings/outside_schools/add.html'
    form_class = OutsideSchoolForm
    model = OutsideSchool
    #success_url = reverse('trainings.teaching_activities')
    success_message = _('Outside School was added successfully')

    def form_valid(self, form):
        EventLog.objects.log(action='outside_school_add')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('trainings.outside_schools')

    def get_form_kwargs(self):
        kwargs = super(OutsideSchoolCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


@method_decorator(is_enabled('trainings'), name="dispatch")
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


@is_enabled('trainings')
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
    #MAX_USERS = 100 # if number of users > 100, courses will not show on transcripts

    if corp_profile_id:
        corp_profile = get_object_or_404(CorpProfile, pk=corp_profile_id)
        if request.user.is_superuser or corp_profile.is_rep(request.user):
            participants_form = ParticipantsForm(request.POST,
                                         request=request,
                                         corp_profile=corp_profile)

            if request.method == 'POST':
                if participants_form.is_valid():
                    participants = participants_form.cleaned_data['p']
                    request.session['transcripts_p'] = participants
            else: # GET
                if 'transcripts_p' in request.session:
                    if request.GET.get('page') or generate_pdf:
                        participants = request.session['transcripts_p']
                    else:
                        del request.session['transcripts_p']
                        if 'transcripts_c' in request.session:
                            del request.session['transcripts_c']
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
            if not profile_this.allow_view_transcript(request.user):
                raise Http403

        participants = [user_this.id]

    if participants:
        courses_info_form = CoursesInfoForm(request.POST,
                                            request=request,
                                            participants=participants,)
        if request.method == 'POST':
            if courses_info_form.is_valid():
                online_courses = courses_info_form.cleaned_data['l']
                onsite_courses = courses_info_form.cleaned_data['s']
                include_outside_schools = courses_info_form.cleaned_data['include_outside_schools']
                include_teaching_activities = courses_info_form.cleaned_data['include_teaching_activities']

                # if len(participants) > MAX_USERS:
                #     online_courses = online_courses.none()
                #     onsite_courses = onsite_courses.none()
                #     include_outside_schools = False
                #     include_teaching_activities = False
                courses_info = {'l': list(online_courses.values_list('id', flat=True)),
                                's': list(onsite_courses.values_list('id', flat=True)),
                                'outside': include_outside_schools,
                                'teaching': include_teaching_activities}
                request.session['transcripts_c'] = json.dumps(courses_info)

                if 'step2' in request.POST:
                    step = 'step3'
    
                    users = User.objects.filter(id__in=participants)
        else: # GET
            if 'transcripts_c' in request.session:
                if request.GET.get('page') or generate_pdf:
                    courses_info = json.loads(request.session['transcripts_c'])
                    online_courses = Course.objects.filter(id__in=courses_info.get('l'))
                    onsite_courses = Course.objects.filter(id__in=courses_info.get('s'))
                    include_outside_schools = courses_info.get('outside')
                    include_teaching_activities = courses_info.get('teaching')
                    step = 'step3'
                    users = User.objects.filter(id__in=participants)
                else:
                    del request.session['transcripts_c']

    if participants_form:
        if not courses_info_form:
            step = 'step1'
        if step != 'step1':
            hidden_participants_form = ParticipantsForm(request.POST,
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
        if corp_profile_id:
            ctzf = CorpTranscriptsZipFile(
                corp_profile_id=corp_profile_id,
                params_dict={'certs': ','.join(str(cert.id) for cert in certs),
                             'users': ','.join(str(u.id) for u in users),
                             'corp_profile': corp_profile.id,
                             'online_courses': ','.join(str(c.id) for c in online_courses),
                             'onsite_courses': ','.join(str(c.id) for c in onsite_courses),
                             'include_outside_schools': include_outside_schools,
                             'include_teaching_activities': include_teaching_activities,},
                creator=request.user,)
            ctzf.save()
            # start a subprocess to generate a zip file
            subprocess.Popen([python_executable(), "manage.py",
                              "generate_transcript_pdfs",
                              str(ctzf.pk) ])
            # redirect to the status page
            messages.add_message(request, messages.INFO, _("The system is now generating all transcript PDFs and zip to a file. Please reload in a few seconds to check if it's ready."))
            return redirect('trainings.corp_pdf_download_list')
        elif user_id:  
            params['customer'] = get_object_or_404(User, pk=user_id)
            file_name = f"transcript_{params['customer'].username}.pdf"
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename={ file_name }'
            return generate_transcript_pdf(response, **params)
    
    params['qs'] = urlparse(request.get_full_path()).query   
    return render_to_resp(request=request,
                          template_name=template_name,
            context=params)


@is_enabled('trainings')
@login_required
def transcripts_corp_pdf_download(request, tz_id=None,):
    tz = get_object_or_404(CorpTranscriptsZipFile, pk=tz_id)
    if request.user != tz.creator and not request.user.is_superuser:
        raise Http403
    if not tz.zip_file:
        raise Http404
    file_name = tz.zip_file.name.rsplit('/', 1)[-1]
    wrapper = FileWrapper(tz.zip_file)
    response = HttpResponse(wrapper, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    EventLog.objects.log(headline='Training transcript PDFs downloaded',
                                 description=f'{request.user.username} downloaded transcript PDFs for corp profile with id:{tz.corp_profile_id}')
    return response


@is_enabled('trainings')
@login_required
def corp_pdf_download_list(request, tz_id=None,):
    tzs = CorpTranscriptsZipFile.objects.all()
    if not request.user.is_superuser:
        tzs = tzs.filter(creator=request.user)
        if not tzs.exists():
            raise Http404
    tzs = tzs.order_by('-start_dt')

    template_name="trainings/transcripts_pdf_download_list.html"
    return render_to_resp(request=request, template_name=template_name,
                          context={'tzs': tzs})


@is_enabled('trainings')
def delete_downloadable(request, tz_id):
    tz = get_object_or_404(CorpTranscriptsZipFile, pk=tz_id)
    if request.user != tz.creator and not request.user.is_superuser:
        raise Http403
    tz.delete()
    messages.add_message(request, messages.INFO, "Success! An entry has been deleted.")
    return redirect('trainings.corp_pdf_download_list')
