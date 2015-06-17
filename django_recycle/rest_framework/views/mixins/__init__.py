class SerializerClassMethodOverrideMixin(object):
    serializer_class_method_overrides = {}

    def get_serializer_class(self):
        return self.serializer_class_method_overrides.get(
            self.request.method,
            super(SerializerClassMethodOverrideMixin, self).get_serializer_class()
            )


class SerializerClassActionOverrideMixin(object):
    serializer_class_action_overrides = {}

    def get_serializer_class(self):
        return self.serializer_class_action_overrides.get(
            self.action,
            super(SerializerClassActionOverrideMixin, self).get_serializer_class()
            )
