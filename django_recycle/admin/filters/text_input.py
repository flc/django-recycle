from django.contrib.admin import ListFilter
from django.utils.translation import ugettext_lazy as _


class SingleTextInputFilter(ListFilter):
    """
    renders filter form with text input and submit button
    """
    parameter_name = None
    template = "admin/textinput_filter.html"

    def __init__(self, request, params, model, model_admin):
        super(SingleTextInputFilter, self).__init__(
            request, params, model, model_admin)
        if self.parameter_name is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify "
                "a 'parameter_name'." % self.__class__.__name__)

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def value(self):
        """
        Returns the value (in string format) provided in the request's
        query string for this filter, if any. If the value wasn't provided then
        returns None.
        """
        return self.used_parameters.get(self.parameter_name, None)

    def has_output(self):
        return True

    def expected_parameters(self):
        """
        Returns the list of parameter names that are expected from the
        request's query string and that will be used by this filter.
        """
        return [self.parameter_name]


    def choices(self, cl):
        all_choice = {
            'selected': self.value() is None,
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': _('All'),
        }
        return ({
            'get_query': cl.params,
            'current_value': self.value(),
            'all_choice': all_choice,
            'parameter_name': self.parameter_name
        }, )


def foreign_key_single_input_factory(field):
    _field_name = field.field.name
    _title = field.field.verbose_name

    class ForeignKeyFilter(SingleTextInputFilter):
        title = _title
        parameter_name = _field_name

        def queryset(self, request, queryset):
            value = self.value()
            if value:
                kwargs = {_field_name: value}
                return queryset.filter(**kwargs)

    return ForeignKeyFilter
