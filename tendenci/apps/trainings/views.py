
#from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

#from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from .models import TeachingActivity
from .forms import TeachingActivityForm


class TeachingActivityCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'trainings/teaching_activities/add.html'
    form_class = TeachingActivityForm
    model = TeachingActivity
    #success_url = reverse('trainings.teaching_activities')
    success_message = _('Teaching Activity was added successfully')

    def form_valid(self, form):
        form.instance.user = self.request.user
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
