from dataclasses import dataclass


@dataclass
class User:
    uid: str
    email: str