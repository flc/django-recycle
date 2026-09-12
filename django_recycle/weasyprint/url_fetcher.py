import os
import urllib.parse

from django.conf import settings
from django.contrib.staticfiles import finders

import weasyprint


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


def make_static_file_url_fetcher(allow_external=False):
    """Build a `url_fetcher` for WeasyPrint that serves local static and media files.

    `static://`, `private://`, `media://` and paths under `STATIC_URL` are resolved to local files,
    and a path that escapes its root directory is refused.

    Every other URL (notably `file://` and `http(s)://`) is refused, so that a document (or a
    value interpolated into one) cannot make WeasyPrint read an arbitrary local file, or reach an
    internal network service, and embed the result in the PDF. Pass `allow_external=True` to hand
    such URLs to WeasyPrint's default fetcher instead.
    """

    def static_file_url_fetcher(url):
        file_path = None
        if url.startswith(STATIC_PREFIX):
            # No containment check needed: finders.find() raises SuspiciousFileOperation for a
            # traversing or absolute path.
            file_path = finders.find(url[len(STATIC_PREFIX) :])
        elif url.startswith(STATIC_PRIVATE_PREFIX):
            root = getattr(settings, "STATICFILES_PRIVATE_DIR", None)
            if root is not None:
                file_path = _resolve_within(
                    root, url[len(STATIC_PRIVATE_PREFIX) :], url
                )
        elif url.startswith(MEDIA_PREFIX):
            file_path = _resolve_within(
                settings.MEDIA_ROOT, url[len(MEDIA_PREFIX) :], url
            )
        elif urllib.parse.urlparse(url).path.startswith(settings.STATIC_URL):
            path = url.split(settings.STATIC_URL)[1]
            file_path = _resolve_within(settings.STATIC_ROOT, path, url)

        if file_path is not None:
            try:
                with open(file_path) as f:
                    contents = f.read()
            except UnicodeDecodeError:
                with open(file_path, "rb") as f:
                    contents = f.read()
            return {"string": contents}

        if not allow_external:
            raise ValueError(
                f"Refused to fetch a URL that is not a local static file: {url!r}"
            )

        return weasyprint.default_url_fetcher(url)

    return static_file_url_fetcher


static_file_url_fetcher = make_static_file_url_fetcher()
