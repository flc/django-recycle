"""Based on http://djangosnippets.org/snippets/1968/ but slightly
modified to make it a bit more flexible."""

from itertools import groupby

from django.forms.models import (
    ModelChoiceIterator,
    ModelChoiceField,
    ModelMultipleChoiceField,
    )
from django.db.models import ForeignKey


class GroupedModelChoiceIterator(ModelChoiceIterator):

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)

        group_by_field = self.field.group_by_field
        query = self.field._get_query()
        choice_cache = self.field.choice_cache

        if self.field.cache_choices:
            if choice_cache is None:
                choice_cache = [
                    (self.field.get_group_label(group), [self.choice(ch) for ch in choices])
                        for group, choices in groupby(query,
                            key=lambda row: getattr(row, group_by_field))
                ]
            for choice in choice_cache:
                yield choice
        else:
            for group, choices in groupby(
                                query,
                                key=lambda row: getattr(row, group_by_field),
                                ):
                yield (
                    self.field.get_group_label(group),
                    [self.choice(ch) for ch in choices],
                    )


class GroupedModelChoiceFieldMixin(object):

    def __init__(self, group_by_field, group_label=None, *args, **kwargs):
        """
        group_by_field is the name of a field on the model
        group_label is a function to return a label for each choice group
        """
        super(GroupedModelChoiceFieldMixin, self).__init__(*args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label

    def _get_query(self):
        group_by_field = self.group_by_field
        if not self.queryset.query.order_by:
            query = self.queryset.order_by(group_by_field)
        else:
            new_order_by = [group_by_field] + self.queryset.query.order_by
            query = self.queryset.order_by(*new_order_by)

        if isinstance(query.model._meta.get_field(group_by_field), ForeignKey):
            query = query.select_related(group_by_field)

        return query

    def _get_choices(self):
        """
        Exactly as per ModelChoiceField except returns new iterator class
        """
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, ModelChoiceField._set_choices)

    def get_group_label(self, group):
        return self.group_label(group)


class GroupedModelChoiceField(GroupedModelChoiceFieldMixin,
                              ModelChoiceField):
    pass


class GroupedModelMultipleChoiceField(GroupedModelChoiceFieldMixin,
                                      ModelMultipleChoiceField):
    pass
