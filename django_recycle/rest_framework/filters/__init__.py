from django.core.exceptions import ValidationError

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
                if value in ("false", "0", "False"):
                    value = False
                filters[name] = value
        if filters:
            try:
                return queryset.filter(**filters)
            except ValidationError as e:
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
