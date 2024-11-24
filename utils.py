from hashlib import sha256

def d(v):
    print(v)
    return v

def digest_password(password):
    return sha256(password.encode('utf-8')).hexdigest()


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
