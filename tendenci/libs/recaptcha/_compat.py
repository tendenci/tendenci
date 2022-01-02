import sys

from urllib.request import build_opener, ProxyHandler, Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
text_type = str
