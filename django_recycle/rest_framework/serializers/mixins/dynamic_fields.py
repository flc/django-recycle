class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.

    Usage::

        class MySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
            class Meta:
                model = MyModel

    """
    dynamic_fields_query_param_name = "fields"
    dynamic_fields_protected = ()

    def __init__(self, *args, **kwargs):
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        request = self.context.get('request')
        if not request:
            return
        fields = request.query_params.get(self.get_dynamic_field_query_param_name())
        if not fields:
            return

        keep_fields = set([f.strip() for f in fields.split(',')]).union(
            set(self.get_dynamic_fields_protected())
            )
        for name, field in self.fields.items():
            if name in keep_fields:
                continue
            del self.fields[name]

    def get_dynamic_field_query_param_name(self):
        return self.dynamic_fields_query_param_name

    def get_dynamic_fields_protected(self):
        return self.dynamic_fields_protected
