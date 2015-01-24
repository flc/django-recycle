from django.db.models import Q


class PrefixedQ(Q):
    accessor = ""

    def __init__(self, **kwargs):
        # Prefix all the dictionary keys
        super(PrefixedQ, self).__init__(**dict(
            (self.prefix(k), v) for k, v in kwargs.items()
        ))

    def prefix(self, *args):
        return "__".join(a for a in (self.accessor,) + args if a)


def prefix_q(q, prefix):
    newchildren = []
    for child in q.children:
        if isinstance(child, Q):
            newchildren.append(prefix_q(child, prefix))
        else:
            key, value = child
            newchildren.append(("__".join((prefix, key)), value))
    q.children = newchildren
    return q
