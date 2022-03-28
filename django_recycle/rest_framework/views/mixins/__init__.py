class SerializerClassMethodOverrideMixin:
    serializer_class_method_overrides = {}

    def get_serializer_class(self):
        return self.serializer_class_method_overrides.get(
            self.request.method,
            super().get_serializer_class()
            )


class SerializerClassActionOverrideMixin:
    serializer_class_action_overrides = {}

    def get_serializer_class(self):
        return self.serializer_class_action_overrides.get(
            self.action,
            super().get_serializer_class()
            )
