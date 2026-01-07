from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, username, password, email="") -> None:
        self.id = id
        self.username = username
        self.password = password
        self.email = email

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

    @classmethod
    def convert_password(self, password):
        return generate_password_hash(password)
