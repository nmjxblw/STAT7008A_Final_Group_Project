class SingletonMeta(type):
    """
    A metaclass for creating singleton classes.
    Ensures that only one instance of a class exists.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
