from django.contrib import admin
from django.contrib.admin import widgets


class RawIdModelAdminMixin(object):

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get('using')
        kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.rel,
                                                         self.admin_site,
                                                         using=db)
        return db_field.formfield(**kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if not db_field.rel.through._meta.auto_created:
            return None

        db = kwargs.get('using')
        kwargs['widget'] = widgets.ManyToManyRawIdWidget(db_field.rel,
                                                         self.admin_site,
                                                         using=db)
        return db_field.formfield(**kwargs)


class RawIdModelAdmin(RawIdModelAdminMixin, admin.ModelAdmin):
    pass
