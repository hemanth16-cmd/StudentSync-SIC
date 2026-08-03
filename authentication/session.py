from authentication.models import User


class Session:
    _current_user: User | None = None

    @classmethod
    def login(cls, user: User):
        cls._current_user = user

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def current_user(cls):
        return cls._current_user

    @classmethod
    def is_logged_in(cls):
        return cls._current_user is not None