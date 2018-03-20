import os

from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage

from tendenci.apps.locations.utils import csv_to_dict, has_null_byte


def is_import_valid(file_path):
    """
    Returns a 2-tuple containing a booelean and list of errors

    The import file must be of type .csv and and include
    a location name column.

    """

    errs = []
    ext = os.path.splitext(file_path)[1]

    if ext != '.csv':
        errs.append("Please make sure you're importing a .csv file.")
        return False, errs

    if has_null_byte(file_path):
        errs.append('This .csv file has null characters, try re-saving it.')
        return False, errs

    # get header column
    f = default_storage.open(file_path, 'r')
    row = f.readline()
    f.close()

    headers = [slugify(r).replace('-','') for r in row.split(',')]

    required = ('locationname',)
    requirements_met = [r in headers for r in required]

    if all(requirements_met):
        return True, []
    else:
        return False, ['Please make sure there is a location name column.']


def clean_field_name(name):
    name = name.lower()
    name = name.replace('-', '_')
    name = name.replace(' ', '_')
    return name


def parse_locs_from_csv(file_path, mapping, parse_range=None):
    """
    Parse location entries from a csv file.
    An extra field called mapping can be passed in for field mapping
    parse_range is the range of rows to be parsed from the csv.
    """

    location_dicts = []
    skipped = 0

    for csv_dict in csv_to_dict(file_path, machine_name=True):  # field mapping
        m = {}
        for app_field, csv_field in mapping.items():
            if csv_field:  # skip blank option
                m[clean_field_name(app_field)] = csv_dict.get(csv_field, '')

        # Check if row should be skipped here
        m['skipped'] = False

        m['hq'] = m.get('headquarters','').lower() == 'true'

        location_dicts.append(m)

    total = len(location_dicts)
    stats = {
        'all': total,
        'skipped': skipped,
        'added': total-skipped,
    }
    return location_dicts, stats
