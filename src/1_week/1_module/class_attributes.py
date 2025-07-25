from datetime import datetime


class AddNewAttr(type):
    def __new__(cls, name, bases, attrs):
        original_init = attrs.get("__init__")

        def __init__(self, *args, **kwargs):
            self.created_at = datetime.now()
            if original_init:
                original_init(self, *args, **kwargs)

        attrs["__init__"] = __init__
        return super().__new__(cls, name, bases, attrs)


class A(metaclass=AddNewAttr):
    pass


a = A()
print(a.created_at)
print(hasattr(a, "created_at"))
