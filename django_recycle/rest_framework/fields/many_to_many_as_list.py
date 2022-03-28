from rest_framework import serializers

from ..compat import Field


class ManyToManyAsListField(Field):
    model = None
    field_name = "name"

    def to_native(self, obj):
        return obj.values_list(self.field_name, flat=True)

    def from_native(self, data):
        filter_kwargs = {
            f"{self.field_name}__in": data
        }
        exists = list(self.model._default_manager.filter(**filter_kwargs))
        exists_vals = [getattr(obj, self.field_name) for obj in exists]
        not_exists = [value for value in data if value not in exists_vals]
        objects = [
            self.model._default_manager.create(**{self.field_name: value})
            for value in not_exists
            ]
        exists.extend(objects)
        return exists
