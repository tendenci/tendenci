from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect

from tendenci.core.base.http import Http403
from tendenci.core.perms.decorators import is_enabled
from tendenci.core.perms.utils import update_perms_and_save, get_notice_recipients, has_perm, get_query_filters, has_view_perm
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.event_logs.models import EventLog
from tendenci.core.versions.models import Version
from tendenci.core.meta.models import Meta as MetaTags
from tendenci.core.meta.forms import MetaForm
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.exports.utils import run_export_task

from tendenci.addons.articles.models import Article
from tendenci.addons.articles.forms import ArticleForm, ArticleSearchForm
from tendenci.apps.notifications import models as notification
from tendenci.core.categories.forms import CategoryForm
from tendenci.core.categories.models import Category


@is_enabled('articles')
def detail(request, slug=None, hash=None, template_name="articles/view.html"):
    if not slug and not hash:
        return HttpResponseRedirect(reverse('articles'))

    if hash:
        version = get_object_or_404(Version, hash=hash)
        current_article = get_object_or_404(Article, pk=version.object_id)
        article = version.get_version_object()
        messages.add_message(request, messages.WARNING, 'You are viewing a previous version of this article. View the <a href="%s%s">Current Version</a>.' % (get_setting('site', 'global', 'siteurl'), current_article.get_absolute_url()))
    else:
        article = get_object_or_404(Article, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (article.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

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
def search(request, template_name="articles/search.html"):
    
    filters = get_query_filters(request.user, 'articles.view_article')
    articles = Article.objects.filter(filters).distinct()
    cat = None

    if not request.user.is_anonymous():
        articles = articles.select_related()

    query = request.GET.get('q', None)
    # Handle legacy tag links
    if query and "tag:" in query:
        return HttpResponseRedirect("%s?q=%s&search_category=tags__icontains" %(reverse('articles'), query.replace('tag:', '')))

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
            articles = articles.filter(release_dt__lte=datetime.now())
        else:
            articles = articles.filter(Q(release_dt__lte=datetime.now()) | Q(owner=request.user) | Q(creator=request.user))

    # don't use order_by with "whoosh"
    if not query or settings.HAYSTACK_SEARCH_ENGINE.lower() != "whoosh":
        articles = articles.order_by('-release_dt')
    else:
        articles = articles.order_by('-create_dt')

    EventLog.objects.log()

    # Query list of category and subcategory for dropdown filters
    category = request.GET.get('category')
    try:
        category = int(category)
    except:
        category = 0
    categories, sub_categories = Article.objects.get_categories(category=category)

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
                                           request.POST,
                                           prefix='category')

            if form.is_valid() and categoryform.is_valid():
                article = form.save()
                article.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

                # update all permissions and save the model
                update_perms_and_save(request, form, article)

                messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % article)

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
                                           initial=initial_category_form_data,
                                           prefix='category')
    

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

            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % article)

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
                                           request.POST,
                                           prefix='category')
            if form.is_valid() and categoryform.is_valid():
                article = form.save()
                article.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

                # add all permissions and save the model
                update_perms_and_save(request, form, article)

                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % article)

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
                                               initial=initial_category_form_data,
                                               prefix='category')


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

            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % article)

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
    """Export Articles"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        fields = [
            'guid',
            'slug',
            'timezone',
            'headline',
            'summary',
            'body',
            'source',
            'first_name',
            'last_name',
            'phone',
            'fax',
            'email',
            'website',
            'release_dt',
            'syndicate',
            'featured',
            'design_notes',
            'tags',
            'enclosure_url',
            'enclosure_type',
            'enclosure_length',
            'not_official_content',
            'entity',
        ]
        export_id = run_export_task('articles', 'article', fields)
        EventLog.objects.log()
        return redirect('export.status', export_id)

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
