# с помощью метакласса


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwds):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwds)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonFromMeta(metaclass=MetaSingleton):
    def __init__(self, value):
        self.value = value


# с помощью метода __new__


class SingletonFromNew:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonFromNew, cls).__new__(cls)
        return cls._instance

    def __init__(self, value=None):
        if not hasattr(self, "initialized"):
            self.value = value
            self.initialized = True


# Через механизм импортов (глобальная переменная)
class SingletonFromImport:
    def __init__(self, value):
        self.value = value


singleton_instance = SingletonFromImport()
