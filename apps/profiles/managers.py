from django.db.models import Manager

from haystack.query import SearchQuerySet

class ProfileManager(Manager):
    def create_profile(self, user):
        return self.create(user=user, 
                           creator_id=user.id, 
                           creator_username=user.username,
                           owner_id=user.id, 
                           owner_username=user.username, 
                           email=user.email)
        
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query user and profiles. 
            Returns a SearchQuerySet
        """
        from profiles.models import Profile
        sqs = SearchQuerySet()
       
        if query: 
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()
        #sqs = sqs.order_by('user')
        
        return sqs.models(Profile)