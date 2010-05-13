# django
from django.shortcuts import render_to_response
from django.template import RequestContext

# local
from articles.models import Article
from articles.permissions import ArticlePermission
from base.auth import Authorize

# Create your views here.
def articles(request, template_name="articles/articles.html"): 
    authorize = Authorize(request.user, ArticlePermission)
    
    print authorize.view()
    # print authorize.change()
    # print authorize.delete()
    
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))