from django.db.models import Manager


class AcctEntryManager(Manager):
    def create_acct_entry(self, user, source, object_id, **kwargs):
        d = {'source': source,
             'object_id': object_id,
             'status': 1}

        if not user.is_anonymous:
            d['creator'] = user
            d['creator_username'] = user.username
            d['owner'] = user
            d['owner_username'] = user.username

        return self.create(**d)


class AcctTranManager(Manager):
    def create_acct_tran(self, user, acct_entry, acct, amount, **kwargs):
        d = {'acct_entry': acct_entry,
             'account': acct,
             'amount': amount,
             'status': 1}

        if not user.is_anonymous:
            d['creator'] = user
            d['owner'] = user

        return self.create(**d)
