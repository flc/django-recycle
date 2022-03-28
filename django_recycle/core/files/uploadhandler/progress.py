# based on http://djangosnippets.org/snippets/678/ but slightly modified

import logging
from itertools import count

from time import time
from math import floor

from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache


logger = logging.getLogger(__name__)


class UploadProgressCachedHandler(FileUploadHandler):
    """Tracks progress for file uploads.
    The http post request must contain a header or query parameter,
    'X-Progress-ID' which should contain a unique string to identify the
    upload to be tracked.
    """

    def __init__(self, request=None):
        super().__init__(request)

        self.progress_id = None
        self.cache_key = None
        self.activated = False
        self.chunk_count = count(1)

    def handle_raw_input(self,
                         input_data, META, content_length,
                         boundary, encoding=None):
        if content_length > self.chunk_size:
            self.activated = True
        else:
            return

        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        elif 'X-Progress-ID' in self.request.META:
            self.progress_id = self.request.META['X-Progress-ID']

        if self.progress_id:
            self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'],
                                        self.progress_id)
            data = {
                'size': content_length,
                'received': 0,
                'speed': 0,
                'remaining_time': 0,
                'prev_timestamp': time(),
                'curr_timestamp': time()
            }
            cache.set(self.cache_key, data)
            logger.debug("Initialized cache key %s with %s.",
                         self.cache_key, data)
        else:
            logger.debug("No progress id provided.")

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        if self.activated and self.cache_key:
            data = cache.get(self.cache_key)
            # update received data size
            # len(raw_data) == self.chunk_size
            data['received'] += self.chunk_size
            # update timestamps
            data['prev_timestamp'] = data['curr_timestamp']
            data['curr_timestamp'] = time()
            # calculate upload speed
            data['speed'] = floor(self.chunk_size / (data['curr_timestamp'] - data['prev_timestamp']))
            # calculate remaining time
            data['remaining_time'] = floor((data['size'] - data['received']) / data['speed'])

            cache.set(self.cache_key, data)

            if not (next(self.chunk_count) % 100):
                logger.debug("Updated cache key %s with %s.",
                             self.cache_key, data)

        return raw_data

    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        if self.activated and self.cache_key:
            logger.debug('Upload complete for cache key %s.',
                         self.cache_key)
            cache.delete(self.cache_key)
