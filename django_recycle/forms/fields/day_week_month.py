from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _


DAY = 10
WEEK = 20
MONTH = 30
CHOICES = (
    (DAY, _("Day(s)")),
    (WEEK, _("Week(s)")),
    (MONTH, _("Month(s)")),
)


class DayWeekMonthWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        _widgets = (
            widgets.TextInput(),
            widgets.Select(choices=CHOICES),
        )
        super().__init__(_widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            amount = value[0]
            choice = value[1]
            return [amount, choice]
        return [None, None]


class DayWeekMonthField(forms.MultiValueField):
    widget = DayWeekMonthWidget

    def __init__(self, *args, **kwargs):
        min_value = kwargs.pop("min_value")
        try:
            max_value = kwargs.pop("max_value")
        except KeyError:
            max_value = None
        fields = (
            forms.IntegerField(min_value=min_value, max_value=max_value, required=True),
            forms.TypedChoiceField(choices=CHOICES, required=True, coerce=int),
        )
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2:
            amount = data_list[0]
            choice = data_list[1]
            return (amount, choice)
        raise forms.ValidationError(self.error_messages['required'])

    @staticmethod
    def get_days(amount, choice):
        if amount is None or choice is None:
            return None
        if choice == DAY:
            return amount
        if choice == WEEK:
            return amount * 7
        if choice == MONTH:
            return amount * 30
