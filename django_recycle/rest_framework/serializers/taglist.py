from rest_framework import serializers
from rest_framework.exceptions import ParseError

from ..compat import Field


class TagListSerializer(Field):

    def from_native(self, data):
        if type(data) is not list:
            raise ParseError("expected a list of data")
        return data

    def to_native(self, obj):
        if type(obj) is not list:
            return [tag.name for tag in obj.iterator()]
        return obj
