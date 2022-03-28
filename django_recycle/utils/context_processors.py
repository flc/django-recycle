import importlib


class ModuleConstants(object):
    __name__ = ""

    def __init__(self, module):
        if isinstance(module, str):
            try:
                module = importlib.import_module(module)
            except ImportError:
                raise ImportError("Could not import %s" % module)

        context = {}
        for c in dir(module):
            if c == c.upper():
                context[c] = getattr(module, c)
        self.context = context

    def __call__(self, request):
        return self.context
