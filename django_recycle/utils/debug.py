import logging
import pprint
import re

from functools import wraps

from django.conf import settings
from django.db import connection
from django.db import reset_queries

from .compat import available_attrs


logger = logging.getLogger(__name__)


def log_queries(view_func):
    def log(msg, *args):
        logger.debug(msg, *args)

    def wrapped_view(request, *args, **kwargs):
        if not settings.DEBUG:
            return view_func(request, *args, **kwargs)

        old_queries = connection.queries
        reset_queries()

        response = view_func(request, *args, **kwargs)
        log('Queries: %s', pprint.pformat(connection.queries))
        log('Queries len: %s', len(connection.queries))
        log('Queries total time: %s', sum(float(q['time']) for q in connection.queries))

        # restore
        connection.queries.extend(old_queries)
        return response

    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)


def shorten_sql_in_query(sql_str):
    return re.sub(r"IN\s+\([ 0-9,]+\)", "IN (...)", sql_str)
