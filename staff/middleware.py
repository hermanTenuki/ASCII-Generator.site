from inspect import getmodule
import django.contrib.admin.sites
from django.http import Http404
from django.conf import settings


class RestrictStaffToAdminMiddleware:
    """
    A middleware that restricts staff members access to administration panels.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        module = getmodule(view_func)
        if (module is django.contrib.admin.sites) and (not request.user.is_staff) and (not settings.DEBUG):
            raise Http404
