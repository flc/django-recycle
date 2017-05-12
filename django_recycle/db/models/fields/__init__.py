import django
from django.db import models


if django.VERSION < (1, 8):
    base_field_class = six.with_metaclass(models.SubfieldBase, models.CharField)
else:
    base_field_class = models.CharField


class NullableCharField(base_field_class):
    description = "CharField that stores NULL but returns ''"
    # this ensures to_python will be called
    # __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, models.CharField):
            return value
        return value or ''

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        return value or None
