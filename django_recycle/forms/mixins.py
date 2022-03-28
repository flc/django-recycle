from django import forms
from django.forms.boundfield import BoundField
from django.utils.translation import gettext as _
from django.utils.translation import gettext

from core.utils.looping import grouper


class FormFieldWithFormMixin:

    def __init__(self, form, *args, **kwargs):
        self.form = form
        super().__init__(*args, **kwargs)


class PrefixedErrorsFormMixin:

    @property
    def errors(self):
        errors = super().errors
        # includes the prefix in the error keys
        new_errors = {}
        for key, value in list(errors.items()):
            new_errors[f"{self.prefix}-{key}"] = value
        return new_errors


def _unique_together_clean_field_method(self):
    field_value = self.cleaned_data.get(self.unique_together_form_field)
    if self.unique_together_form_field_allow_empty and not field_value:
        return field_value

    kwargs = self.get_unique_together_filter_kwargs(field_value)
    query = self.get_unique_together_queryset(**kwargs)
    if self._instance is not None:
        query = query.exclude(pk=self._instance.pk)
    if query.exists():
        raise forms.ValidationError(
                            self.get_unique_together_error_msg(field_value))
    return field_value


class ValidateUniqueTogetherFormMixin:
    unique_together_form_field = None
    unique_together_form_field_lookup = "iexact"
    unique_together_form_field_allow_empty = False
    unique_together_against_field = None
    unique_together_model = None
    unique_together_error_msg = _("This value is already in use.")

    def __init__(self, *args, **kwargs):
        if isinstance(self, forms.ModelForm):
            self._instance = kwargs.get("instance", None)
        else:
            self._instance = kwargs.pop("instance", None)
        setattr(self.__class__,
                f'clean_{self.unique_together_form_field}',
                _unique_together_clean_field_method)
        super().__init__(*args, **kwargs)

    def get_unique_together_filter_kwargs(self, field_value):
        kwargs = {
            "{}__{}".format(self.unique_together_form_field,
                        self.unique_together_form_field_lookup): field_value,
            self.unique_together_against_field:
                                        self.unique_together_against_value,
        }
        return kwargs

    def get_unique_together_queryset(self, **kwargs):
        return self.unique_together_model._default_manager.filter(**kwargs)

    def get_unique_together_error_msg(self, field_value):
        return self.unique_together_error_msg


class MinMaxFormMixin(forms.Form):
    # min_max_field_names = ("min", "max")
    min_max_field_names = None
    min_max_field_class = forms.FloatField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.min_max_field_names is not None:
            self.min_max_names = self.min_max_field_names[:]
        else:
            self.min_max_names = []
            self.create_fields()

    def create_fields(self):
        min_max_fields = self.get_min_max_fields()
        for name, field in min_max_fields:
            self.fields[name] = field
            self.min_max_names.append(name)

    def get_min_max_field_class(self):
        return self.min_max_field_class

    def get_min_max_fields(self):
        klass = self.get_min_max_field_class()
        return (
            ("min", klass(label=_('Min value'), required=False)),
            ("max", klass(label=_('Max value'), required=False)),
        )

    def get_min_max_field_pair_label(self, min_field, max_field):
        return min_field.label.rsplit(" ", 1)[0].strip()

    def get_min_max_field_pair_help_text(self, min_field, max_field):
        return min_field.help_text

    def get_grouped_min_max_fields(self):
        data = []
        for min_name, max_name in grouper(2, self.min_max_names):
            min_field = BoundField(self, self.fields[min_name], min_name)
            max_field = BoundField(self, self.fields[max_name], max_name)
            label = self.get_min_max_field_pair_label(min_field, max_field)
            help_text = self.get_min_max_field_pair_help_text(min_field,
                                                              max_field)
            data.append((min_field, max_field, label, help_text))
        return data

    def clean(self):
        cleaned_data = super().clean()

        for min_name, max_name in grouper(2, self.min_max_names):
            min_value = cleaned_data.get(min_name, None)
            max_value = cleaned_data.get(max_name, None)

            if min_value is not None and max_value is not None:
                if min_value > max_value:
                    error_msg = gettext("Max value should be greater than "
                                         "or equal to min value.")
                    self._errors[min_name] = self.error_class([error_msg])
                    # These fields are no longer valid. Remove them from the
                    # cleaned data.
                    del cleaned_data[min_name]
                    del cleaned_data[max_name]

        return cleaned_data


class RequiredMinMaxFormMixin(MinMaxFormMixin):
    """Use when either the min or the max value is required."""

    def clean(self):
        cleaned_data = super().clean()

        for min_name, max_name in grouper(2, self.min_max_names):
            min_value = cleaned_data.get(min_name, None)
            max_value = cleaned_data.get(max_name, None)

            if (self._errors.get(min_name, None) is None and
                self._errors.get(max_name, None) is None):
                # both are valid so far
                if min_value is None and max_value is None:
                    error_msg = gettext("You have to specify either "
                                         "the min or the max value.")
                    self._errors[min_name] = self.error_class([error_msg])
                    # These fields are no longer valid. Remove them
                    # from the cleaned data.
                    del cleaned_data[min_name]
                    del cleaned_data[max_name]

        return cleaned_data
