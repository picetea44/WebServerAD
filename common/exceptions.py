
class BaseAppException(Exception):

    status_code = 500
    default_message = "An error occurred"

    def __init__(self, message=None, status_code=None):
        self.message = message if message else self.default_message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundException(BaseAppException):

    status_code = 404
    default_message = "The requested resource was not found"


class PermissionDeniedException(BaseAppException):

    status_code = 403
    default_message = "You don't have permission to perform this action"


class ValidationException(BaseAppException):

    status_code = 400
    default_message = "Invalid input data"


class AuthenticationException(BaseAppException):

    status_code = 401
    default_message = "Authentication failed"