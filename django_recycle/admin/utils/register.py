from django.contrib import admin
from django.db.models import Model


def auto_register_admin(models, admin_class=None):
    """Dummy registers models to admin.

    :param models: models module
    """
    if admin_class is None:
        admin_class = admin.ModelAdmin

    for attr_name in dir(models):
        attr = getattr(models, attr_name)
        try:
            if issubclass(attr, Model):
                model = attr
                if model._meta.abstract:
                    continue
                if not model._meta.managed:
                    continue
                try:
                    admin.site.register(model, admin_class)
                except admin.sites.AlreadyRegistered:
                    continue
        except TypeError:
            continue
