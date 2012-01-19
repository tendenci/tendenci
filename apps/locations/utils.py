

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