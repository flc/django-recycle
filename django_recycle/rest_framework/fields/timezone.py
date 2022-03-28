import pytz

from rest_framework.fields import ChoiceField


class TimeZoneField(ChoiceField):

    def __init__(self, *args, **kwargs):
        tzs = [(tz, tz) for tz in pytz.common_timezones]
        kwargs['choices'] = kwargs.get("choices", tzs)
        super().__init__(*args, **kwargs)
