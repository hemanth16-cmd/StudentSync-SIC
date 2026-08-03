try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
except ImportError:
    firebase_admin = None
    credentials = None
    firestore = None

firebase_app = None
db = None


def initialize_firebase():
    global firebase_app
    global db

    if firebase_admin is None:
        return None

    if firebase_app is None:
        try:
            cred = credentials.Certificate("config/firebase_key.json")
            firebase_app = firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("Firebase initialized successfully!")
        except Exception as e:
            print(f"Firebase init notice: {e}")

    return db


def get_db():
    global db

    if db is None and firebase_admin is not None:
        initialize_firebase()

    return db


# Initialize safely
if firebase_admin is not None:
    try:
        initialize_firebase()
    except Exception:
        pass