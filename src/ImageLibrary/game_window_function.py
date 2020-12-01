
def game_window_function(func):
    def wrapper(self, *args, **kwargs):
        if "window" not in kwargs:
            kwargs["window"] = None
        if "wind_index" not in kwargs:
            kwargs["wind_index"] = 1
        window = self._get_window(kwargs["window"], kwargs["wind_index"])
        func_name = func.__name__
        wind_func = getattr(window, func_name)
        assert wind_func is not None, "Function {} not found in game_window".format(func_name)
        del kwargs["window"]
        del kwargs["wind_index"]
        return wind_func(*args, **kwargs)
    return wrapper