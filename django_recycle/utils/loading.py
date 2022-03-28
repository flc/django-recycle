from importlib import import_module


def import_class(class_string):
    module, classname = class_string.rsplit(".", 1)
    m = import_module(module)
    return getattr(m, classname)


class ClassMapper:
    overrides = {}

    def __init__(self, module_pattern, attr_name, callable_attr_name=None, fallback_class=None):
        self.module_pattern = module_pattern
        self.attr_name = attr_name
        self.callable_attr_name = callable_attr_name
        self.fallback_class = fallback_class

        self._cache = {}

    def _get_fallback_class(self):
        if not isinstance(self.fallback_class, str):
            # assume it's a class already
            klass = self.fallback_class
        else:
            klass = import_class(self.fallback_class)
        return klass

    def get(self, name):
        if name in self._cache:
            return self._cache[name]

        klass = None
        klass_path = self.overrides.get(name, None)
        if klass_path is not None:
            if not isinstance(klass_path, str):
                # assume it's a class already
                klass = klass_path
            else:
                klass = import_class(klass_path)
        else:
            module_path = self.module_pattern.format(name=name)
            module = None
            try:
                module = import_module(module_path)
            except ImportError as exc:
                klass = self._get_fallback_class()

            if klass is None:
                if module is None:
                    raise exc

                if hasattr(module, self.callable_attr_name):
                    klass = getattr(module, self.callable_attr_name)()
                    # do not cache it
                    return klass
                else:
                    klass = getattr(module, self.attr_name, None)
                    if klass is None:
                        klass = self._get_fallback_class()

        self._cache[name] = klass
        return klass
