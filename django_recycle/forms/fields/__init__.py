from django.utils.translation import gettext_lazy as _

from accounts.helpers import get_full_name_or_username

from ..mixins import FormFieldWithFormMixin
from ..groupedmodelchoicefield import GroupedModelChoiceField


class UserGroupModelChoiceField(FormFieldWithFormMixin, GroupedModelChoiceField):
    # label of the group of objects without a user (e.g. created by anonymous visitors)
    empty_group_label = _('Anonymous user')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_group_label(self, group):
        if group is None:
            return self.empty_group_label
        user = self.form.user
        name = get_full_name_or_username(group)
        if group == user:
            return _('%(name)s (You)') % {'name': name}
        return name


from .day_week_month import *
