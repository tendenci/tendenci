from django.contrib.auth.models import User
from tastypie.validation import CleanedDataFormValidation

class TendenciValidation(CleanedDataFormValidation):
    """Validation that makes use of a given Form.
    The Form is assumed to be a ModelForm of a TendenciBaseModel subclass
    """

    def is_valid(self, bundle, request=None):
        """Validate the bundle with the given form.
        Creator and Owner fields and defaulted to be the user of
        the apikey if they were not specified.
        """

        data = bundle.data
        # Ensure we get a bound Form, regardless of the state of the bundle.
        if data is None:
            data = {}

        if request:
            user = User.objects.get(username=request.GET.get('username'))
            if not data.get('creator', None):
                data['creator'] = user.pk
                data['creator_username'] = user.username
            if not data.get('owner', None):
                data['owner'] = user.pk
                data['owner_username'] = user.username

        form = self.form_class(data, instance=bundle.obj, request=request)

        if form.is_valid():
            # We're different here & relying on having a reference to the same
            # bundle the rest of the process is using.
            bundle.data = form.cleaned_data
            return {}

        # The data is invalid. Let's collect all the error messages & return
        # them.
        return form.errors
