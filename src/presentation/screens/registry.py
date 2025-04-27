import re

handlers = {}

def register(name):
    def decorator(func):
        handlers[name] = func
        return func
    return decorator

def register_pattern(pattern):
    def decorator(func):
        handlers[re.compile(pattern)] = func
        return func
    return decorator

def resolve_handler(data):
    for key, handler in handlers.items():
        if isinstance(key, str):
            if key == data:
                return handler, None
        elif hasattr(key, "match"):
            match = key.match(data)
            if match:
                return handler, match
    return None, None
