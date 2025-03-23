
handlers = {}

def register(name):
    def decorator(func):
        handlers[name] = func
        return func
    return decorator
