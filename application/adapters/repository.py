import abc
from typing import List

from sqlalchemy import desc, asc

from application.domain.model import User, Article, Tag, Comment

from datetime import date

from bisect import bisect, bisect_left, insort_left


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        """" Adds a User to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username) -> User:
        """ Returns the User named username from the repository.

        If there is no User with the given username, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_article(self, article: Article):
        """ Adds an Article to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_article(self, id: int) -> Article:
        """ Returns Article with id from the repository.

        If there is no Article with the given id, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_articles_by_date(self, target_date: date) -> List[Article]:
        """ Returns a list of Articles that were published on target_date.

        If there are no Articles on the given date, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_articles(self):
        """ Returns the number of Articles in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_first_article(self) -> Article:
        """ Returns the first Article, ordered by date, from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_last_article(self) -> Article:
        """ Returns the last Article, ordered by date, from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_articles_by_id(self, id_list):
        """ Returns a list of Articles, whose ids match those in id_list, from the repository.

        If there are no matches, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_article_ids_for_tag(self, tag_name: str):
        """ Returns a list of ids representing Articles that are tagged by tag_name.

        If there are Articles that are tagged by tag_name, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_date_of_previous_article(self, article: Article):
        """ Returns the date of an Article that immediately precedes article.

        If article is the first Article in the repository, this method returns None because there are no Articles
        on a previous date.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_date_of_next_article(self, article: Article):
        """ Returns the date of an Article that immediately follows article.

        If article is the last Article in the repository, this method returns None because there are no Articles
        on a later date.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_tag(self, tag: Tag):
        """ Adds a Tag to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_tags(self) -> List[Tag]:
        """ Returns the Tags stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_comment(self, comment: Comment):
        """ Adds a Comment to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_comments(self):
        """ Returns the Comments stored in the repository. """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self._session = session

    def add_user(self, user: User):
        self._session.add(user)

    def get_user(self, username) -> User:
        user = None
        try:
            user = self._session.query(User).filter_by(_username=username).one()
        except:  # What's the type of Error?
            pass

        return user

    def add_article(self, article: Article):
        raise NotImplementedError

    def get_article(self, id: int) -> Article:
        article = None
        try:
            article = self._session.query(Article).filter(Article._id==id).one()
        except:  # what's the error type?
            print('Got ORM exception, was asked for id ', id)

        return article

    def get_articles_by_date(self, target_date: date) -> List[Article]:
        if target_date is None:
            return self._session.query(Article).all()
        else:
            # Return articles matching target_date; return an empty list if there are no matches.
            return self._session.query(Article).filter(Article._date == target_date).all()

    def get_number_of_articles(self):
        return self._session.query(Article).count()

    def get_first_article(self):
        return self._session.query(Article).first()

    def get_last_article(self):
        return self._session.query(Article).order_by(desc(Article._id)).first()

    def get_articles_by_id(self, id_list):
        return self._session.query(Article).filter(Article._id.in_(id_list)).all()

    def get_article_ids_for_tag(self, tag_name: str):
        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session.execute('SELECT id FROM tags WHERE name = :tag_name', {'tag_name': tag_name}).fetchone()
        tag_id = row[0]

        article_ids = self._session.execute(
            'SELECT article_id FROM article_tags WHERE tag_id = :tag_id ORDER BY article_id ASC',
            {'tag_id': tag_id}
        ).fetchall()
        article_ids = [id[0] for id in article_ids]

        return article_ids

    def get_date_of_previous_article(self, article: Article):
        """ Returns the closest previous date of an article to the argument. If there are no previous articles,
        this method returns None."""
        result = None
        prev = self._session.query(Article).filter(Article._date < article.date).order_by(desc(Article._date)).first()

        if prev is not None:
            result = prev.date
        return result

    def get_date_of_next_article(self, article: Article):
        result = None
        next = self._session.query(Article).filter(Article._date > article.date).order_by(asc(Article._date)).first()

        if next is not None:
            result = next.date
        return result

    def get_tags(self) -> List[Tag]:
        return self._session.query(Tag).all()

    def add_tag(self, tag: Tag):
        raise NotImplementedError

    def get_comments(self):
        raise NotImplementedError

    def add_comment(self, comment: Comment):
        self._session.add(comment)


class MemoryRepository(AbstractRepository):
    # Articles ordered by date, not id. id is assumed unique.

    def __init__(self):
        self._articles = list()
        self._articles_index = dict()
        self._tags = list()
        self._users = list()
        self._comments = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_article(self, article: Article):
        insort_left(self._articles, article)
        self._articles_index[article.id] = article

    def get_article(self, id: int) -> Article:
        article = None

        try:
            article = self._articles_index[id]
        except KeyError:
            pass  # Ignore exception and return None.

        return article

    def get_articles_by_date(self, target_date: date) -> List[Article]:
        target_article = Article(
            date=target_date,
            title=None,
            first_para=None,
            hyperlink=None,
            image_hyperlink=None
        )
        matching_articles = list()

        try:
            index = self.article_index(target_article)
            for article in self._articles[index:None]:
                if article.date == target_date:
                    matching_articles.append(article)
                else:
                    break
        except ValueError:
            # No articles for specified date. Simply return an empty list.
            pass

        return matching_articles

    def get_number_of_articles(self):
        return len(self._articles)

    def get_first_article(self):
        article = None

        if len(self._articles) > 0:
            article = self._articles[0]
        return article

    def get_last_article(self):
        article = None

        if len(self._articles) > 0:
            article = self._articles[-1]
        return article

    def get_articles_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Article ids in the repository.
        existing_ids = [id for id in id_list if id in self._articles_index]

        # Fetch the Articles.
        articles = [self._articles_index[id] for id in existing_ids]
        return articles

    def get_article_ids_for_tag(self, tag_name: str):
        # Linear search, to find the first occurrence of a Tag with the name tag_name.
        tag = next((tag for tag in self._tags if tag.tag_name == tag_name), None)

        # Retrieve the ids of articles associated with the Tag.
        if tag is not None:
            article_ids = [article.id for article in tag.tagged_articles]
        else:
            # No Tag with name tag_name, so return an empty list.
            article_ids = list()

        return article_ids

    def get_date_of_previous_article(self, article: Article):
        previous_date = None

        try:
            index = self.article_index(article)
            for stored_article in reversed(self._articles[0:index]):
                if stored_article.date < article.date:
                    previous_date = stored_article.date
                    break
        except ValueError:
            # No earlier articles, so return None.
            pass

        return previous_date

    def get_date_of_next_article(self, article: Article):
        next_date = None

        try:
            index = self.article_index(article)
            for stored_article in self._articles[index + 1:len(self._articles)]:
                if stored_article.date > article.date:
                    next_date = stored_article.date
                    break
        except ValueError:
            # No subsequent articles, so return None.
            pass

        return next_date

    def add_tag(self, tag: Tag):
        self._tags.append(tag)

    def get_tags(self) -> List[Tag]:
        return self._tags

    def add_comment(self, comment: Comment):
        self._comments.append(comment)

    def get_comments(self):
        return self._comments

    # Helper method to return article index.
    def article_index(self, article: Article):
        index = bisect_left(self._articles, article)
        if index != len(self._articles) and self._articles[index].date == article.date:
            return index
        raise ValueError

