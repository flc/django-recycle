try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

from django.utils.decorators import method_decorator, available_attrs
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponseBadRequest, Http404, HttpResponseForbidden


def view_decorator(orig_dec):
    """
        Convert the provided decorator to one that can be applied to a view
        class (ie. automatically decorates dispatch)
    """

    # We're going to be applying a regular decorator to a method, so the first
    # step is to convert it to a method decorator.
    method_dec = method_decorator(orig_dec)

    # This is the decorator we're actually going to return. Since we're
    # returning a class decorator, it takes a single argument, the class
    # that it's decorating. It therefore returns this as well.
    def dec(cls):
        # We're about to change what cls.dispatch refers to, so we need to
        # keep a reference to the original dispatch around so that we can
        # call it later.
        orig_dispatch = cls.dispatch

        def _dispatch(self, *args, **kwargs):
            # Right - decorate the original dispatch method using our new,
            # method-ised version of the decorator we were passed in to start
            # with
            decorated = method_dec(orig_dispatch)

            # Finally, we can call the decorated dispatch() method.
            return decorated(self, *args, **kwargs)

        # Replace the original dispatch with our new dispatch function. We
        # kept a reference to the old dispatch method earlier, in a closure.
        cls.dispatch = _dispatch
        return cls
    return dec


def ajax_required(view_func):
    """Required the view is only accessed via AJAX."""

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest()
    return _wrapped_view


def remove_uploadhandlers(*handler_classes):
    """Removes the specified upload handlers for the decorated view.

    Usage:

    from django.core.files.uploadhandler import MemoryFileUploadHandler
    from yourapp.uploadhandler import YourUploadHandler

    @remove_uploadhandlers(MemoryFileUploadHandler)
    def view(request):
        ...

    @remove_uploadhandlers(YourUploadHandler, MemoryFileUploadHandler)
    def view(request):
        ...


    Related docs:
        https://docs.djangoproject.com/en/dev//topics/http/file-uploads/#modifying-upload-handlers-on-the-fly
    """
    handler_classes = tuple(handler_classes)

    def decorator(view):

        @wraps(view, assigned=available_attrs(view))
        @csrf_exempt
        def wrapped_view(request, *args, **kwargs):
            upload_handlers = request.upload_handlers
            new_handlers = [handler for handler in upload_handlers
                            if not isinstance(handler, handler_classes)]
            request.upload_handlers = new_handlers

            response = _upload_file_view(request, *args, **kwargs)
            return response

        @csrf_protect
        def _upload_file_view(request, *args, **kwargs):
            response = view(request, *args, **kwargs)
            return response

        return wrapped_view

    return decorator


def staff_or_404(view_func):
    def _check(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            raise Http404
    return wraps(view_func)(_check)


def user_passes_test_or_response(test_func, response=None):
    if response is None:
        response = HttpResponseForbidden()

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return response
        return _wrapped_view

    return decorator


def permission_required_or_response(perm, *args, **kwargs):
    return user_passes_test_or_response(
        lambda u: u.has_perm(perm), *args, **kwargs
        )
