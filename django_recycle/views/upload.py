import json

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseServerError
from django.template.defaultfilters import filesizeformat

from recycle.utils import seconds_to_str


def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''

    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    elif 'X-Progress-Id' in request.GET:
        # stupid Safari
        progress_id = request.GET['X-Progress-Id']
    elif 'X-Progress-Id' in request.META:
        # stupid Safari
        progress_id = request.META['X-Progress-Id']

    if progress_id:
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)

        if data:
            for attr in ('size', 'received', 'speed'):
                if attr in data:
                    data[attr + '_pretty'] = filesizeformat(data[attr])
            for attr in ('remaining_time',):
                if attr in data:
                    data[attr + '_pretty'] = seconds_to_str(data[attr])
            if 'received' in data and 'size' in data:
                data['progress'] = float(data['received']) / float(data['size'])

            # # simulate nginx response
            # data = {
            #     'received': data['received'],
            #     'size': data['size'],
            #     'state': 'uploading'
            # }
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseServerError("Server Error: You must provide X-Progress-ID header or query param.")
