import os
import urllib.parse

from django.conf import settings
from django.contrib.staticfiles import finders

import weasyprint


def static_file_url_fetcher(url):
    file_path = None
    static_prefix = 'static://'
    static_private_prefix = 'private://'
    media_prefix = 'media://'
    if url.startswith(static_prefix):
        path = url.split(static_prefix)[1]
        file_path = finders.find(path)
    elif url.startswith(static_private_prefix):
        if getattr(settings, "STATICFILES_PRIVATE_DIR", None) is not None:
            path = url.split(static_private_prefix)[1]
            file_path = os.path.join(settings.STATICFILES_PRIVATE_DIR, path)
    elif url.startswith(media_prefix):
        path = url.split(media_prefix)[1]
        file_path = os.path.join(settings.MEDIA_ROOT, path)
    elif urllib.parse.urlparse(url).path.startswith(settings.STATIC_URL):
        path = url.split(settings.STATIC_URL)[1]
        file_path = os.path.join(settings.STATIC_ROOT, path)

    if file_path is not None:
        try:
            with open(file_path) as f:
                contents = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'rb') as f:
                contents = f.read()
        return dict(string=contents)

    return weasyprint.default_url_fetcher(url)
