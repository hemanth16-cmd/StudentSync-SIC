from authentication.auth_service import AuthService

print(AuthService.is_logged_in())

user = AuthService.login(
    "st.tarancr7@gmail.com",
    "228801"
)

print(AuthService.current_user())
print(AuthService.is_logged_in())

AuthService.logout()

print(AuthService.current_user())
print(AuthService.is_logged_in())