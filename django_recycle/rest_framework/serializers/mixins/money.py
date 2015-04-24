import types

from django.db.models.fields import FieldDoesNotExist
from rest_framework import serializers
from djmoney.models import fields as djmoney_fields


class MoneyField(serializers.DecimalField):
    type_name = 'MoneyField'

    def __init__(self, max_digits=10, decimal_places=2, *args, **kwargs):
        return super(MoneyField, self).__init__(
            max_digits, decimal_places, *args, **kwargs
            )

    def to_representation(self, value):
        if not value:
            return None
        # return {
        #     'value': value.amount,
        #     'currency': str(value.currency)
        #     }
        return value.amount


class MoneyFieldMixin(object):

    def __init__(self, *args, **kwargs):
        super(MoneyFieldMixin, self).__init__(*args, **kwargs)

        declared_fields = self.__class__._declared_fields
        model = getattr(self.Meta, 'model')
        read_only_fields = getattr(self.Meta, 'read_only_fields', None)

        for name, field in self.fields.items():
            if name in declared_fields:
                # if the field is declared explicitly we don't
                # do any manipulation with it, we assume the developer
                # does the correct thing
                continue
            try:
                model_field = model._meta.get_field(name)
            except FieldDoesNotExist:
                continue
            if isinstance(model_field, djmoney_fields.MoneyField):
                self.fields[name] = MoneyField(
                    max_digits=field.max_digits,
                    decimal_places=field.decimal_places,
                    )
            # djmoney sets the currency field to editable=False and thus
            # rest framework considers it read_only
            if (isinstance(model_field, djmoney_fields.CurrencyField) and
                read_only_fields and name not in read_only_fields):
                field.read_only = False
