from api.models import APIAccessKey

def validate_api_request(data):
    """Validate if this is a valid api request.
    """
    access_id = data.get('access_id', '')
    time_stamp = data.get('time_stamp', '')
    h_sequence = data.get('h_sequence')

    try:
        api_access_key = APIAccessKey.objects.get(access_id=access_id)
    except APIAccessKey.DoesNotExist:
        return False
    secret_key = api_access_key.secret_key
    my_h_sequence = get_h_sequence(access_id, time_stamp, secret_key)

    return h_sequence == my_h_sequence


def get_h_sequence(access_id, time_stamp, secret_key):
    import hmac

    msg = '&'.join([str(access_id),
           str(time_stamp)
           ])+'&'

    return hmac.new(str(secret_key), str(msg)).hexdigest()
