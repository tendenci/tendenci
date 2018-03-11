from builtins import str
from celery.task import Task

from tendenci.apps.locations.models import Location
from tendenci.apps.locations.importer.utils import parse_locs_from_csv


class ImportLocationsTask(Task):

    def run(self, user, file_path, fields, **kwargs):

        location_fields = [f.name for f in Location._meta.fields]

        #get parsed membership dicts
        imported = []
        locs, stats = parse_locs_from_csv(file_path, fields)

        for m in locs:
            if not m['skipped']:
                # Create Location object
                obj_dict = {}
                for key in m:
                    if key in location_fields:
                        if isinstance(m[key], str):
                            m[key] = m[key].strip()
                        obj_dict[key] = m[key]

                # Add other fields
                obj_dict['location_name'] = m['locationname']
                obj_dict['creator'] = user
                obj_dict['creator_username'] = user.username
                obj_dict['owner'] = user
                obj_dict['owner_username'] = user.username

                # Import Locations as publicly viewable
                obj_dict['allow_anonymous_view'] = True
                obj_dict['allow_user_view'] = False
                obj_dict['allow_member_view'] = False
                obj_dict['allow_user_edit'] = False
                obj_dict['allow_member_edit'] = False

                new_location = Location.objects.create(**obj_dict)

                # append to imported list
                imported.append(new_location)

        return imported, stats
