from django.db import connection


def explain_query(qs, analyze=False):
    query_str = str(qs.query)
    cursor = connection.cursor()
    an = " ANALYZE" if analyze else ""
    comm = "".join(["EXPLAIN", an])
    cursor.execute(f"{comm} {query_str}")
    return "\n".join([i[0] for i in cursor.fetchall()])
