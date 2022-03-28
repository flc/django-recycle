from django.db import models


class NullableCharField(models.CharField):
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
