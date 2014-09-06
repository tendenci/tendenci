from django.contrib.auth.models import User
from tastypie import fields
from tendenci.apps.api_tasty.resources import TendenciResource
from tendenci.apps.api_tasty.validation import TendenciValidation
from tendenci.apps.api_tasty.users.resources import UserResource
from tendenci.apps.api_tasty.payments.resources import PaymentMethodResource
from tendenci.apps.api_tasty.memberships.forms import MembershipForm
from tendenci.apps.memberships.models import MembershipDefault, MembershipType, MembershipApp


class MembershipTypeResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = MembershipType.objects.all()
        resource_name = 'membership_type'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']


class AppResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = MembershipApp.objects.all()
        resource_name = 'app'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']


class MembershipResource(TendenciResource):
    """Membership API
    list:
    *example: http://0.0.0.0:8000/api_tasty/v1/membership/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf
    *extra GET filters: mem_id, mem_type, mem_app, mem_corp_mem_id, mem_username, mem_userid
    create:
    *example: curl -H "Content-Type: application/json" -X POST --data @data.json "http://0.0.0.0:8000/api_tasty/v1/membership/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf"
    *create options: if create_user is set to true the username and password fields are used to create a new user otherwise username is required to associate to an existing user.
    update:
    curl -H "Content-Type: application/json" -X PUT --data @data.json "http://0.0.0.0:8000/api_tasty/v1/membership/12/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf"
    *update options: same sa create's options
    delete:
    *example: curl -H "Content-Type: application/json" -X DELETE "http://0.0.0.0:8000/api_tasty/v1/membership/12/?format=json&username=sam&api_key=6f21b5cad4841d7ba76e6d76d5b9332dddf109bf"
    """

    user = fields.ForeignKey(UserResource, 'user')
    membership_type = fields.ForeignKey(MembershipTypeResource, 'membership_type')
    ma = fields.ForeignKey(AppResource, 'ma', null=True)
    payment_method = fields.ForeignKey(PaymentMethodResource, 'payment_method', null=True)

    class Meta(TendenciResource.Meta):
        queryset = MembershipDefault.objects.all()
        resource_name = 'membership'
        validation = TendenciValidation(form_class=MembershipForm)
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']

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
            mems = mems.filter(membership_type__pk=mem_type)
        if mem_app:
            mems = mems.filter(ma__pk=mem_app)
        if corp_mem_id:
            mems = mems.filter(corporate_membership_id=corp_mem_id)
        if username:
            mems = mems.filter(user__username=username)
        if userid:
            mems = mems.filter(user__pk=userid)

        return mems

    def obj_create(self, bundle, request=None, **kwargs):
        data = bundle.data

        if data['create_user']:
            print "creating user"
            user = User.objects.create(username=data['username'])
            user.set_password(data['password'])
        else:
            user = User.objects.get(username=data['username'])

        mem = MembershipDefault()
        mem.user = user
        for key in data:
            setattr(mem, key, data[key])

        mem.save()

        bundle.obj = mem

        return bundle
