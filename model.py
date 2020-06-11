from typing import List
from datetime import date

class User:
    def __init__(
        self, username: str, password: str
    ):
        self._username = username
        self._password = password

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

# To do: assign timestamp when created.
# Make frozen?
class Comment:
    def __init__(
        self, user: User, article: Article, comment : str
    ):
        self._user = user
        self._article = article
        self._comment = comment
        self._timestamp = None

    @property
    def user() -> User:
        return _user

    @property
    def article() -> Article:
        return _article

class Article:
    def __init__(
        self, date: date, title: str, first_para : str, hyperlink: str, image_hyperlink
    ):
        self._date = date
        self._title = title
        self._first_para = first_para
        self._hyperlink = hyperlink
        self._image_hyperlink = image_hyperlink
    
    @property
    def date() -> date:
        return self._date

    @property
    def title() -> str:
        return self._title
    
    @property
    def first_para() -> str:
        return self._first_para

    @property
    def hyperlink() -> str:
        return self._hyperlink

    @property
    def image_hyperlink() -> str:
        return self._image_hyperlink

class Tag:
    def __init__(
        self, tag_name: str
    ):
        self._tag_name = tag_name

    @property
    def tag_name() -> str:
        return self._tag_name
