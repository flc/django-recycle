from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.db.models.constants import LOOKUP_SEP
from django.db import models

from rest_framework import filters
from rest_framework import exceptions as drf_exceptions

from ...db.utils import find_model_field_by_lookup


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
                # and fields that can accept null as a filter value
                model = queryset.model
                try:
                    model_field = find_model_field_by_lookup(model, name)
                except FieldDoesNotExist:
                    # special care for isnull lookups
                    if name.endswith('__isnull'):
                        if value.lower() in ("false", "0"):
                            value = False
                        elif value.lower() in ("true", "1"):
                            value = True
                else:
                    if isinstance(value, str) and isinstance(
                        model_field, (models.BooleanField, models.NullBooleanField)
                    ):
                        if value.lower() in ("false", "0"):
                            value = False
                        elif value.lower() in ("true", "1"):
                            value = True
                        elif value.lower() in ("null",):
                            value = None

                    if (
                        isinstance(value, str)
                        and model_field.null
                        and not isinstance(model_field, (models.CharField, models.TextField))
                    ):
                        if value.lower() in ("null",):
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
            field_param = f"{field}__in"
            param_value = None
            if field_param in params:
                param_value = params[field_param]
            if not param_value:
                continue
            try:
                values = {v.strip() for v in param_value.split(self.delimiter)}
            except Exception:
                continue
            filters[field_param] = values
        if filters:
            try:
                return queryset.filter(**filters)
            except Exception:
                return queryset.none()
        return queryset
