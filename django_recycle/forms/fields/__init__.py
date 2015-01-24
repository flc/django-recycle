from django.utils.translation import ugettext_lazy as _

from accounts.helpers import get_full_name_or_username

from ..mixins import FormFieldWithFormMixin
from ..groupedmodelchoicefield import GroupedModelChoiceField


class UserGroupModelChoiceField(FormFieldWithFormMixin,
                                GroupedModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(UserGroupModelChoiceField, self).__init__(*args, **kwargs)

    def get_group_label(self, group):
        user = self.form.user
        name = get_full_name_or_username(group)
        if group == user:
            return _('%(name)s (You)') % {'name': name}
        return name


from .day_week_month import *
