from django.core.exceptions import ValidationError
from django.db import models

from rest_framework import filters
from rest_framework import exceptions as drf_exceptions


class FieldsFilterBackend(filters.BaseFilterBackend):
    fields = ()  # subclass and specify

    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        fields = self.fields

        filters = {}
        for name in fields:
            if name in params:
                value = params[name]

                # special care for boolean fields
                model = queryset.model
                model_field = model._meta.get_field(name)
                if isinstance(value, str) and isinstance(
                    model_field,
                    (models.BooleanField, models.NullBooleanField)
                ):
                    if value.lower() in ("false", "0"):
                        value = False
                    elif value.lower() in ("true", "1"):
                        value = True
                    elif value.lower() in ("null",):
                        value = None

                filters[name] = value
        if filters:
            try:
                return queryset.filter(**filters)
            except ValidationError as e:
                raise drf_exceptions.ValidationError(detail=str(e))
            except Exception as e:
                raise drf_exceptions.ValidationError(detail=str(e))
        return queryset


class FieldsInBackend(filters.BaseFilterBackend):
    fields = ()  # subclass and specify
    delimiter = ","

    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        filters = {}
        for field in self.fields:
            field_param = "{}__in".format(field)
            param_value = None
            if field_param in params:
                param_value = params[field_param]
            if not param_value:
                continue
            try:
                values = set([v.strip() for v in param_value.split(self.delimiter)])
            except Exception:
                continue
            filters[field_param] = values
        if filters:
            try:
                return queryset.filter(**filters)
            except Exception:
                return queryset.none()
        return queryset
