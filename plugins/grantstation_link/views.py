import hashlib
from datetime import datetime, timedelta

from django.conf import settings
from django.http import Http404, HttpResponseRedirect

from base.http import Http403
from perms.utils import is_member, is_admin

grantstation_id = getattr(settings, 'GRANTSTATION_ID', None)

def grantstation_redirect(request, offset='-3'):
    if grantstation_id:
        if is_member(request.user) or is_admin(request.user):
            hashdt = ''
            if offset and int(offset):
                timestamp = datetime.now() + timedelta(hours=int(offset))
                hashdt = hashlib.md5(timestamp.strftime("%Y;%m;%d;%H;%M").replace(';0',';')).hexdigest()
            redirect_url = "http://www.grantstation.com/Licensing?ID=%s;%s" % (grantstation_id,hashdt)
            return HttpResponseRedirect(redirect_url)
        else:
            raise Http403
    else:
        raise Http404
