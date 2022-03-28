import logging
import time
import re

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import unidecode


logger = logging.getLogger(__name__)


# empty means we log everything
REQUEST_RESPONSE_LOG_PATHS = getattr(settings, "REQUEST_RESPONSE_LOG_PATHS", ())


def get_request_headers(request):
    regex_http_ = re.compile(r'^HTTP_.+$')
    regex_content_type = re.compile(r'^CONTENT_TYPE$')
    regex_content_length = re.compile(r'^CONTENT_LENGTH$')

    headers = {}
    for header in request.META:
        if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
            headers[header] = request.META[header]
    return headers


class LoggingMiddleware(MiddlewareMixin):
    """
    Provides simple logging of requests and responses
    """

    def process_request(self, request):
        request._req_res_log = {
            'body': request.body,
            'start_time': time.time(),
        }

    def process_response(self, request, response):
        """
        Adding request and response logging
        """
        req_res_log = getattr(request, "_req_res_log", None)
        if req_res_log is None:
            return response

        path = request.path
        matched = len(REQUEST_RESPONSE_LOG_PATHS) == 0
        for regex in REQUEST_RESPONSE_LOG_PATHS:
            if re.search(regex, path) is not None:
                matched = True

        if not matched:
            return response

        duration = time.time() - req_res_log['start_time']
        request_headers = "\n".join([f"{k}: {v}" for k, v in list(get_request_headers(request).items())])
        mp = 'multipart' in request.META.get('CONTENT_TYPE', '')
        if mp:
            request_body = 'Multipart data'
        else:
            request_body = req_res_log.get('body', '')

        respone_content = ""
        try:
            response_content = str(getattr(response, "content", "File response"))
        except UnicodeDecodeError:
            try:
                response_content = str(getattr(response, "content", "File response").decode("utf8"))
            except UnicodeDecodeError:
                response_content = ""

        try:
            # request_body = unicode(request_body, "utf8", errors="ignore").encode("ascii", "ignore")
            request_body = str(request_body)
        except UnicodeDecodeError:
            try:
                request_body = request_body.decode("utf8")
            except UnicodeDecodeError:
                try:
                    request_body = unidecode.unidecode(request_body)
                except Exception as e:
                    request_body = 'Unidecode error'

        logger.debug(
            "\n"
            "Request method: %s\n"
            "Request path: %s\n"
            "Request headers:\n%s\n\n"
            "Request GET: %s\n\n"
            "Request body: %s\n\n"
            "Response code: %s %s\n\n"
            "Response content:\n%s\n\n"
            "Response headers:\n%s\n\n"
            "Duration: %s seconds",
            request.method,
            request.path,
            request_headers,
            request.GET,
            request_body,
            response.status_code,
            response.reason_phrase,
            response_content,
            response.serialize_headers(),
            duration,
        )

        return response
