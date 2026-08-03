import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

firebase_app = None
db = None


def initialize_firebase():
    global firebase_app
    global db

    if firebase_app is None:

        cred = credentials.Certificate("config/firebase_key.json")

        firebase_app = firebase_admin.initialize_app(cred)

        db = firestore.client()

        print("Firebase initialized successfully!")

    return db


def get_db():
    global db

    if db is None:
        initialize_firebase()

    return db


# Initialize automatically when this module is imported
initialize_firebase()