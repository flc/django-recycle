import types

from django.core.exceptions import FieldDoesNotExist
from rest_framework.fields import ChoiceField
from django_countries.fields import CountryField as CountryModelField


def _to_representation(self, value):
    if str(value) == '':
        return ''
    return ChoiceField.to_representation(self, value)


class CountryFieldMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # XXX uh, this is gonna be a bit ugly
        # we will monkeypatch ChoiceField.to_representation
        # on the instance level
        model = getattr(self.Meta, 'model')

        for name, field in list(self.fields.items()):
            try:
                model_field = model._meta.get_field(name)
            except FieldDoesNotExist:
                continue
            if isinstance(model_field, CountryModelField):
                new_method = types.MethodType(
                    _to_representation, field
                    )
                field.to_representation = new_method
