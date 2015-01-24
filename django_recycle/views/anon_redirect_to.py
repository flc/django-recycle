import urlparse

from django.http import HttpResponseBadRequest, HttpResponse
from django.utils.html import format_html


def anon_redirect_to(request):
    if not request.user.is_authenticated():
        return HttpResponseBadRequest()

    url = request.GET.get("url")
    if not url:
        return HttpResponseBadRequest()

    parsed_url = urlparse.urlparse(url)
    scheme = parsed_url.scheme or "http"
    if not url.startswith(scheme):
        url = "://".join([scheme, url])

    return HttpResponse(format_html(
        "<script>window.location.replace('{}');</script>", url
        ))
