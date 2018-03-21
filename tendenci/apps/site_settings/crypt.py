from __future__ import print_function
from builtins import str
import base64
from Crypto.Cipher import AES

from django.conf import settings


def encrypt(value):
    """Return the encrypted value of the setting.
    Uses the character '\0' as padding.
    """
    cipher = AES.new(settings.SITE_SETTINGS_KEY.encode('utf-8'), AES.MODE_ECB)
    value = str(value).encode('utf-8')
    padding = AES.block_size - len(value) % AES.block_size
    for i in range(padding):
        value += b'\0'
    ciphertext = cipher.encrypt(value)
    ciphertext = base64.b64encode(ciphertext) # make it database friendly
    return ciphertext.decode('utf-8')

def decrypt(value):
    """Return the decrypted value of the setting.
    This removes the padding character '\0'
    """
    cipher = AES.new(settings.SITE_SETTINGS_KEY.encode('utf-8'), AES.MODE_ECB)
    value = value.encode('utf-8')
    value = base64.b64decode(value)
    value = cipher.decrypt(value)
    return value.replace(b'\0', b'').decode('utf-8')

def test():
    """Check if original values and decrypted values
    will still be equal to each other.
    """
    from tendenci.apps.site_settings.models import Setting
    s = Setting.objects.all()
    for x in s:
        code = encrypt(x.value)
        decode = decrypt(code)
        if x.value != decode:
            print("not equal!")
