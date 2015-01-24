from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    )
from django.utils.translation import ugettext_lazy as _


class MaxValueLessValidator(MaxValueValidator):
    compare = lambda self, a, b: a >= b
    message = _('Ensure this value is less than %(limit_value)s.')


class MinValueGreaterValidator(MinValueValidator):
    compare = lambda self, a, b: a <= b
    message = _('Ensure this value is greater than %(limit_value)s.')
