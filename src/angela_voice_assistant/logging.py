import os
import time

class loging():
    def __init__(self, path:str='../../logs'):
        '''
        Initializes the logging class with a specified path for log files.
        
        Args:
            path (str): The directory path where log files will be stored.
        '''
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def log_funs(self):
        '''
        Decorator for logging function calls, their arguments, results, and any exceptions raised.
        
        Args: None
        '''
        def decorator(func):
            def wrapper(*args, **kwargs):
                error = None
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    result = None
                    error = e
                with open(os.path.join(self.path, f"{func.__name__}.log"), "a") as f:
                    f.write(f" Function {func.__name__} worked at time: {time.strftime('%Y-%m-%d %H:%M:%S')} called with arguments: {args}, {kwargs}, result: {result}, error: {error}.\n\n\n")
                return result
            return wrapper
        return decorator

    def log_class(self, all_funs=False):
        '''
        Class decorator for logging all methods of a class. It applies the log_funs decorator to
        each method of the class, logging their calls, arguments, results, and any exceptions raised.
        
        Args:
            all_funs (bool): If True, logs all methods including private ones. If False, logs only public methods.
        '''
        def class_decorator(cls):
            info = vars(cls)
            for name, method in info.items():
                if callable(method) and (all_funs or not name.startswith("__")):
                    setattr(cls, name, self.log_funs()(method))
            return cls
        return class_decorator
