import re

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def validate_email(email: str):
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("Invalid email format.")

    return email.strip().lower()


def validate_password(password: str):
    if len(password) < 6:
        raise ValueError(
            "Password must contain at least 6 characters."
        )

    return password