import functools
import inspect
import os
import time


class Logging:
    def __init__(self, path: str = '../../logs'):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def log_funs(self):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                error = None
                result = None
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    error = e
                    raise 
                finally:
                    with open(os.path.join(self.path, f"{func.__name__}.log"), "a") as f:
                        f.write(
                            f" Function {func.__name__} worked at time: "
                            f"{time.strftime('%Y-%m-%d %H:%M:%S')} called with "
                            f"arguments: {args}, {kwargs}, result: {result}, "
                            f"error: {error}.\n\n\n"
                        )
                return result
            return wrapper
        return decorator

    def log_class(self, all_funs=False):
        def class_decorator(cls):
            for name, attr in vars(cls).items():
                if isinstance(attr, staticmethod):
                    setattr(cls, name, staticmethod(self.log_funs()(attr.__func__)))
                elif isinstance(attr, classmethod):
                    setattr(cls, name, classmethod(self.log_funs()(attr.__func__)))
                elif inspect.isfunction(attr) and (all_funs or not name.startswith("__")):
                    setattr(cls, name, self.log_funs()(attr))
            return cls
        return class_decorator

    def write_error(self, error_message: str, file_name: str = "error.log"):
        with open(os.path.join(self.path, file_name), "a") as f:
            f.write(
                f"Error occurred at time: {time.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"error message: {error_message}.\n\n\n"
            )