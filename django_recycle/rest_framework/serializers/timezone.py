import pytz
from timezone_field import TimeZoneField

from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
from rest_framework import serializers


try:
    from timezone_field.backends import get_tz_backend
    tz_backend_available = True
except ImportError:
    tz_backend_available = False

if tz_backend_available:
    from timezone_field.rest_framework import TimeZoneSerializerField

    class TimeZoneSerializerChoiceField(TimeZoneSerializerField, serializers.ChoiceField):
        def __init__(self, **kwargs):
            self.use_pytz = kwargs.pop("use_pytz", None)
            self.tz_backend = get_tz_backend(use_pytz=self.use_pytz)
            super().__init__([(tz, tz) for tz in self.tz_backend.base_tzstrs], **kwargs)

else:
    class TimeZoneSerializerField(serializers.ChoiceField):
        default_error_messages = {
            'invalid': _('A valid timezone is required.'),
        }

        def __init__(self, **kwargs):
            # default_choices removed in django-timezone-field==5.0
            if hasattr(TimeZoneField, 'default_choices'):
                choices = TimeZoneField.default_choices
                try:
                    choices = [c[1] for c in choices]
                except IndexError:
                    pass
            else:
                # django-timezone-field==5.0
                pytz_tzs = TimeZoneField.default_pytz_tzs
                choices = [tz.zone for tz in pytz_tzs]

            super().__init__(choices, **kwargs)

        def to_internal_value(self, data):
            try:
                return pytz.timezone(force_str(data))
            except pytz.UnknownTimeZoneError:
                self.fail('invalid')

        def to_representation(self, value):
            return str(super().to_representation(value))
