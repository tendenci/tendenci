from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse, reverse_lazy

from tendenci.core.event_logs.models import EventLog

from .models import Newsletter


class NewsletterStatusMixin(object):
    def dispatch(self, request, *args, **kwargs):
        pk = int(kwargs.get('pk'))
        newsletter = get_object_or_404(Newsletter, pk=pk)
        if newsletter.send_status != 'draft':
            return redirect(reverse('newsletter.detail.view', kwargs={'pk': newsletter.pk}))

        return super(NewsletterStatusMixin, self).dispatch(request, *args, **kwargs)


class NewsletterEditLogMixin(object):
    def form_valid(self, form):
        # logging of edits done
        EventLog.objects.log(instance=self.get_object(), action='edit')
        return super(NewsletterEditLogMixin, self).form_valid(form)
