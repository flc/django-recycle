from django.contrib import admin
from django.contrib.admin import widgets


class RawIdModelAdminMixin(object):
    raw_id_exclude = []

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        if db_field.name in self.raw_id_exclude:
            return super().formfield_for_foreignkey(db_field, request=None, **kwargs)

        db = kwargs.get('using')
        # django 2.0 compatibility
        rel = getattr(db_field, 'rel', db_field.remote_field)
        kwargs['widget'] = widgets.ForeignKeyRawIdWidget(rel,
                                                         self.admin_site,
                                                         using=db)
        return db_field.formfield(**kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.raw_id_exclude:
            return super().formfield_for_manytomany(db_field, request=None, **kwargs)

        # django 2.0 compatibility
        rel = getattr(db_field, 'rel', db_field.remote_field)

        if not rel.through._meta.auto_created:
            return None

        db = kwargs.get('using')
        kwargs['widget'] = widgets.ManyToManyRawIdWidget(rel,
                                                         self.admin_site,
                                                         using=db)
        return db_field.formfield(**kwargs)


class RawIdModelAdmin(RawIdModelAdminMixin, admin.ModelAdmin):
    pass
