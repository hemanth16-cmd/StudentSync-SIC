class AuthenticationError(Exception):
    """Base authentication exception."""
    pass


class ValidationError(AuthenticationError):
    pass


class UserAlreadyExists(AuthenticationError):
    pass


class InvalidCredentials(AuthenticationError):
    pass


class UserNotFound(AuthenticationError):
    pass


class FirebaseError(AuthenticationError):
    pass