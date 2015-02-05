import rest_framework
from distutils.version import StrictVersion


if StrictVersion(rest_framework.VERSION) < StrictVersion('3.0.0'):
    from rest_framework.serializers import Serializer
    class Field(rest_framework.serializers.WritableField):
        pass
    class ReadOnlyField(rest_framework.serializers.Field):
        pass
else:
    class Serializer(rest_framework.serializers.Serializer):
        @property
        def object(self):
            return self.validated_data
    from rest_framework.serializers import Field, ReadOnlyField

