from rest_framework import serializers


class OrderPreservingMultipleChoiceField(serializers.MultipleChoiceField):
    def to_internal_value(self, data):
        new_data = set(super().to_internal_value(data))
        return [item for item in data if item in new_data]
