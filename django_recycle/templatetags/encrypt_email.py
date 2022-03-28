# based on http://djangosnippets.org/snippets/1907/ but modified
import random

from django import template


class EncryptEmail(template.Node):
    def __init__(self, context_var):
        self.context_var = template.Variable(context_var)

    def render(self, context):
        email_address = self.context_var.resolve(context)
        character_set = '+-.0123456789@' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_' 'abcdefghijklmnopqrstuvwxyz'
        char_list = list(character_set)
        random.shuffle(char_list)

        key = ''.join(char_list)

        id_ = 'e' + str(random.randrange(1, 999999999))

        cipher_text = "".join([key[character_set.find(a)] for a in email_address])

        script = "".join(
            (
                'var a="{key}";',
                'var b=a.split("").sort().join("");',
                'var c="{cipher_text}";',
                'var d="";',
                'for(var e=0;e<c.length;e++)d+=b.charAt(a.indexOf(c.charAt(e)));',
                'document.getElementById("{id}")' '.innerHTML="<a href=\\"mailto:"+d+"\\">"+d+"</a>"',
            )
        ).format(key=key, cipher_text=cipher_text, id=id_)

        script = "eval(\"" + script.replace("\\", "\\\\").replace('"', '\\"') + "\")"
        script = '<script type="text/javascript">/*<![CDATA[*/' + script + '/*]]>*/</script>'

        return '<span id="' + id_ + '">[javascript protected email address]</span>' + script


def encrypt_email(parser, token):
    """Usage:
    {% encrypt_email user.email %}
    """
    tokens = token.contents.split()
    if len(tokens) != 2:
        raise template.TemplateSyntaxError("%r tag accepts two arguments" % tokens[0])
    return EncryptEmail(tokens[1])
