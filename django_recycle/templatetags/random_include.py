import random

from django.template import Node, Variable, TemplateSyntaxError
from django.template.loader import get_template
from django.conf import settings


class RandomIncludeNode(Node):

    def __init__(self, template_names):
        templates = template_names.split(',')
        self.template_name = Variable(random.choice(templates))

    def render(self, context):
        try:
            template_name = self.template_name.resolve(context)
            t = get_template(template_name)
            return t.render(context)
        except TemplateSyntaxError:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''
        except:
            return ''  # Fail silently for invalid included templates.


def random_include(parser, token):
    """
    Loads a template and renders it with the current context.

    Example::

    {% random_include "foo/some_include_1","foo/some_include_2 %}
    """
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "%r tag takes one argument: the name of the template to be included" % bits[0]
    # path = bits[1]
    return RandomIncludeNode(bits[1])
