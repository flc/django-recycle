from collections import defaultdict

from django.db import models
from django.core.exceptions import FieldDoesNotExist


class TransformQuerySet(models.query.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transform_fns = []

    def _clone(self, *args, **kwargs):
        c = super()._clone(*args, **kwargs)
        c._transform_fns = self._transform_fns[:]
        return c

    def transform(self, fn):
        c = self._clone()
        c._transform_fns.append(fn)
        return c

    def _iterator(self, *args, **kwargs):
        result_iter = super()._iterator(*args, **kwargs)
        if self._transform_fns:
            results = list(result_iter)
            for fn in self._transform_fns:
                fn(results)
            # return iter(results)
            return results
        return result_iter


class TransformManager(models.Manager):
    def get_queryset(self):
        return TransformQuerySet(self.model)


def lookup_foreignkey(items, fields, chunk_size=1000000):
    """Usage:
    from functools import partial
    queryset = queryset._clone(TransformQuerySet).transform(
        partial(lookup_foreignkey, fields=["foreignkey_field1", "foreignkey_field2"])
    )

    or use it as standalone (note that you can also use __ to lookup deeper)

    queryset = MyModel.objects.all()
    items = list(queryset)
    lookup_foreignkey(items, ["foreignkey_field1__subforeignkey_field", "foreignkey__field2"]
    """
    if not items or not fields:
        return

    model = items[0].__class__

    for field in fields:
        split_fields = field.split("__")
        field_name = split_fields[0]
        try:
            field = model._meta.get_field(field_name)
            column = field.column
        except FieldDoesNotExist:
            continue

        dd = defaultdict(list)

        for item in items:
            dd[getattr(item, column)].append(item)

        if hasattr(field, 'rel'):
            query_model = field.rel.to
        else:
            query_model = field.remote_field.model
        objs = []
        for obj in query_model.objects.filter(id__in=dd.keys()).iterator(chunk_size=chunk_size):
            for item in dd[obj.id]:
                setattr(item, field_name, obj)
                objs.append(obj)

        remaining_fields = ["__".join(split_fields[1:])]
        lookup_foreignkey(objs, remaining_fields)
