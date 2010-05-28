from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from articles.models import Article
from perms.models import ObjectPermission

user_query_set = User.objects.filter(is_active=True)
user_perm_options = {
    'label':'People',
    'help_text':'People who have permissions on this article',
    'required':False,
    'queryset':user_query_set                    
}

#class ArticleForm(forms.ModelForm):
#    user_perms = forms.ModelMultipleChoiceField(**user_perm_options)
#    class Meta:
#        model = Article
#        fields = (
#        'headline',
#        'summary',
#        'body',
#        'source',
#        'website',
#        'release_dt',
#        'timezone',
#        'first_name',
#        'last_name',
#        'phone',
#        'fax',
#        'email',
#        'enclosure_url',
#        'enclosure_type',
#        'enclosure_length',
#        'allow_anonymous_view',
#        'allow_anonymous_edit',
#        'allow_user_view',
#        'allow_user_edit',
#        'syndicate',
#        'featured',
#        'not_official_content',
#        'status',
#        'status_detail',
#        'user_perms',
#        )
#      
#    def __init__(self, user=None, *args, **kwargs):
#        self.user = user 
#        super(ArticleForm, self).__init__(*args, **kwargs)

class ArticleForm(forms.ModelForm):
    user_perms = forms.ModelMultipleChoiceField(**user_perm_options)
    class Meta:
        model = Article
        fields = (
        'headline',
        'summary',
        'body',
        'source',
        'website',
        'release_dt',
        'timezone',
        'first_name',
        'last_name',
        'phone',
        'fax',
        'email',
        'enclosure_url',
        'enclosure_type',
        'enclosure_length',
        'allow_anonymous_view',
        'allow_anonymous_edit',
        'allow_user_view',
        'allow_user_edit',
        'syndicate',
        'featured',
        'not_official_content',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(ArticleForm, self).__init__(*args, **kwargs)
        
        # TODO: Create permissions form field that takes care of 
        # the permissions below. 
        
        # assign user permissions
        if 'instance' in kwargs:
            instance = kwargs['instance']
            content_type = ContentType.objects.get_for_model(instance)
            filters = {
                'user__in':user_query_set, 
                'content_type':content_type,
                'object_id':instance.pk       
            }
            users_with_perms = ObjectPermission.objects.filter(**filters)
            if users_with_perms:
                users_with_perms = list(set([u.user.pk for u in users_with_perms]))
                self.fields['user_perms'].initial = users_with_perms
        
        