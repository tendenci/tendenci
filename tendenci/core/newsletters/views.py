import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.template import Template as DTemplate
from django.template.loader import render_to_string
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import TemplateView, FormView, UpdateView, DetailView, ListView
from django.core.urlresolvers import reverse, reverse_lazy

from tendenci.core.base.http import Http403
from tendenci.core.emails.models import Email
from tendenci.core.newsletters.utils import apply_template_media
from tendenci.core.newsletters.models import NewsletterTemplate, Newsletter
from tendenci.core.newsletters.forms import (
    GenerateForm,
    OldGenerateForm,
    MarketingStepOneForm,
    MarketingStepThreeForm,
    MarketingStepFourForm,
    MarketingStep2EmailFilterForm)
from tendenci.core.newsletters.utils import (
    newsletter_articles_list,
    newsletter_jobs_list,
    newsletter_news_list,
    newsletter_pages_list,
    newsletter_events_list)
from tendenci.core.perms.utils import has_perm
from tendenci.core.site_settings.utils import get_setting


class NewsletterGeneratorView(TemplateView):
    template_name="newsletters/newsletter_generator.html"

    def get_context_data(self, **kwargs):
        context = super(NewsletterGeneratorView, self).get_context_data(**kwargs)
        cm_api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
        cm_client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)

        context['CAMPAIGNMONITOR_ENABLED'] = (cm_api_key and cm_client_id)
        return context


class NewsletterGeneratorOrigView(FormView):
    template_name = "newsletters/add.html"
    form_class = OldGenerateForm

    def get_initial(self):
        site_name = get_setting('site', 'global', 'sitedisplayname')
        date_string = datetime.datetime.now().strftime("%d-%b-%Y")
        subject_initial = site_name + ' Newsletter ' + date_string

        return {'subject': subject_initial}

    def form_valid(self, form):
        nl = form.save()
        self.object_id = nl.pk
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('newsletter.action.step1', kwargs={'pk': self.object_id })

    def get_context_data(self, **kwargs):
        context = super(NewsletterGeneratorOrigView, self).get_context_data(**kwargs)
        templates = NewsletterTemplate.objects.all()
        context['templates'] = templates

        return context

    def get_form_kwargs(self):
        kwargs = super(NewsletterGeneratorOrigView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        return kwargs


class MarketingActionStepOneView(UpdateView):
    model = Newsletter
    form_class = MarketingStepOneForm
    template_name = 'newsletters/actions/step1.html'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('newsletter.action.step2', kwargs={'pk': obj.pk})


class MarketingActionStepTwoView(ListView):
    paginate_by = 10
    model = Email
    template_name = 'newsletters/actions/step2.html'


    def get(self, request, *args, **kwargs):
        self.form = MarketingStep2EmailFilterForm(request.GET)
        return super(MarketingActionStepTwoView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MarketingActionStepTwoView, self).get_context_data(**kwargs)
        pk = int(self.kwargs.get('pk'))
        context['newsletter'] = get_object_or_404(Newsletter, pk=pk)
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


class MarketingActionStepThreeView(UpdateView):
    model = Newsletter
    form_class = MarketingStepThreeForm
    template_name = 'newsletters/actions/step3.html'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('newsletter.action.step4', kwargs={'pk': obj.pk})


class MarketingActionStepFourView(UpdateView):
    model = Newsletter
    form_class = MarketingStepFourForm
    template_name = 'newsletters/actions/step4.html'


class MarketingActionStepFiveView(TemplateView):
    template_name = 'newsletters/actions/step5.html'



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

    news_content = ""
    news = int(request.GET.get('news', 1))
    news_days = request.GET.get('news_days',30)
    if news:
        news_list, news_content = newsletter_news_list(request, news_days, simplified)

    jobs_content = ""
    jobs = int(request.GET.get('jobs', 1))
    jobs_days = request.GET.get('jobs_days', 30)
    if jobs:
        jobs_list, jobs_content = newsletter_jobs_list(request, jobs_days, simplified)

    pages_content = ""
    pages = int(request.GET.get('pages', 0))
    pages_days = request.GET.get('pages_days', 7)
    if pages:
        pages_list, pages_content = newsletter_pages_list(request, pages_days, simplified)

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
