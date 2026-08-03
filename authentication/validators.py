import re

from authentication.exceptions import ValidationError


EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def validate_email(email: str):
    if not re.match(EMAIL_PATTERN, email):
        raise ValidationError("Invalid email address.")


def validate_password(password: str):
    if len(password) < 6:
        raise ValidationError(
            "Password must contain at least 6 characters."
        )


def validate_name(name: str):
    if len(name.strip()) < 2:
        raise ValidationError(
            "Name must contain at least 2 characters."
        )