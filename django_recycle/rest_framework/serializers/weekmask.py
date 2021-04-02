from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

import numpy


class WeekmaskSerializerField(serializers.CharField):
    default_error_messages = {
        'invalid': _('Invalid business day weekmask string.'),
    }

    def to_internal_value(self, value):
        try:
            numpy.busdaycalendar(weekmask=value)
        except ValueError as e:
            self.fail('invalid')
        return value
