from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ImproperlyConfigured

from tendenci.apps.perms.utils import has_perm
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.base.http import Http403

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


class NewsletterPermissionMixin(object):
    newsletter_permission = None

    def get_obj(self):
        try:
            obj = self.get_object()
        except AttributeError:
            obj = None
        return obj

    def get_newsletter_permission(self):
        if not self.newsletter_permission:
            raise ImproperlyConfigured('Permission is not properly configured on the view.')
        return self.newsletter_permission

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_obj()
        perm = self.get_newsletter_permission()
        if not has_perm(request.user, perm, obj=obj):
            raise Http403

        return super(NewsletterPermissionMixin, self).dispatch(request, *args, **kwargs)


class NewsletterPermStatMixin(NewsletterPermissionMixin, NewsletterStatusMixin):
    pass


class NewsletterPassedSLAMixin(object):
    def dispatch(self, request, *args, **kwargs):
        pk = int(kwargs.get('pk'))
        newsletter = get_object_or_404(Newsletter, pk=pk)
        if not newsletter.sla:
            return redirect(reverse('newsletter.action.step4', kwargs={'pk': newsletter.pk}))
        return super(NewsletterPassedSLAMixin, self).dispatch(request, *args, **kwargs)
