import logging

from rest_framework.response import Response
from rest_framework import generics

from ...utils.ip import get_ip_of_request


class ClientSideExceptionLoggerView(generics.GenericAPIView):
    throttle_scope = 'client_side_exceptions'
    log_level = "info"
    ip_resolver_func = None

    def post(self, request, format=None):
        logger = logging.getLogger("client_side_exceptions")
        ip = get_ip_of_request(self.request, ip_resolver=self.ip_resolver_func)
        user_agent = request.headers.get('User-Agent', '')
        url = request.DATA.get("url")
        message = request.DATA.get("message")
        cause = request.DATA.get("cause")
        type = request.DATA.get("type")
        stacktrace = request.DATA.get("stackTrace")
        if isinstance(stacktrace, list):
            stacktrace = "\n".join(stacktrace)
        text = (
            "\nuser: %s\n"
            "ip: %s\n"
            "user agent: %s\n"
            "url: %s\n"
            "message: %s\n"
            "cause: %s\n"
            "type: %s\n"
            "stacktrace:\n"
            "%s\n"
            )
        getattr(logger, self.log_level)(text, request.user, ip, user_agent, url, message, cause, type, stacktrace)
        return Response()
