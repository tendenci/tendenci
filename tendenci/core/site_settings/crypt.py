import base64
from Crypto.Cipher import AES

from django.conf import settings


def encrypt(value):
    """Return the encrypted value of the setting.
    Uses the character '\0' as padding.
    """
    cipher = AES.new(settings.SITE_SETTINGS_KEY, AES.MODE_ECB)
    value = unicode(value).encode('utf-8')
    padding = cipher.block_size - len(value) % cipher.block_size
    for i in xrange(padding):
        value += '\0'
    ciphertext = cipher.encrypt(value)
    ciphertext = base64.b64encode(ciphertext) # make it database friendly
    return ciphertext

def decrypt(value):
    """Return the decrypted value of the setting.
    This removes the padding character '\0'
    """
    cipher = AES.new(settings.SITE_SETTINGS_KEY, AES.MODE_ECB)
    value = base64.b64decode(value)
    value = cipher.decrypt(value)
    return value.replace('\0', '')

def test():
    """Check if original values and decrypted values
    will still be equal to each other.
    """
    from tendenci.core.site_settings.models import Setting
    s = Setting.objects.all()
    for x in s:
        code = encrypt(x.value)
        decode = decrypt(code)
        if x.value != decode:
            print "not equal!"
