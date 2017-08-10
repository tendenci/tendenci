import subprocess
import time

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, Http404
from django.template import RequestContext

from django.http import HttpResponseRedirect, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import update_perms_and_save, get_notice_recipients, has_perm, get_query_filters, has_view_perm
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.versions.models import Version
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.theme.shortcuts import themed_response as render_to_response
from tendenci.apps.exports.utils import run_export_task

from tendenci.apps.articles.models import Article
from tendenci.apps.articles.forms import ArticleForm, ArticleSearchForm
from tendenci.apps.notifications import models as notification
from tendenci.apps.categories.forms import CategoryForm
from tendenci.apps.categories.models import Category, CategoryItem


@is_enabled('articles')
def detail(request, slug=None, hash=None, template_name="articles/view.html"):
    if not slug and not hash:
        return HttpResponseRedirect(reverse('articles'))

    if hash:
        version = get_object_or_404(Version, hash=hash)
        current_article = get_object_or_404(Article, pk=version.object_id)
        article = version.get_version_object()
        msg_string = 'You are viewing a previous version of this article. View the <a href="%s%s">Current Version</a>.' % (get_setting('site', 'global', 'siteurl'), current_article.get_absolute_url())
        messages.add_message(request, messages.WARNING, _(msg_string))
    else:
        article = get_object_or_404(Article, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (article.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

    if not article.release_dt_local and article.release_dt:
        article.assign_release_dt_local()

    if not article.release_dt_local or article.release_dt_local >= datetime.now():
        if not any([
            has_perm(request.user, 'articles.view_article'),
            request.user == article.owner,
            request.user == article.creator
            ]):
            raise Http403

    if has_view_perm(request.user, 'articles.view_article', article):
        EventLog.objects.log(instance=article)
        return render_to_response(template_name, {'article': article},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('articles')
def search(request, template_name="articles/search.html"):

    filters = get_query_filters(request.user, 'articles.view_article')
    articles = Article.objects.filter(filters).distinct()
    cat = None

    if not request.user.is_anonymous():
        articles = articles.select_related()

    query = request.GET.get('q', None)
    if query:
        # Handle legacy tag links
        if "tag:" in query:
            return HttpResponseRedirect("%s?q=%s&search_category=tags__icontains" %(reverse('articles'), query.replace('tag:', '')))

        # Handle legacy category links
        if "category:" in query or "sub_category:" in query:
            key, name = query.split(':')
            category = Category.objects.filter(name__iexact=name)
            if category.exists():
                return HttpResponseRedirect("%s?%s=%s" %(reverse('articles'), key, category[0].pk))
            else:
                return HttpResponseRedirect(reverse('articles'))

    tag = request.GET.get('tag', None)
    form = ArticleSearchForm(request.GET, is_superuser=request.user.is_superuser)

    if tag:
        articles = articles.filter(tags__icontains=tag)

    if form.is_valid():
        cat = form.cleaned_data['search_category']
        filter_date = form.cleaned_data['filter_date']
        date = form.cleaned_data['date']

        if cat in ('featured', 'syndicate'):
            articles = articles.filter(**{cat : True } )
        elif query and cat:
            articles = articles.filter( **{cat : query} )

        if filter_date and date:
            articles = articles.filter( release_dt__month=date.month, release_dt__day=date.day, release_dt__year=date.year )

    if not has_perm(request.user, 'articles.view_article'):
        if request.user.is_anonymous():
            articles = articles.filter(release_dt_local__lte=datetime.now())
        else:
            articles = articles.filter(Q(release_dt_local__lte=datetime.now()) | Q(owner=request.user) | Q(creator=request.user))

    # Query list of category and subcategory for dropdown filters
    category = request.GET.get('category')
    sub_cat = request.GET.get('sub_category')
    try:
        category = int(category)
    except:
        category = 0
    categories, sub_categories = Article.objects.get_categories(category=category)

    if category > 0:
        cat_article_ids = CategoryItem.objects.filter(content_type_id=ContentType.objects.get_for_model(Article), category_id=category, parent_id__isnull=True).values('object_id')
        articles = articles.filter(id__in=[c['object_id'] for c in cat_article_ids])

    if sub_cat:
        try:
            sub_cat = int(sub_cat)
            subcat_article_ids = CategoryItem.objects.filter(content_type_id=ContentType.objects.get_for_model(Article), parent_id=sub_cat, category_id__isnull=True).values('object_id')
            articles = articles.filter(id__in=[c['object_id'] for c in subcat_article_ids])
        except Exception as e:
            pass

    # don't use order_by with "whoosh"
    default_engine = settings.HAYSTACK_CONNECTIONS.get('default', {}).get('ENGINE', '')
    if not query or "whoosh" not in default_engine:
        articles = articles.order_by('-release_dt')
    else:
        articles = articles.order_by('-create_dt')

    EventLog.objects.log()

    return render_to_response(template_name, {'articles': articles,
        'categories': categories, 'form' : form, 'sub_categories': sub_categories},
        context_instance=RequestContext(request))


def search_redirect(request):
    return HttpResponseRedirect(reverse('articles'))


@is_enabled('articles')
def print_view(request, slug, template_name="articles/print-view.html"):
    article = get_object_or_404(Article, slug=slug)

    if article.release_dt >= datetime.now():
        if not any([
            has_perm(request.user, 'articles.view_article'),
            request.user == article.owner,
            request.user == article.creator
            ]):
            raise Http403

    if has_view_perm(request.user, 'articles.view_article', article):
        EventLog.objects.log(instance=article)
        return render_to_response(template_name, {'article': article},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('articles')
@login_required
def edit(request, id, form_class=ArticleForm,
         category_form_class=CategoryForm,
         template_name="articles/edit.html"):
    article = get_object_or_404(Article, pk=id)
    content_type = get_object_or_404(ContentType, app_label='articles',
                                     model='article')

    if has_perm(request.user, 'articles.change_article', article):
        if request.method == "POST":
            form = form_class(request.POST, instance=article, user=request.user)
            categoryform = category_form_class(content_type,
                                           request.POST,)

            if form.is_valid() and categoryform.is_valid():
                article = form.save()
                article.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

                # update all permissions and save the model
                update_perms_and_save(request, form, article)
                msg_string = 'Successfully updated %s' % unicode(article)
                messages.add_message(request, messages.SUCCESS, _(msg_string))

                return HttpResponseRedirect(reverse('article', args=[article.slug]))
        else:
            form = form_class(instance=article, user=request.user)
            category = Category.objects.get_for_object(article, 'category')
            sub_category = Category.objects.get_for_object(article, 'sub_category')

            initial_category_form_data = {
                'app_label': 'articles',
                'model': 'article',
                'pk': article.pk,
                'category': getattr(category, 'name', '0'),
                'sub_category': getattr(sub_category, 'name', '0')
            }
            categoryform = category_form_class(content_type,
                                           initial=initial_category_form_data,)


        return render_to_response(template_name, {'article': article,
                                                  'form': form,
                                                  'categoryform': categoryform,},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('articles')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="articles/edit-meta.html"):
    # check permission
    article = get_object_or_404(Article, pk=id)
    if not has_perm(request.user, 'articles.change_article', article):
        raise Http403

    defaults = {
        'title': article.get_title(),
        'description': article.get_description(),
        'keywords': article.get_keywords(),
        'canonical_url': article.get_canonical_url(),
    }
    article.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=article.meta)
        if form.is_valid():
            article.meta = form.save()  # save meta
            article.save()  # save relationship
            msg_string = 'Successfully updated meta for %s' % unicode(article)
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return HttpResponseRedirect(reverse('article', args=[article.slug]))
    else:
        form = form_class(instance=article.meta)

    return render_to_response(template_name, {'article': article, 'form': form},
        context_instance=RequestContext(request))


@is_enabled('articles')
@login_required
def add(request, form_class=ArticleForm,
        category_form_class=CategoryForm,
        template_name="articles/add.html"):
    content_type = get_object_or_404(ContentType,
                                     app_label='articles',
                                     model='article')
    if has_perm(request.user, 'articles.add_article'):
        if request.method == "POST":
            form = form_class(request.POST, user=request.user)
            categoryform = category_form_class(content_type,
                                           request.POST,)
            if form.is_valid() and categoryform.is_valid():
                article = form.save()
                article.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

                # add all permissions and save the model
                update_perms_and_save(request, form, article)
                msg_string = 'Successfully added %s' % unicode(article)
                messages.add_message(request, messages.SUCCESS, _(msg_string))

                # send notification to administrator(s) and module recipient(s)
                recipients = get_notice_recipients('module', 'articles', 'articlerecipients')
                if recipients and notification:
                    notification.send_emails(recipients, 'article_added', {
                        'object': article,
                        'request': request,
                    })

                return HttpResponseRedirect(reverse('article', args=[article.slug]))
        else:
            form = form_class(user=request.user)
            initial_category_form_data = {
                'app_label': 'articles',
                'model': 'article',
                'pk': 0,
            }
            categoryform = category_form_class(content_type,
                                               initial=initial_category_form_data,)


        return render_to_response(template_name, {'form': form,
                                                  'categoryform': categoryform,},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('articles')
@login_required
def delete(request, id, template_name="articles/delete.html"):
    article = get_object_or_404(Article, pk=id)

    if has_perm(request.user, 'articles.delete_article'):
        if request.method == "POST":
            msg_string = 'Successfully deleted %s' % unicode(article)
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            # send notification to administrators
            recipients = get_notice_recipients('module', 'articles', 'articlerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': article,
                        'request': request,
                    }
                    notification.send_emails(recipients, 'article_deleted', extra_context)

            article.delete()

            return HttpResponseRedirect(reverse('article.search'))

        return render_to_response(template_name, {'article': article},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('articles')
@staff_member_required
def articles_report(request, template_name='reports/articles.html'):
    article_type = ContentType.objects.get(app_label="articles", model="article")
    stats = EventLog.objects.filter(content_type=article_type,
                                    action='detail') \
                    .values('content_type', 'object_id', 'headline')\
                    .annotate(count=Count('pk'))\
                    .order_by('-count')

    # get sort order
    sort = request.GET.get('sort', 'viewed')
    if sort == 'viewed':
        stats = stats.order_by('-count')
    elif sort == 'name':
        stats = stats.order_by('headline')
    elif sort == 'created':
        stats = stats.order_by('create_dt')

    for item in stats:

        try:
            article = Article.objects.get(pk=item['object_id'])
            item['article'] = article
            if article.age().days > 0:
                item['per_day'] = item['count'] * 1.0 / article.age().days
            else:
                item['per_day'] = item['count'] * 1.0
        except Article.DoesNotExist:
            pass

    EventLog.objects.log()

    # special sort option
    if sort == 'day':
        stats = sorted(stats, key=lambda item: item['per_day'], reverse=True)

    return render_to_response(template_name, {
        'stats': stats
    }, context_instance=RequestContext(request))


@is_enabled('articles')
@login_required
def export(request, template_name="articles/export.html"):
    """Export Profiles"""
    if not request.user.profile.is_staff:
        raise Http403

    if request.method == "POST" and "download" in request.POST:
        identifier = int(time.time())
        temp_file_path = 'export/articles/%s_temp.csv' % identifier
        default_storage.save(temp_file_path, ContentFile(''))

        # start the process
        subprocess.Popen(["python", "manage.py",
                          "articles_export_process",
                          '--identifier=%s' % identifier,
                          '--user=%s' % request.user.id])
        # log an event
        EventLog.objects.log()
        return HttpResponseRedirect(reverse('article.export_status', args=[identifier]))

    return render_to_response(template_name, {}, RequestContext(request))


@is_enabled('articles')
@login_required
def export_status(request, identifier, template_name="articles/export-status.html"):
    """Display export status"""
    if not request.user.profile.is_staff:
        raise Http403

    export_path = 'export/articles/%s.csv' % identifier
    download_ready = False
    if default_storage.exists(export_path):
        download_ready = True
    else:
        temp_export_path = 'export/articles/%s_temp.csv' % identifier
        if not default_storage.exists(temp_export_path) and \
                not default_storage.exists(export_path):
            raise Http404

    context = {'identifier': identifier,
               'download_ready': download_ready}
    return render_to_response(template_name, context, RequestContext(request))


@is_enabled('articles')
@login_required
def export_download(request, identifier):
    """Download the profiles export."""
    if not request.user.profile.is_staff:
        raise Http403

    file_name = '%s.csv' % identifier
    file_path = 'export/articles/%s' % file_name
    if not default_storage.exists(file_path):
        raise Http404

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="articles_export_%s"' % file_name
    response.content = default_storage.open(file_path).read()
    return response
