from authentication.auth_service import AuthService

email = input("Email: ")
password = input("Password: ")

try:
    user = AuthService.signup(email, password)

    print("\nUser created successfully!")
    print(user)

except Exception as e:
    print("\nSignup failed:")
    print(e)