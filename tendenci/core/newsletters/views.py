import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.template import Template as DTemplate
from django.template.loader import render_to_string
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import TemplateView, FormView, UpdateView, DetailView, ListView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from tendenci.core.base.http import Http403
from tendenci.core.emails.models import Email
from tendenci.core.event_logs.models import EventLog
from tendenci.core.newsletters.utils import apply_template_media, is_newsletter_relay_set
from tendenci.core.newsletters.models import NewsletterTemplate, Newsletter
from tendenci.core.newsletters.forms import (
    GenerateForm,
    OldGenerateForm,
    MarketingStepOneForm,
    MarketingStepThreeForm,
    MarketingStepFourForm,
    MarketingStepFiveForm,
    MarketingStep2EmailFilterForm,
    NewslettterEmailUpdateForm
    )
from tendenci.core.newsletters.mixins import (
    NewsletterEditLogMixin,
    NewsletterStatusMixin,
    NewsletterPermissionMixin,
    NewsletterPermStatMixin,
    NewsletterPassedSLAMixin
    )
from tendenci.core.newsletters.utils import (
    newsletter_articles_list,
    newsletter_jobs_list,
    newsletter_news_list,
    newsletter_pages_list,
    newsletter_events_list,
    newsletter_directories_list,
    newsletter_resumes_list)
from tendenci.core.perms.utils import has_perm, get_query_filters
from tendenci.core.site_settings.utils import get_setting



class NewsletterGeneratorView(TemplateView):
    template_name="newsletters/newsletter_generator.html"

    def get_context_data(self, **kwargs):
        context = super(NewsletterGeneratorView, self).get_context_data(**kwargs)
        cm_api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
        cm_client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)

        context['CAMPAIGNMONITOR_ENABLED'] = (cm_api_key and cm_client_id)
        return context


class NewsletterListView(NewsletterPermissionMixin, ListView):
    model = Newsletter
    paginate_by = 10
    newsletter_permission = 'newsletters.view_newsletter'
    template_name = 'newsletters/search.html'

    def get_queryset(self, **kwargs):
        qset = super(NewsletterListView, self).get_queryset(**kwargs)
        qset = qset.order_by('-date_created')

        return qset


