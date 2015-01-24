from rest_framework import serializers


class ManyToManyAsListField(serializers.WritableField):
    model = None
    field_name = "name"

    def to_native(self, obj):
        return obj.values_list(self.field_name, flat=True)

    def from_native(self, data):
        filter_kwargs = {
            "{}__in".format(self.field_name): data
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
