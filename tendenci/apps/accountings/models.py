from django.db import models
from django.contrib.auth.models import User
from tendenci.apps.accountings.managers import (AcctEntryManager,
                                                AcctTranManager)


class Acct(models.Model):
    account_number = models.IntegerField(unique=True)
    description = models.TextField()
    type = models.CharField(max_length=5)

    class Meta:
        app_label = 'accountings'


class AcctEntry(models.Model):
    source = models.TextField()
    object_id = models.IntegerField()
    entry_dt = models.DateTimeField(auto_now_add=True)
    exported = models.BooleanField(default=False)
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="accentry_creator",
                                 null=True,
                                 on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=150, default='')
    owner = models.ForeignKey(User, related_name="accentry_owner",
                              null=True,
                              on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=150, default='')
    status = models.BooleanField(default=True)

    objects = AcctEntryManager()

    class Meta:
        app_label = 'accountings'


class AcctTran(models.Model):
    acct_entry = models.ForeignKey(AcctEntry,
                                   related_name="trans",
                                   on_delete=models.CASCADE)
    #account_number = models.IntegerField()
    account = models.ForeignKey(Acct, related_name="accts", null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    cleared = models.BooleanField(default=False)
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="accttran_creator",
                                null=True,
                                on_delete=models.SET_NULL)
    owner = models.ForeignKey(User, related_name="accttran_owner",
                              null=True,
                              on_delete=models.SET_NULL)
    status = models.BooleanField(default=True)

    objects = AcctTranManager()

    class Meta:
        app_label = 'accountings'

    @property
    def debit(self):
        if self.amount > 0:
            return self.amount
        return 0

    @property
    def credit(self):
        if self.amount < 0:
            return abs(self.amount)
        return 0
