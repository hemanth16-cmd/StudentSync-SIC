from authentication.auth_service import AuthService
from authentication.session import Session

AuthService.login(
    "st.tarancr7@gmail.com",
    "228801"
)

print(Session.current_user())

print(Session.is_logged_in())

Session.logout()

print(Session.is_logged_in())