import logging
import time
import re


logger = logging.getLogger(__name__)


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
    _initial_http_body = None

    def process_request(self, request):
        # this is required since for some reason there is no way
        # to access request.body in the 'process_response' method.
        self._initial_http_body = request.body
        self._start_time = time.time()
        self._request_headers = get_request_headers(request)

    def process_response(self, request, response):
        """
        Adding request and response logging
        """
        duration = time.time() - self._start_time
        request_headers = "\n".join([
            "{}: {}".format(k, v)
            for k, v in self._request_headers.items()
            ])
        logger.debug(
          "\n"
          "Request headers:\n%s\n\n"
          "GET: %s\n\n"
          "body: %s\n\n"
          "response code: %s %s\n\n"
          "response content:\n%s\n\n"
          "Response headers:\n%s\n\n"
          "duration: %s seconds",
          request_headers,
          request.GET,
          self._initial_http_body,
          response.status_code, response.reason_phrase,
          response.content,
          response.serialize_headers(),
          duration,
        )
        return response