class NewsletterGeneratorOrigView(NewsletterPermissionMixin, FormView):
    template_name = "newsletters/add.html"
    form_class = OldGenerateForm
    newsletter_permission = 'newsletters.add_newsletter'

    def get_initial(self):
        site_name = get_setting('site', 'global', 'sitedisplayname')
        date_string = datetime.datetime.now().strftime("%d-%b-%Y")
        subject_initial = site_name + ' Newsletter ' + date_string

        return {'subject': subject_initial}

    def form_valid(self, form):
        nl = form.save()
        self.object_id = nl.pk

        # add event logging
        EventLog.objects.log(action='add')

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('newsletter.action.step4', kwargs={'pk': self.object_id })

    def get_context_data(self, **kwargs):
        context = super(NewsletterGeneratorOrigView, self).get_context_data(**kwargs)
        templates = NewsletterTemplate.objects.all()
        context['templates'] = templates

        return context

    def get_form_kwargs(self):
        kwargs = super(NewsletterGeneratorOrigView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        return kwargs


class MarketingActionStepOneView(NewsletterPermStatMixin, NewsletterEditLogMixin, UpdateView):
    model = Newsletter
    form_class = MarketingStepOneForm
    template_name = 'newsletters/actions/step1.html'
    newsletter_permission = 'newsletters.change_newsletter'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('newsletter.action.step2', kwargs={'pk': obj.pk})


class MarketingActionStepTwoView(NewsletterPermStatMixin, ListView):
    paginate_by = 10
    model = Email
    template_name = 'newsletters/actions/step2.html'
    newsletter_permission = 'newsletters.change_newsletter'

    def get(self, request, *args, **kwargs):
        self.form = MarketingStep2EmailFilterForm(request.GET)
        return super(MarketingActionStepTwoView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MarketingActionStepTwoView, self).get_context_data(**kwargs)
        pk = int(self.kwargs.get('pk'))
        context['object'] = get_object_or_404(Newsletter, pk=pk)
        context['form'] = self.form
        return context

    def get_queryset(self):
        qset = super(MarketingActionStepTwoView, self).get_queryset()
        qset = qset.filter(status=True, status_detail='active').order_by('-pk')
        request = self.request
        form = self.form

        if 'search_criteria' in request.GET and 'q' in request.GET:
            qset = form.filter_email(request, qset)

        return qset


class NewsletterUpdateEmailView(NewsletterPermStatMixin, NewsletterEditLogMixin, UpdateView):
    model = Newsletter
    form_class = NewslettterEmailUpdateForm
    template_name = 'newsletters/actions/step2.html'
    newsletter_permission = 'newsletters.change_newsletter'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('newsletter.action.step3', kwargs={'pk': obj.pk})


class MarketingActionStepThreeView(NewsletterPermStatMixin, NewsletterEditLogMixin, UpdateView):
    model = Newsletter
    form_class = MarketingStepThreeForm
    template_name = 'newsletters/actions/step3.html'
    newsletter_permission = 'newsletters.change_newsletter'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('newsletter.action.step4', kwargs={'pk': obj.pk})


class MarketingActionStepFourView(NewsletterPermStatMixin, NewsletterEditLogMixin, UpdateView):
    model = Newsletter
    form_class = MarketingStepFourForm
    template_name = 'newsletters/actions/step4.html'
    newsletter_permission = 'newsletters.change_newsletter'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('newsletter.action.step5', kwargs={'pk': obj.pk})


class MarketingActionStepFiveView(NewsletterPermStatMixin, NewsletterPassedSLAMixin, UpdateView):
    model = Newsletter
    template_name = 'newsletters/actions/step5.html'
    form_class = MarketingStepFiveForm
    newsletter_permission = 'newsletters.change_newsletter'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('newsletter.detail.view', kwargs={'pk': obj.pk})

    def form_valid(self, form):
        EventLog.objects.log(instance=self.get_object(), action='send')
        messages.success(self.request,
            "Your newsletter has been scheduled to send within the next 10 minutes. "
            "Please note that it may take several hours to complete the process depending "
            "on the size of your user group. You will receive an email notification when it's done."
            )
        return super(MarketingActionStepFiveView, self).form_valid(form)


class NewsletterDetailView(NewsletterPermissionMixin, NewsletterPassedSLAMixin, DetailView):
    model = Newsletter
    template_name = 'newsletters/actions/view.html'
    newsletter_permission = 'newsletters.view_newsletter'

    def get(self, request, *args, **kwargs):
        EventLog.objects.log(instance=self.get_object(), action='view')
        return super(NewsletterDetailView, self).get(request, *args, **kwargs)


class NewsletterResendView(NewsletterPermissionMixin, NewsletterPassedSLAMixin, DetailView):
    model = Newsletter
    template_name = 'newsletters/actions/view.html'
    newsletter_permission = 'newsletters.view_newsletter'

    def dispatch(self, request, *args, **kwargs):
        pk = int(kwargs.get('pk'))
        newsletter = get_object_or_404(Newsletter, pk=pk)
        if newsletter.send_status == 'draft':
            return redirect(reverse('newsletter.action.step4', kwargs={'pk': newsletter.pk}))

        elif newsletter.send_status == 'sending' or newsletter.send_status == 'resending':
            return redirect(reverse('newsletter.detail.view', kwargs={'pk': newsletter.pk}))

        if not is_newsletter_relay_set():
            messages.error(request, _('Email relay is not configured properly.'
                ' Newsletter cannot be sent.'))
            return redirect(reverse('newsletter.detail.view', kwargs={'pk': newsletter.pk}))

        return super(NewsletterResendView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        newsletter = self.get_object()
        if newsletter.send_status == 'sent' or newsletter.send_status == 'resent':
            newsletter.send_status = 'resending'
            newsletter.save()
            newsletter.send_to_recipients()
            EventLog.objects.log(instance=newsletter, action='resend')
            messages.success(request, 'Resending newsletters.'
                "Your newsletter has been scheduled to send within the next 10 minutes. "
            "Please note that it may take several hours to complete the process depending "
            "on the size of your user group. You will receive an email notification when it's done.")
            return redirect(reverse('newsletter.detail.view', kwargs={'pk': newsletter.pk}))

        return super(NewsletterResendView, self).get(request, *args, **kwargs)


class NewsletterDeleteView(NewsletterPermissionMixin, DeleteView):
    model = Newsletter
    newsletter_permission = 'newsletters.delete_newsletter'
    template_name = 'newsletters/delete.html'
    success_url = reverse_lazy('newsletter.list')


@login_required
def generate(request):
    """
    Newsletter generator form
    """
    if not has_perm(request.user,'newsletters.add_newsletter'):
        raise Http403

    if request.method == 'POST':
        form = GenerateForm(request.POST)
        if form.is_valid():
            template = form.cleaned_data['template']

            html_url = [
                reverse('newsletter.template_render', args=[template.template_id]),
                u'?jump_links=%s' % form.cleaned_data.get('jump_links'),
                '&events=%s' % form.cleaned_data.get('events'),
                '&events_type=%s' % form.cleaned_data.get('events_type'),
                '&event_start_dt=%s' % form.cleaned_data.get('event_start_dt', u''),
                '&event_end_dt=%s' % form.cleaned_data.get('event_end_dt', u''),
                '&articles=%s' % form.cleaned_data.get('articles', u''),
                '&articles_days=%s' % form.cleaned_data.get('articles_days', u''),
                '&news=%s' % form.cleaned_data.get('news', u''),
                '&news_days=%s' % form.cleaned_data.get('news_days', u''),
                '&jobs=%s' % form.cleaned_data.get('jobs', u''),
                '&jobs_days=%s' % form.cleaned_data.get('jobs_days', u''),
                '&pages=%s' % form.cleaned_data.get('pages', u''),
                '&pages_days=%s' % form.cleaned_data.get('pages_days', u''),
                ]

            return redirect(''.join(html_url))

    form = GenerateForm()

    return render(request, 'newsletters/generate.html', {'form':form})

@login_required
def template_view(request, template_id, render=True):
    """
    Generate newsletter preview
    Combine template with context passed via GET
    """
    template = get_object_or_404(NewsletterTemplate, template_id=template_id)
    if not template.html_file:
        raise Http404

    if not has_perm(request.user, 'newsletters.view_newslettertemplate'):
        raise Http403

    simplified = True
    login_content = ""
    include_login = int(request.GET.get('include_login', 0))
    if include_login:
        login_content = render_to_string('newsletters/login.txt',
                                        context_instance=RequestContext(request))

    jumplink_content = ""
    jump_links = int(request.GET.get('jump_links', 1))
    if jump_links:
        jumplink_content = render_to_string('newsletters/jumplinks.txt', locals(),
                                        context_instance=RequestContext(request))

    art_content = ""
    articles = int(request.GET.get('articles', 1))
    articles_days = request.GET.get('articles_days', 60)
    if articles:
        articles_list, articles_content = newsletter_articles_list(request, articles_days, simplified)
    else:
        articles_list = []
        articles_content = []

    news_content = ""
    news = int(request.GET.get('news', 1))
    news_days = request.GET.get('news_days',30)
    if news:
        news_list, news_content = newsletter_news_list(request, news_days, simplified)
    else:
        news_list = []
        news_content = []

    jobs_content = ""
    jobs = int(request.GET.get('jobs', 1))
    jobs_days = request.GET.get('jobs_days', 30)
    if jobs:
        jobs_list, jobs_content = newsletter_jobs_list(request, jobs_days, simplified)
    else:
        jobs_list = []
        jobs_content = []

    pages_content = ""
    pages = int(request.GET.get('pages', 0))
    pages_days = request.GET.get('pages_days', 7)
    if pages:
        pages_list, pages_content = newsletter_pages_list(request, pages_days, simplified)
    else:
        pages_list = []
        pages_content = []

    directories_content = ""
    directories = int(request.GET.get('directories', 0))
    directories_days = request.GET.get('directories_days', 7)
    if directories:
        directories_list, directories_content = newsletter_directories_list(request, directories_days, simplified)
    else:
        directories_list = []
        directories_content = []

    resumes_content = ""
    resumes = int(request.GET.get('resumes', 0))
    resumes_days = request.GET.get('resumes_days', 7)
    if resumes:
        resumes_list, resumes_content = newsletter_resumes_list(request, resumes_days, simplified)
    else:
        resumes_list = []
        resumes_content = []

    try:
        events = int(request.GET.get('events', 1))
        events_type = request.GET.get('events_type')
        start_y, start_m, start_d = request.GET.get('event_start_dt', str(datetime.date.today())).split('-')
        event_start_dt = datetime.date(int(start_y), int(start_m), int(start_d))

        end_y, end_m, end_d = request.GET.get(
            'event_end_dt',
            str(datetime.date.today() + datetime.timedelta(days=90))).split('-')
        event_end_dt = datetime.date(int(end_y), int(end_m), int(end_d))

        events_list, events_content = newsletter_events_list(
            request,
            start_dt=event_start_dt,
            end_dt=event_end_dt,
            simplified=simplified)

    except ImportError:
        events_list = []
        events_type = None

    text = DTemplate(apply_template_media(template))
    context = RequestContext(request,
            {
                'jumplink_content':jumplink_content,
                'login_content':login_content,
                "art_content":articles_content, # legacy usage in templates
                "articles_content":articles_content,
                "articles_list":articles_list,
                "jobs_content":jobs_content,
                "jobs_list":jobs_list,
                "news_content":news_content,
                "news_list":news_list,
                "pages_content":pages_content,
                "pages_list":pages_content,
                "directories_content":directories_content,
                "directories_list":directories_list,
                "resumes_content":resumes_content,
                "resumes_list":resumes_list,
                "events":events_list, # legacy usage in templates
                "events_content":events_content,
                "events_list":events_list,
                "events_type":events_type
            })
    content = text.render(context)

    if render:
        response = HttpResponse(content)
        return response
    else:
        template_name="newsletters/content.html"
        return render_to_response(
            template_name, {
            'content': content,
            'template': template},
            context_instance=RequestContext(request))


@login_required
def default_template_view(request):
    template_name = request.GET.get('template_name', '')
    if not template_name:
        raise Http404
    return render (request, template_name)


def view_email_from_browser(request, pk):
    nl = get_object_or_404(Newsletter, pk=pk)
    email = nl.email
    if email == None:
        raise Http404
    if not email.allow_view_by(request.user):
        # check if security_key is in GET
        key = request.GET.get("key", "")
        if key == "" or key != nl.security_key:
            raise Http403

    return render_to_response("newsletters/viewbody.html", {'email': email},
                                context_instance=RequestContext(request))
