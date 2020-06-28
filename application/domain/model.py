from datetime import datetime as dt


class User:
    """Data model for user accounts."""

    def __init__(self, username, email, bio='', created=dt.now(), admin=False):
        self.username = username
        self.email = email
        self.created = created
        self.bio = bio
        self.admin = admin

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.username == self.username

    def __hash__(self):
        return hash(self.username)
