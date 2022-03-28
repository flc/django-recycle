from rest_framework import serializers
from easy_thumbnails.alias import aliases


class ThumbnailerImageField(serializers.ImageField):
    # use_files = True
    type_name = 'ThumbnailerImageField'
    # type_label = 'image upload'

    def to_native(self, value):
        if not value:
            return None
        urls = {'original': value.url}
        key = "{}.{}.{}".format(value.instance._meta.app_label, value.instance._meta.object_name, value.field.name)
        aliases_thumbnails = aliases.all(key)
        for thumb in aliases_thumbnails:
            urls[thumb] = value[thumb].url
        return urls
