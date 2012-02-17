from tastypie import fields
from tastypie.validation import CleanedDataFormValidation
from api_tasty.resources import TendenciResource
from api_tasty.users.resources import UserResource
from memberships.models import Membership, MembershipType, App

class MembershipTypeResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = MembershipType.objects.all()
        resource_name = 'membership_type'
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        
class AppResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = App.objects.all()
        resource_name = 'app'
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]

class MembershipResource(TendenciResource):
    """Membership API
    list: /api_tasty/v1/membership/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf
    """
    
    user = fields.ForeignKey(UserResource, 'user')
    membership_type = fields.ForeignKey(MembershipTypeResource, 'membership_type')
    app = fields.ForeignKey(AppResource, 'app', null=True)
    
    class Meta(TendenciResource.Meta):
        queryset = Membership.objects.all()
        resource_name = 'membership'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        
    def get_object_list(self, request):
        """Membership list filtered by GET params
        """
        # initialize all filters:
        mem_id = request.GET.get('mem_id', None)
        mem_type = request.GET.get('mem_type', None)
        mem_app = request.GET.get('mem_app', None)
        corp_mem_id = request.GET.get('mem_corp_mem_id', None)
        username = request.GET.get('mem_username', None)
        userid = request.GET.get('mem_userid', None)
        
        mems = self._meta.queryset._clone()
        if mem_id:
            mems = mems.filter(pk=mem_id)
        if mem_type:
            mems = mems.filter(membership_type__pk=mt)
        if mem_app:
            mems = mems.filter(ma__pk=ma)
        if corp_mem_id:
            mems = mems.filter(corporate_membership_id=corp_mem_id)
        if username:
            mems = mems.filter(user__username=username)
        if userid:
            mems = mems.filter(user__pk=userid)
        
        return mems
