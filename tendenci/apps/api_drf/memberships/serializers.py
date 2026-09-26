from rest_framework import serializers

from tendenci.apps.memberships.models import MembershipDefault, MembershipType


class MembershipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipType
        fields = ['id', 'name', 'description', 'price', 
                  'renewal_price', 'admin_fee', 'group_id', 
                  'require_approval', 'require_payment_approval',
                  'allow_renewal', 
                  'renewal_period_start', 'renewal_period_end',
                  'expiration_grace_period', 'status_detail']


class MembershipSerializer(serializers.ModelSerializer):
    #membership_type = MembershipTypeSerializer(read_only=True)
    class Meta:
        model = MembershipDefault
        fields = ['id', 'user_id', 'membership_type_id', 'member_number', 'join_dt', 
                  'renew_dt', 'renewal', 'expire_dt', 'certifications',
                  'work_experience', 'referer_url', 'referral_source', 'referral_source_other',
                  'referral_source_member_name', 'referral_source_member_number', 'affiliation_member_number',
                  'primary_practice', 'how_long_in_practice', 'notes', 'admin_notes',
                  'application_approved', 'application_approved_dt', 'payment_method', 'chapter',
                  'areas_of_expertise', 'corp_profile_id', 'corporate_membership_id', 'home_state',
                  'year_left_native_country', 'network_sectors', 'networking', 'government_worker',
                  'government_agency', 'license_number', 'license_state', 'industry',
                  'region', 'company_size', 'groups', 'app',
                  'status_detail', 'create_dt']