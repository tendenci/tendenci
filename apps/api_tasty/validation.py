from tastypie.validation import CleanedDataFormValidation

class ModelFormValidation(CleanedDataFormValidation):
    """
    A validation class that uses a Django ``Form`` to validate the data.

    This class **ALTERS** data sent by the user!!!

    This class requires a ``form_class`` argument, which should be a Django
    ``Form`` (or ``ModelForm``, though ``save`` will never be called) class.
    This form will be used to validate the data in ``bundle.data``.
    """
    def is_valid(self, bundle, request=None):
        """
        Checks ``bundle.data``to ensure it is valid & replaces it with the
        cleaned results.

        If the form is valid, an empty list (all valid) will be returned. If
        not, a list of errors will be returned.
        """
        data = bundle.data
        # Ensure we get a bound Form, regardless of the state of the bundle.
        if data is None:
            data = {}

        form = self.form_class(data, instance=bundle.obj, request=request)

        if form.is_valid():
            # We're different here & relying on having a reference to the same
            # bundle the rest of the process is using.
            bundle.data = form.cleaned_data
            return {}

        # The data is invalid. Let's collect all the error messages & return
        # them.
        return form.errors
