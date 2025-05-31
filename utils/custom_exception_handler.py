from django.core.exceptions import ObjectDoesNotExist, BadRequest
from rest_framework import status


from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.serializers import ReturnDict, ReturnList
from django.utils.encoding import force_str
from rest_framework.exceptions import ErrorDetail
from rest_framework.exceptions import ValidationError, APIException, AuthenticationFailed, PermissionDenied
from django.db import DatabaseError
from django.http import Http404
from rest_framework.exceptions import NotAuthenticated, NotFound


def _get_error_details(data, default_code=None):
    """
    Descend into a nested data structure, forcing any
    lazy translation strings or strings into `ErrorDetail`,
    and return lists as single values where applicable.
    """
    if isinstance(data, (list, tuple)):
        ret = [_get_error_details(item, default_code) for item in data]
        if isinstance(data, ReturnList):
            return ReturnList(ret, serializer=data.serializer)
        return ret[0] if len(ret) == 1 else ret

    elif isinstance(data, dict):
        ret = {
            key: _get_error_details(value, default_code) for key, value in data.items()
        }
        if isinstance(data, ReturnDict):
            return ReturnDict(ret, serializer=data.serializer)
        return ret

    text = force_str(data)
    code = getattr(data, "code", default_code)
    return ErrorDetail(text, code)


# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)
#
#     if response:
#         response = response
#
#     if isinstance(exc, ValidationError) and response is not None:
#         # Format the response using the _get_error_details function
#         response.data = _get_error_details(response.data)
#
#     elif isinstance(exc, KeyError):
#         response = Response(
#             {exc.__str__().strip("'"): ["This Field Is Required"]},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#
#     elif isinstance(exc, ObjectDoesNotExist):
#         response = Response(
#             {"message": exc.__str__()}, status=status.HTTP_404_NOT_FOUND
#         )
#     elif isinstance(exc, RestrictedError):
#         response = Response(
#             {"message": "Removing Not Allowed"}, status=status.HTTP_400_BAD_REQUEST
#         )
#     else:
#         response = Response(
#             {"message": exc.__str__()}, status=status.HTTP_400_BAD_REQUEST
#         )
#
#     return response

def custom_exception_handler(exc, context):
    """
    Custom exception handler to process all types of exceptions and return JSON responses.
    Handles both DRF exceptions and uncaught Python exceptions.
    """
    # Call DRF's default exception handler to get the standard error response.
    response = exception_handler(exc, context)

    errors = []

    if response is not None:
        # Handle DRF exceptions (e.g., ValidationError, AuthenticationFailed, PermissionDenied, etc.)
        if isinstance(exc, ValidationError):
            # Handle validation errors and reformat them properly
            def parse_errors(error_dict, field_prefix=""):
                parsed_errors = []
                for field, value in error_dict.items():
                    field_name = str(field)  # Ensure field is always a string
                    formatted_field = field_name.replace('_', ' ').capitalize() if isinstance(field_name,
                                                                                              str) else field_name

                    if isinstance(value, list):
                        for error in value:
                            if isinstance(error, dict):
                                parsed_errors.extend(parse_errors(error, field_prefix=f"{field_name}."))
                            else:
                                parsed_errors.append(f"{field_prefix}{formatted_field}: {error}")
                    elif isinstance(value, dict):
                        parsed_errors.extend(parse_errors(value, field_prefix=f"{field_name}."))
                    else:
                        parsed_errors.append(f"{field_prefix}{formatted_field}: {value}")
                return parsed_errors

            if isinstance(response.data, dict):
                errors.extend(parse_errors(response.data))
            elif isinstance(response.data, list):
                errors.extend(response.data)

            response.data = {
                "data": errors,
                "message": "Validation error",
                "status": response.status_code,
            }
        elif isinstance(exc, AuthenticationFailed):
            # Handle authentication failure
            response.data = {
                "data": [str(exc)],
                "message": "Authentication failed",
                "status": status.HTTP_401_UNAUTHORIZED,
            }
        elif isinstance(exc, PermissionDenied):
            # Handle permission denial
            response.data = {
                "data": [str(exc)],
                "message": "Permission denied",
                "status": status.HTTP_403_FORBIDDEN,
            }
        elif isinstance(exc, NotAuthenticated):
            # Handle not authenticated
            response.data = {
                "data": [str(exc)],
                "message": "Not authenticated",
                "status": status.HTTP_401_UNAUTHORIZED,
            }
        elif isinstance(exc, Http404):
            # Handle not found error
            response.data = {
                "data": [str(exc)],
                "message": "Not found",
                "status": status.HTTP_404_NOT_FOUND,
            }
        elif isinstance(exc, APIException):
            # Handle API-related exceptions
            response.data = {
                "data": [str(exc)],
                "message": exc.default_detail if hasattr(exc, 'default_detail') else "An error occurred",
                "status": status.HTTP_400_BAD_REQUEST,
            }
        elif isinstance(exc, DatabaseError):
            # Handle database-related errors
            response.data = {
                "data": [str(exc)],
                "message": "Database error",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        elif isinstance(exc, ObjectDoesNotExist):
            # Handle Django's ObjectDoesNotExist (e.g., querying an object that doesn't exist)
            response.data = {
                "data": [str(exc)],
                "message": "Requested object does not exist",
                "status": status.HTTP_404_NOT_FOUND,
            }
    else:
        # Handle non-DRF exceptions (uncaught exceptions like KeyError, ValueError, etc.)
        error_message = "An unexpected server error occurred."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if isinstance(exc, KeyError):
            error_message = "A required key is missing."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, ValueError):
            error_message = "Invalid value provided."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, TypeError):
            error_message = "A type error occurred."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, AttributeError):
            error_message = "An invalid attribute was accessed."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, ImportError):
            error_message = "An import error occurred."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, IndexError):
            error_message = "Index out of range."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, IOError):
            error_message = "Input/Output error occurred."
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        elif isinstance(exc, OverflowError):
            error_message = "Numerical overflow error."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, ZeroDivisionError):
            error_message = "Cannot divide by zero."
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, ObjectDoesNotExist):
            error_message = "Data not found"
            status_code = status.HTTP_404_NOT_FOUND

        # Create a JSON response for non-DRF exceptions
        response = Response(
            {
                "data": [str(exc)],
                "message": error_message,
                "status": status_code,
            },
            status=status_code,
        )

    return response
