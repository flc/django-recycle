from django.db import models


class NullableCharField(models.CharField):
    description = "CharField that stores NULL but returns ''"
    # this ensures to_python will be called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, models.CharField):
            return value
        return value or ''

    def get_prep_value(self, value):
        return value or None
