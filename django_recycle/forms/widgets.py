from django import forms


class ClassAttrAwareWidgetMixin:
    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build an attribute dictionary."""
        classes1 = base_attrs.pop('class', '')
        classes2 = extra_attrs.pop('class', '')
        classes = " ".join(clss for clss in [classes1, classes2] if clss)
        ret = {**base_attrs, **(extra_attrs or {}), **{'class': classes}}
        return ret


class ClassAttrAwareTextInput(ClassAttrAwareWidgetMixin, forms.TextInput):
    pass


class ClassAttrAwareHiddenInput(ClassAttrAwareWidgetMixin, forms.HiddenInput):
    pass
