import operator

from django.db import connection
from django.template.defaultfilters import filesizeformat


def get_db_table_sizes(top_n=None, order_by=1, pretty=True):
    """Calculate postgreSQL table size.

    :param top_n:
        return only the top n sizes
    :param order_by:
        1 - order by sizes with indexes
        2 - order by sizes without indexes
    :param pretty:
        pretty format the sizes if True
    :return:
        list of
            (db table name, size with indexes, size without indexes)
        3-tuples
    """
    assert order_by in (1, 2)

    with_indexes_select = "pg_total_relation_size(%s)"
    without_indexes_select = "pg_relation_size(%s)"

    tables = connection.introspection.table_names()
    cursor = connection.cursor()

    sizes = []
    for table in tables:
        cursor.execute(f"SELECT {with_indexes_select}, {without_indexes_select}", [table, table])
        row = cursor.fetchone()
        sizes.append((table, row[0], row[1]))

    sorted_sizes = sorted(sizes, key=operator.itemgetter(order_by), reverse=True)

    if pretty:
        sorted_sizes = [
            (table, filesizeformat(size1).replace("\xa0", " "), filesizeformat(size2).replace("\xa0", " "))
            for table, size1, size2 in sorted_sizes
        ]

    if top_n is not None:
        sorted_sizes = sorted_sizes[:top_n]

    return sorted_sizes
