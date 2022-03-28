import six

from django.forms.forms import NON_FIELD_ERRORS, BoundField
from django.utils.safestring import mark_safe


class DynamicMultiForm:
    # if self.validate fail and defer_form_validation is True the validation of
    # the independent forms will be skipped;
    # it's useful when you do expensive validations in the forms
    defer_form_validation = False

    def __init__(self, data=None, forms=None, **kwargs):
        """
        :param data:
            list of (form_class, data) tuples
            form_class can be form or formset

        """
        if forms is None:
            forms = []
            for d in data:
                form_class = d[0]
                form_data = d[1]
                form = form_class(form_data, **kwargs)
                forms.append(form)
        self.forms = forms
        self._errors = []

    def __unicode__(self):
        return self.as_table()

    def as_table(self):
        return mark_safe('\n'.join([form.as_table() for form in self.forms]))

    def save(self, commit=True):
        return tuple(form.save(commit) for form in self.forms)

    def validate(self):
        return True

    def is_valid(self):
        self._valid = self.validate()
        if not self._valid:
            return False

        # force to validate all forms
        is_valids = [form.is_valid() for form in self.forms]
        # return all(form.is_valid() for form in self.forms)

        is_valids.append(self._valid)
        return all(is_valids)

    def get_errors(self):
        form_errors = []
        if not self.defer_form_validation or self._valid:
            for form in self.forms:
                if hasattr(form, "non_form_errors"):
                    # it's a formset
                    form_errors.append({
                        'formset_errors': form.non_form_errors(),
                        'form_errors': form.errors,
                    })
                else:
                    form_errors.append(form.errors)
        errors = {
            NON_FIELD_ERRORS: [str(x) for x in self._errors],
            'forms': form_errors,
        }
        return errors

    @property
    def errors(self):
        return self.get_errors()

    def non_field_errors(self):
        """
        Returns an ErrorList of errors that aren't associated with a particular
        field -- i.e., from Form.clean(). Returns an empty ErrorList if there
        are none.
        """
        return self.errors.get(NON_FIELD_ERRORS)

    def __iter__(self):
        for form in self.forms:
            for name, field in list(form.fields.items()):
                yield BoundField(form, field, name)
