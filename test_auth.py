from authentication.auth_service import AuthService

user = AuthService.signup(
    "Shawn",
    "st.tarancr7@gmail.com",   # or any unused email
    "228801"
)

print(user)