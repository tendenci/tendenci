import os
import csv

from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage

from tendenci.apps.base.utils import normalize_newline

def geocode_api(**kwargs):
    import simplejson, urllib
    GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
    kwargs['sensor'] = kwargs.get('sensor', 'false')
    url = '%s?%s' % (GEOCODE_BASE_URL, urllib.urlencode(kwargs))
    return simplejson.load(urllib.urlopen(url))

def get_coordinates(address):
    """
    Get the latitude and longitude for the address parameter.
    Return a 2-tuple with latitude and longitude.
    Else return a 2-tuple with None Type objects.
    """
    result = geocode_api(address=address)

    if result['status'] == 'OK':
        return result['results'][0]['geometry']['location'].values()

    return (None, None)

def distance_api(*args, **kwargs):
    import simplejson, urllib

    output = kwargs.get('output', 'json')
    distance_base_url = 'http://maps.googleapis.com/maps/api/distancematrix/%s' & ouput

    kwargs.update({
        'origins':kwargs.get('origins',''),
        'destinations': kwargs.get('destinations',''),
        'sensor': kwargs.get('sensor', 'false')
    })

    url = '%s?%s' % (distance_base_url, urllib.urlencode(kwargs))
    return simplejson.load(urllib.urlopen(url))

def distance_via_sphere(lat1, long1, lat2, long2):
    """
    http://www.johndcook.com/python_longitude_latitude.html
    Distance in miles multiply by 3960
    Distance in kilometers multiply by 6373
    """
    import math

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc * 3960

def csv_to_dict(file_path, **kwargs):
    """
    Returns a list of dicts. Each dict represents record.
    """
    machine_name = kwargs.get('machine_name', False)

    # null byte; assume xls; not csv
    if has_null_byte(file_path):
        return []

    normalize_newline(file_path)
    csv_file = csv.reader(default_storage.open(file_path, 'rU'))
    colnames = next(csv_file)  # row 1;

    if machine_name:
        colnames = [slugify(c).replace('-', '') for c in colnames]

    cols = xrange(len(colnames))
    lst = []

    # make sure colnames are unique
    duplicates = {}
    for i in cols:
        for j in cols:
            # compare with previous and next fields
            if i != j and colnames[i] == colnames[j]:
                number = duplicates.get(colnames[i], 0) + 1
                duplicates[colnames[i]] = number
                colnames[j] = colnames[j] + "-" + str(number)

    for row in csv_file:
        entry = {}
        rows = len(row) - 1
        for col in cols:
            if col > rows:
                break  # go to next row
            entry[colnames[col]] = row[col]
        lst.append(entry)

    return lst  # list of dictionaries

def has_null_byte(file_path):
    f = default_storage.open(file_path, 'r')
    data = f.read()
    f.close()
    return ('\0' in data)