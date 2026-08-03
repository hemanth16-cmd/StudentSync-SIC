class AuthenticationError(Exception):
    """Base authentication exception."""
    pass


class InvalidEmailError(AuthenticationError):
    pass


class WeakPasswordError(AuthenticationError):
    pass


class UserAlreadyExistsError(AuthenticationError):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class UserNotFoundError(AuthenticationError):
    pass