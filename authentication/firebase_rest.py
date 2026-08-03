import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FIREBASE_API_KEY")

BASE_URL = "https://identitytoolkit.googleapis.com/v1"


def signup(email: str, password: str):
    url = f"{BASE_URL}/accounts:signUp?key={API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    return response.json()


def login(email: str, password: str):
    url = f"{BASE_URL}/accounts:signInWithPassword?key={API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    return response.json()