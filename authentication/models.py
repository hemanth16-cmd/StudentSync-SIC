from dataclasses import dataclass


@dataclass
class User:
    uid: str
    name: str
    email: str
    role: str = "student"

    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            uid=data["uid"],
            name=data["name"],
            email=data["email"],
            role=data.get("role", "student"),
        )