from copy import copy

from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.html import conditional_escape
from django.utils.encoding import force_str


class ClassAttrAwareWidgetMixin:

    def build_attrs(self, extra_attrs=None, **kwargs):
        """Reimplements forms.Widget.build_attrs"""
        extra_attrs = copy(extra_attrs)
        attrs = dict(self.attrs, **kwargs)
        if extra_attrs:
            extra_classes = extra_attrs.pop("class", None)
            if extra_classes is not None:
                if 'class' not in attrs:
                    attrs['class'] = extra_classes
                else:
                    attrs['class'] = " ".join([attrs['class'], extra_classes])
            attrs.update(extra_attrs)
        return attrs


class ClassAttrAwareTextInput(ClassAttrAwareWidgetMixin, forms.TextInput):
    pass


class ClassAttrAwareHiddenInput(ClassAttrAwareWidgetMixin, forms.HiddenInput):
    pass


class HorizontalRadioRenderer(forms.RadioSelect.renderer):

    def render(self):
        return mark_safe('\n'.join(['%s\n' % w for w in self]))


class NewlinePreservingTextarea(forms.widgets.Textarea):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe('<textarea%s>\r\n%s</textarea>' % (flatatt(final_attrs),
                conditional_escape(force_str(value))))
