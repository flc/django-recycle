from django.shortcuts import _get_queryset


def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.

    .. note:: Like with get(), a MultipleObjectsReturned will be raised if more
    than one object is found.

    :param klass:
        may be a Model, Manager, or QuerySet object. All other passed
        arguments and keyword arguments are used in the get() query.
    :return: Model instance or None
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
