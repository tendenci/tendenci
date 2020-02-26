
from builtins import str
import base64
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

from django.conf import settings


def aes_key_from_conf_key(string):
    # AES.new(key) requires "key" to be provided as a 32 byte long bytestring,
    # which it uses directly as a 256 bit key.
    # Since the configured key is stored in a Django settings file, the stored
    # key must be limited to printable characters.  However, using a key that
    # contains only printable characters and is still only 32 characters long
    # would significantly reduce the key's strength, since the use of printable
    # characters guarantees that a majority of possible keys will never be used.
    # To enable a sufficiently strong key to be configured using only printable
    # characters, the configured key should contain at least 40 printable
    # characters, or 43 alphanumeric characters, or 64 hex characters, and
    # should be converted to a 32 byte AES key using a hash.
    return SHA256.new(string).digest()

def aes_key_for_site_settings():
    # Tendenci < 8 used a 32 byte SITE_SETTINGS_KEY directly.  To avoid forcing
    # users to reconfigure all settings when upgrading to Tendenci 8, continue
    # to use SITE_SETTINGS_KEY directly if it is 32 bytes long.
    if len(settings.SITE_SETTINGS_KEY) == 32:
        return settings.SITE_SETTINGS_KEY.encode()
    return aes_key_from_conf_key(settings.SITE_SETTINGS_KEY.encode())

SITE_SETTINGS_AES_KEY = aes_key_for_site_settings()

def encrypt(value):
    """Return the encrypted value of the setting.
    Uses the character '\0' as padding.
    """
    cipher = AES.new(SITE_SETTINGS_AES_KEY, AES.MODE_ECB)
    value = str(value).encode()
    padding = AES.block_size - len(value) % AES.block_size
    for i in range(padding):
        value += b'\0'
    ciphertext = cipher.encrypt(value)
    ciphertext = base64.b64encode(ciphertext) # make it database friendly
    return ciphertext.decode()

def decrypt(value):
    """Return the decrypted value of the setting.
    This removes the padding character '\0'
    """
    cipher = AES.new(SITE_SETTINGS_AES_KEY, AES.MODE_ECB)
    value = value.encode()
    value = base64.b64decode(value)
    value = cipher.decrypt(value)
    return value.replace(b'\0', b'').decode()

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
