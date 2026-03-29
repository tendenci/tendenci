from datetime import datetime, timedelta
import subprocess

from django.views.generic import DetailView, ListView, CreateView, RedirectView
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from tendenci.libs.utils import python_executable
from tendenci.apps.perms.decorators import superuser_required
from tendenci.apps.reports.models import Report, Run
from tendenci.apps.reports.forms import ReportForm, RunForm


class ReportListView(ListView):
#     def get_redirect_url(self, *args, **kwargs):
#         # redirect to invoices reports overview
#         return reverse('invoices.reports_overview')
    model = Report
    context_object_name = "reports"
    template_name = "reports/report_list.html"

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm
    template_name = "reports/report_create.html"

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        # Pass in the request so we can use it in the save
        self.object = form.save(commit=False, request=self.request)
        return HttpResponseRedirect(self.get_success_url())


class ReportDetailView(DetailView):
    model = Report
    template_name = "reports/report_detail.html"

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class RunCreateView(CreateView):
    model = Run
    form_class = RunForm
    template_name = "reports/report_run_create.html"

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        # Get the Report ID to associate
        initial.update({
            'report': self.kwargs.get('report_id'),
            'range_start_dt': timezone.now()-timedelta(days=30),
            'range_end_dt': timezone.now()
        })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report'] = get_object_or_404(Report, pk=self.kwargs.get('report_id'))
        return context

    def form_valid(self, form):
        # Pass in the request so we can use it in the save
        self.object = form.save(commit=False, request=self.request)
        return HttpResponseRedirect(self.get_success_url())


class RunDetailView(DetailView):
    model = Run
    template_name = "reports/report_run_detail.html"

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        #invalidate('reports_run')
        obj = get_object_or_404(Run, pk=self.kwargs['pk'], report_id=self.kwargs['report_id'])
        if obj.status == "unstarted":
            subprocess.Popen([python_executable(), "manage.py", "process_report_run", str(obj.pk)])
        return obj


class RunOutputView(DetailView):
    model = Run
    template_name = "reports/report_run_output.html"

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        #invalidate('reports_run')
        obj = get_object_or_404(Run, pk=self.kwargs['pk'], report_id=self.kwargs['report_id'])
        return obj
