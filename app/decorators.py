from django.shortcuts import redirect


def redirect_if_not_ajax(url: str):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not request.is_ajax():
                return redirect(url)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
