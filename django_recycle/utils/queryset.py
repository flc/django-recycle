import gc


def large_qs_pk_iterator(queryset, size=10000, use_iterator_method=False):
    """Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 10000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support
    ordered query sets.
    """
    queryset = queryset.order_by("pk")
    pk = None
    while True:
        qs = queryset
        if pk:
            qs = qs.filter(pk__gt=pk)
        qs = qs[:size]
        if use_iterator_method:
            qs = qs.iterator()
        idx = None
        for idx, row in enumerate(qs, 1):
            # keep this before yield because the row (if it is a model object)
            # may gets deleted
            pk = row.pk
            yield row
        gc.collect()
        if idx < size:
            break


def large_vlqs_pk_iterator(queryset, size=50000, use_iterator_method=False):
    """Use for iterating over large ValuesListQuerySet's.
    Note that the implementation of the iterator does not support
    ordered query sets."""
    fields = getattr(queryset, '_fields', [])
    if fields and fields.index('pk') != 0:
        raise ValueError("The `pk` field must be included as the first field.")

    queryset = queryset.order_by("pk")
    pk = None
    while True:
        qs = queryset
        if pk:
            qs = qs.filter(pk__gt=pk)
        qs = qs[:size]
        if use_iterator_method:
            qs = qs.iterator()
        idx = 0
        for idx, row in enumerate(qs, 1):
            yield row
        if idx < size:
            break
        if isinstance(row, tuple):
            pk = row[0]
        else:  # flat=True case
            pk = row
        gc.collect()


def large_qs_iterator(queryset, size=50000, use_iterator_method=False):
    """Use for iterating over large Querysets.
    Do not use on a queryset that may change during the iteration and only
    use for ordered querysets. If ordering doesn't matter use
    large_qs_pk_iterator."""
    offset = 0
    while True:
        idx = -1
        limit = offset + size
        qs = queryset[offset:limit]
        if use_iterator_method:
            qs = qs.iterator()
        for idx, row in enumerate(qs, 1):
            yield row
        offset += idx
        if idx < size:
            break
        gc.collect()
