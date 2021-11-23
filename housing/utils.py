def error_handler(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        return result
    except (AttributeError, IndexError, KeyError) as e:
        # print(e.__class__.__name__, e, func.__name__)
        return None
