"""
Copyright (c) 2011 Embed.ly, Inc.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

https://github.com/embedly/embedly-python/

Client
======

The embedly object that interacts with the service
"""

import re
import httplib2
import json
from urllib.parse import quote, urlencode

from collections import UserDict as IterableUserDict


class Url(IterableUserDict, object):
    """
    A dictionary with two additional attributes for the method and url.
    UserDict provides a dictionary interface along with the regular
    dictionary accsesible via the `data` attribute.
    """
    def __init__(self, data=None, method=None, original_url=None, **kwargs):
        super(Url, self).__init__(data, **kwargs)
        self.method = method or 'url'
        self.original_url = original_url

    def __str__(self):
        return '<%s %s>' % (self.method.title(), self.original_url or "")

def get_user_agent():
    __version__ = '0.5.0'
    return 'Mozilla/5.0 (compatible; embedly-python/%s;)' % __version__


class Embedly(object):
    """
    Client

    """
    def __init__(self, key=None, user_agent=None, timeout=60):
        """
        Initialize the Embedly client

        :param key: Embedly Pro key
        :type key: str
        :param user_agent: User Agent passed to Embedly
        :type user_agent: str
        :param timeout: timeout for HTTP connection attempts
        :type timeout: int

        :returns: None
        """
        self.key = key
        self.user_agent = user_agent or get_user_agent()
        self.timeout = timeout

        self.services = []
        self._regex = None

    def get_services(self):
        """
        get_services makes call to services end point of api.embed.ly to fetch
        the list of supported providers and their regexes
        """

        if self.services:
            return self.services

        url = 'https://api.embed.ly/1/services/python'

        http = httplib2.Http(timeout=self.timeout)
        headers = {'User-Agent': self.user_agent,
                   'Connection': 'close'}
        resp, content = http.request(url, headers=headers)

        if resp['status'] == '200':
            resp_data = json.loads(content.decode('utf-8'))
            self.services = resp_data

            # build the regex that we can use later
            _regex = []
            for each in self.services:
                _regex.append('|'.join(each.get('regex', [])))

            self._regex = re.compile('|'.join(_regex))

        return self.services

    def is_supported(self, url):
        """
        ``is_supported`` is a shortcut for client.regex.match(url)
        """
        return self.regex.match(url) is not None

    @property
    def regex(self):
        """
        ``regex`` property just so we can call get_services if the _regex is
        not yet filled.
        """
        if not self._regex:
            self.get_services()

        return self._regex

    def _get(self, version, method, url_or_urls, **kwargs):
        """
        _get makes the actual call to api.embed.ly
        """
        if not url_or_urls:
            raise ValueError('%s requires a url or a list of urls given: %s' %
                             (method.title(), url_or_urls))

        # a flag we can use instead of calling isinstance() all the time
        multi = isinstance(url_or_urls, list)

        # throw an error early for too many URLs
        if multi and len(url_or_urls) > 20:
            raise ValueError('Embedly accepts only 20 urls at a time. Url '
                             'Count:%s' % len(url_or_urls))

        query = ''

        key = kwargs.get('key', self.key)

        # make sure that a key was set on the client or passed in
        if not key:
            raise ValueError('Requires a key. None given: %s' % key)

        kwargs['key'] = key

        query += urlencode(kwargs)

        if multi:
            query += '&urls=%s&' % ','.join([quote(url) for url in url_or_urls])
        else:
            query += '&url=%s' % quote(url_or_urls)

        url = 'https://api.embed.ly/%s/%s?%s' % (version, method, query)

        http = httplib2.Http(timeout=self.timeout)

        headers = {'User-Agent': self.user_agent,
                   'Connection': 'close'}

        resp, content = http.request(url, headers=headers)

        if resp['status'] == '200':
            data = json.loads(content.decode('utf-8'))

            if kwargs.get('raw', False):
                data['raw'] = content
        else:
            data = {'type': 'error',
                    'error': True,
                    'error_code': int(resp['status'])}

        if multi:
            return map(lambda url, data: Url(data, method, url),
                       url_or_urls, data)

        return Url(data, method, url_or_urls)

    def oembed(self, url_or_urls, **kwargs):
        """
        oembed
        """
        return self._get(1, 'oembed', url_or_urls, **kwargs)

    def preview(self, url_or_urls, **kwargs):
        """
        oembed
        """
        return self._get(1, 'preview', url_or_urls, **kwargs)

    def objectify(self, url_or_urls, **kwargs):
        """
        oembed
        """
        return self._get(2, 'objectify', url_or_urls, **kwargs)

    def extract(self, url_or_urls, **kwargs):
        """
        oembed
        """
        return self._get(1, 'extract', url_or_urls, **kwargs)
