from tendenci.apps.profiles.models import Profile


def update_profiles_total_spend(instance, **kwargs):
    """
    adds total to profiles.total_spend if status_detail=='tendered'
    @instance invoices.Invoice object
    """
    if instance.status_detail == 'tendered':
        user = instance.owner or instance.creator
        if not user:
            return

        try:
            profile = Profile.objects.get(user=user)
        except:
            profile = Profile.objects.create_profile(user)

        if not profile:
            return

        profile.total_spend += instance.total
        profile.save()
