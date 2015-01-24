import gc


def large_qs_pk_iterator(queryset, size=10000):
    """Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 10000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support
    ordered query sets.
    """
    queryset = queryset.order_by("pk")
    pk = 0
    while True:
        yielded = False
        for row in queryset.filter(pk__gt=pk)[:size].iterator():
            # keep this before yield because the row (if it is a model object)
            # may gets deleted
            pk = row.pk
            yielded = True
            yield row
        gc.collect()
        if not yielded:
            break


def large_vlqs_pk_iterator(queryset, size=50000):
    """Use for iterating over large ValuesListQuerySet's.
    Note that the implementation of the iterator does not support
    ordered query sets."""
    pk_inserted = False
    original_flat = queryset.flat
    if queryset.field_names[0] not in ("id", "pk"):
        values = queryset.field_names[:]
        values.insert(0, "pk")
        queryset = queryset.values_list(*values)
        pk_inserted = True

    queryset = queryset.order_by("pk")
    pk = 0
    while True:
        yielded = False
        for row in queryset.filter(pk__gt=pk)[:size].iterator():
            yielded = True
            if pk_inserted:
                if original_flat:
                    yield row[-1]
                else:
                    yield row[1:]
            else:
                yield row
        if not yielded:
            break
        if isinstance(row, tuple):
            pk = row[0]
        else:  # flat=True case
            pk = row
        gc.collect()


def large_qs_iterator(queryset, size=50000):
    """Use for iterating over large Querysets.
    Do not use on a queryset that may change during the iteration and only
    use for ordered querysets. If ordering doesn't matter use
    large_qs_pk_iterator."""
    offset = 0
    while True:
        idx = -1
        limit = offset + size
        for idx, row in enumerate(queryset[offset:limit].iterator(), 1):
            yield row
        offset += idx
        if idx == -1:
            break
        gc.collect()
