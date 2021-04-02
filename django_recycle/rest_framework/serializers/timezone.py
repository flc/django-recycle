import pytz
from timezone_field import TimeZoneField

from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
from rest_framework import serializers


class TimeZoneSerializerField(serializers.ChoiceField):
    default_error_messages = {
        'invalid': _('A valid timezone is required.'),
    }

    def __init__(self, **kwargs):
        choices = TimeZoneField.default_choices
        try:
            choices = [c[1] for c in choices]
        except IndexError:
            pass
        super().__init__(choices, **kwargs)

    def to_internal_value(self, data):
        try:
            return pytz.timezone(force_str(data))
        except pytz.UnknownTimeZoneError:
            self.fail('invalid')

    def to_representation(self, value):
        return str(super().to_representation(value))
