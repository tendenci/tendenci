from celery.task import Task
from user_groups.importer.utils import parse_subs_from_csv

class ImportSubscribersTask(Task):

    def run(self, group, file_path, **kwargs):
        #get parsed membership dicts
        
        subs = parse_subs_from_csv(group, file_path)
        
        return subs

