import functools
from concurrent.futures import ProcessPoolExecutor

import more_itertools

import django
from django.db import transaction


def update_chunk(pk_chunk, update_data, model):
    with transaction.atomic():
        return model._default_manager.filter(pk__in=pk_chunk).update(**update_data)


def update_queryset_in_chunks_parallel(
    queryset,
    update_data: dict,
    chunk_size: int = 1000,
    iterator_chunk_size: int | None = None,
    max_workers: int | None = None
):
    model = queryset.model
    pks = queryset.order_by('pk').values_list('pk', flat=True).iterator(chunk_size=iterator_chunk_size)
    pks_chunks = list(more_itertools.chunked(pks, chunk_size))

    update_func = functools.partial(update_chunk, update_data=update_data, model=model)

    # close db connections to avoid db errors
    django.db.connections.close_all()

    total_updated = 0
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for count in executor.map(update_func, pks_chunks):
            total_updated += count
    return total_updated
