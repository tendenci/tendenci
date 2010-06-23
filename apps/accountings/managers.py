from django.db.models import Manager
  
class AcctEntryManager(Manager):
    def create_acct_entry(self, user, source, object_id,  **kwargs):
        return self.create(source = source,
                        object_id = object_id,
                        creator = user,
                        creator_username= user.username,
                        owner = user,
                        owner_username = user.username, 
                        status = 1)
        
class AcctTranManager(Manager):
    def create_acct_tran(self, user, acct_entry, acct, amount, **kwargs):
        return self.create(acct_entry = acct_entry,
                           account = acct,
                           amount = amount,
                           creator = user,
                           owner = user,
                           status = 1)