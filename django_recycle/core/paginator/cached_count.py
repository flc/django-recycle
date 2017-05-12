# based on https://gist.github.com/e4c5/6852723
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import connection
from django.conf import settings


CACHED_COUNT_PAGINATOR_TIMEOUT = getattr(
    settings, "CACHED_COUNT_PAGINATOR_TIMEOUT", 3600
    )


class CachedCountPaginator(Paginator):
    """
    A custom paginator that helps to cut down on the number of
    SELECT COUNT(*) form table_name queries. These are really slow, therefore
    once we execute the query, we will cache the result which means the page
    numbers are not going to be very accurate but we don't care
    """

    def _get_count(self):
        """
        Returns the total number of objects, across all pages.
        """
        if getattr(self, '_count', None) is None:
            try:
                key = "cachedcountpaginator:{0}".format(
                    hash(self.object_list.query.__str__())
                    )
                self._count = cache.get(key, -1)
                if self._count == -1:
                    if not self.object_list.query.where:
                        if connection.vendor == "postgresql":
                            # This query that avoids a count(*) alltogether is
                            # stolen from https://djangosnippets.org/snippets/2593/
                            cursor = connection.cursor()
                            cursor.execute(
                                "SELECT reltuples FROM pg_class WHERE relname = %s",
                                [self.object_list.query.model._meta.db_table]
                                )
                            self._count = int(cursor.fetchone()[0])

                    if self._count == -1:
                        self._count = self.object_list.count()

                    cache.set(key, self._count, CACHED_COUNT_PAGINATOR_TIMEOUT)
            except (AttributeError, TypeError) as e:
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)
