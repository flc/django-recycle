from django.contrib import admin
from django.db.models.base import ModelBase


def auto_register_admin(models, admin_class=None):
    """Dummy registers models to admin.

    :param models: models module
    """
    for attr_name in dir(models):
        attr = getattr(models, attr_name)
        try:
            if isinstance(attr, ModelBase):
                model = attr
                if model._meta.abstract:
                    continue
                if not model._meta.managed:
                    continue
                try:
                    admin.site.register(model, admin_class=admin_class)
                except admin.sites.AlreadyRegistered:
                    continue
        except TypeError:
            continue
