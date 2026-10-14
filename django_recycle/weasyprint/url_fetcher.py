import mimetypes
import os
import urllib.parse

from django.conf import settings
from django.contrib.staticfiles import finders

import weasyprint

try:
    # WeasyPrint 68+: a url_fetcher is a URLFetcher, and 70 accepts nothing else
    from weasyprint.urls import URLFetcher, URLFetcherResponse
except ImportError:  # WeasyPrint < 68: a function returning a dict
    URLFetcher = URLFetcherResponse = None


STATIC_PREFIX = "static://"
STATIC_PRIVATE_PREFIX = "private://"
MEDIA_PREFIX = "media://"


def _resolve_within(root, path, url):
    """Join `path` onto `root`, refusing anything that resolves outside it.

    A bare `os.path.join(root, path)` lets `../` (or an absolute path) walk out of the root, so
    a document could name any file the process can read and have its contents embedded in the PDF.
    """
    root = os.path.realpath(root)
    file_path = os.path.realpath(os.path.join(root, path))
    if file_path != root and not file_path.startswith(root + os.sep):
        raise ValueError(f"URL resolves outside its root directory: {url!r}")
    return file_path


def _local_file_path(url):
    """The local file `url` names, or None if it names none of them."""
    if url.startswith(STATIC_PREFIX):
        # No containment check needed: finders.find() raises SuspiciousFileOperation for a
        # traversing or absolute path.
        return finders.find(url[len(STATIC_PREFIX) :])
    if url.startswith(STATIC_PRIVATE_PREFIX):
        root = getattr(settings, "STATICFILES_PRIVATE_DIR", None)
        if root is None:
            return None
        return _resolve_within(root, url[len(STATIC_PRIVATE_PREFIX) :], url)
    if url.startswith(MEDIA_PREFIX):
        return _resolve_within(settings.MEDIA_ROOT, url[len(MEDIA_PREFIX) :], url)
    if urllib.parse.urlparse(url).path.startswith(settings.STATIC_URL):
        path = url.split(settings.STATIC_URL)[1]
        return _resolve_within(settings.STATIC_ROOT, path, url)
    return None


def _refused(url):
    return ValueError(f"Refused to fetch a URL that is not a local static file: {url!r}")


if URLFetcher is not None:

    class StaticFileURLFetcher(URLFetcher):
        """A WeasyPrint URL fetcher that serves local static and media files.

        `static://`, `private://`, `media://` and paths under `STATIC_URL` are resolved to
        local files, and a path that escapes its root directory is refused.

        Every other URL (notably `file://` and `http(s)://`) is refused, so that a document (or
        a value interpolated into one) cannot make WeasyPrint read an arbitrary local file, or
        reach an internal network service, and embed the result in the PDF. Pass
        `allow_external=True` to fetch such URLs as WeasyPrint's own fetcher does instead.
        """

        def __init__(self, allow_external=False, **kwargs):
            super().__init__(**kwargs)
            self.allow_external = allow_external

        def fetch(self, url, headers=None):
            file_path = _local_file_path(url)
            if file_path is not None:
                with open(file_path, "rb") as f:
                    body = f.read()
                content_type = mimetypes.guess_type(file_path)[0]
                return URLFetcherResponse(
                    url, body, headers={"Content-Type": content_type} if content_type else None
                )
            if not self.allow_external:
                raise _refused(url)
            return super().fetch(url, headers)


def make_static_file_url_fetcher(allow_external=False):
    """Build a `url_fetcher` for WeasyPrint that serves local static and media files: a
    StaticFileURLFetcher, or the same rules as a function before WeasyPrint 68."""
    if URLFetcher is not None:
        return StaticFileURLFetcher(allow_external=allow_external)

    def static_file_url_fetcher(url):
        file_path = _local_file_path(url)
        if file_path is not None:
            try:
                with open(file_path) as f:
                    contents = f.read()
            except UnicodeDecodeError:
                with open(file_path, "rb") as f:
                    contents = f.read()
            return {"string": contents}
        if not allow_external:
            raise _refused(url)
        return weasyprint.default_url_fetcher(url)

    return static_file_url_fetcher


static_file_url_fetcher = make_static_file_url_fetcher()
