class TaggedItemViewMixin:
    tags_field_name = "tags"

    def _adjust_tags_data(self, data, key="text"):
        """
        [{'text': 'tagX'}, {'text': 'tagY'}] -> ['tagX', 'tagY']
        """
        if data and isinstance(data[0], dict):
            return [tag[key] for tag in data]
        return data

    def get_tagged_object(self, obj):
        return obj

    def post_save(self, obj, *args, **kwargs):
        super().post_save(obj, *args, **kwargs)

        tagged_obj = self.get_tagged_object(obj)
        if type(getattr(tagged_obj, self.tags_field_name)) is list:
            # If tags were provided in the request
            try:
                saved_obj = tagged_obj._meta.model.objects.get(pk=tagged_obj.pk)
                # XXX optimize later
                tags_field = getattr(saved_obj, self.tags_field_name)
                tags_field.clear()
            except tagged_obj._meta.model.DoesNotExist:
                pass
            tags_field.add(*self._adjust_tags_data(getattr(tagged_obj, self.tags_field_name)))
