from __future__ import absolute_import
from .utils import gen_xml

def test_run():
    f = open('test_result.txt', 'w+')
    f.write(gen_xml().content)
    f.close()
