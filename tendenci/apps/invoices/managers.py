from haystack.query import SearchQuerySet

from django.db.models import Manager

class InvoiceManager(Manager):
    def create_invoice(self, user, **kwargs):
        return self.create(title=kwargs.get('title', ''),
                           estimate=('estimate' == kwargs.get('status_detail', 'estimate')),
                           status=kwargs.get('status', True),
                           status_detail=kwargs.get('status_detail', 'estimate'),
                           object_type=kwargs.get('object_type', None),
                           object_id=kwargs.get('object_id', 0),
                           subtotal=kwargs.get('subtotal', 0),
                           total=kwargs.get('total', 0),
                           balance=kwargs.get('balance', 0),
                           creator=user,
                           creator_username=user.username,
                           owner=user,
                           owner_username=user.username)

    def search(self, query=None, *args, **kwargs):
        """
            invoice haystack to query invoices.
            Returns a SearchQuerySet
        """
        from tendenci.apps.invoices.models import Invoice
        sqs = SearchQuerySet()

        if query:
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()

        return sqs.models(Invoice)

    def first(self, **kwargs):
        """
        Returns first instance that matches filters.
        If no instance is found then a none type object is returned.
        """
        [instance] = self.filter(**kwargs).order_by('pk')[:1] or [None]
        return instance

    def get_queryset(self):
        """
        Exclude void invoices by default
        """
        return super(InvoiceManager, self).get_queryset().filter(is_void=False)

    def all_invoices(self):
      """
      Returns ALL invoice records
      """
      return super(InvoiceManager, self).get_queryset()

    def void(self):
      """
      Returns ALL invoice records
      """
      return super(InvoiceManager, self).get_queryset().filter(is_void=True)
