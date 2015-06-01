import logging
import time
import re

from django.conf import settings


logger = logging.getLogger(__name__)


# empty means we log everything
REQUEST_RESPONSE_LOG_PATHS = getattr(
  settings, "REQUEST_RESPONSE_LOG_PATHS", ()
  )


def get_request_headers(request):
    regex_http_          = re.compile(r'^HTTP_.+$')
    regex_content_type   = re.compile(r'^CONTENT_TYPE$')
    regex_content_length = re.compile(r'^CONTENT_LENGTH$')

    headers = {}
    for header in request.META:
      if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
          headers[header] = request.META[header]
    return headers


class LoggingMiddleware(object):
    """
    Provides simple logging of requests and responses
    """

    def process_request(self, request):
        request._initial_http_body = request.body
        request._start_time = time.time()

    def process_response(self, request, response):
        """
        Adding request and response logging
        """
        path = request.path
        matched = len(REQUEST_RESPONSE_LOG_PATHS) == 0
        for regex in REQUEST_RESPONSE_LOG_PATHS:
          if re.search(regex, path) is not None:
            matched = True

        if not matched:
          return response

        duration = time.time() - request._start_time
        request_headers = "\n".join([
            "{}: {}".format(k, v)
            for k, v in get_request_headers(request).items()
            ])
        logger.debug(
          "\n"
          "Request Path:%s\n"
          "Request headers:\n%s\n\n"
          "Request GET: %s\n\n"
          "Request body: %s\n\n"
          "Response code: %s %s\n\n"
          "Response content:\n%s\n\n"
          "Response headers:\n%s\n\n"
          "Duration: %s seconds",
          request.path,
          request_headers,
          request.GET,
          request._initial_http_body,
          response.status_code, response.reason_phrase,
          getattr(response, "content", "File response"),
          response.serialize_headers(),
          duration,
        )
        return response
