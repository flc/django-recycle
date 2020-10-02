from django.core.exceptions import FieldDoesNotExist
from django.db.models.constants import LOOKUP_SEP


def find_model_field_by_lookup(model, lookup):
    lookups = list(reversed(lookup.split(LOOKUP_SEP)))
    field = None

    while model and lookups:
        current = lookups.pop()
        field = model._meta.get_field(current)
        model = field.related_model
        if lookups and model is None:
            raise FieldDoesNotExist(lookup)
    return field
