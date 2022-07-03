from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler
from django.http import JsonResponse


def default_handler(exc, context):
    # https://www.django-rest-framework.org/api-guide/exceptions/
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = drf_exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        if not response.data.get("detail"):
            response.data = {
                "detail": response.data,
                "status_code": response.status_code,
            }
        else:
            response.data["status_code"] = response.status_code

    return response


def bad_request(request, exception, *args, **kwargs):
    """
    Generic 400 error handler.
    """
    data = {"error": "Bad Request (400)"}
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
