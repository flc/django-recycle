try:
    import urlparse
except ImportError:  # python3
    import urllib.parse as urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import QueryDict


def url_with_domain(path):
    domain = "{protocol}://{domain}".format(
        protocol=getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http"),
        domain=Site.objects.get_current().domain,
    )
    return urlparse.urljoin(domain, path)


def reverse_with_domain(*args, **kwargs):
    path = reverse(*args, **kwargs)
    return url_with_domain(path)


def reverse_build_url(*args, **kwargs):
    params = kwargs.pop('params', {})
    url = reverse(*args, **kwargs)
    if not params:
        return url

    qdict = QueryDict('', mutable=True)
    for k, v in params.iteritems():
        if type(v) is list:
            qdict.setlist(k, v)
        else:
            qdict[k] = v

    return url + '?' + qdict.urlencode()
