import csv
import os
from datetime import date, datetime

from application.adapters.repository import MemoryRepository
from application.domain.model import Article, Tag, User, make_tag_association, make_comment


def read_csv_file(filename: str):
    with open(filename) as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_articles_and_tags(data_path: str, repo: MemoryRepository):
    tags = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'news_articles.csv')):

        article_key = int(data_row[0])
        number_of_tags = len(data_row) - 6
        article_tags = data_row[-number_of_tags:]

        # Add any new tags; associate the current article with tags.
        for tag in article_tags:
            if tag not in tags.keys():
                print('Adding tag *', tag, '*')
                tags[tag] = list()
            tags[tag].append(article_key)

        del data_row[-number_of_tags:]

        # Create Article object.
        article = Article(
            date=date.fromisoformat(data_row[1]),
            title=data_row[2],
            first_para=data_row[3],
            hyperlink=data_row[4],
            image_hyperlink=data_row[5],
            id=article_key
        )

        # Add the Article to the repository.
        repo.add_article(article)

    # Create Tag objects, associate them with Articles and add them to the repository.
    for tag_name in tags.keys():
        tag = Tag(tag_name)
        for article_id in tags[tag_name]:
            article = repo.get_article(article_id)
            make_tag_association(article, tag)
        repo.add_tag(tag)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=data_row[2]
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_comments(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'comments.csv')):
        print('Looking up user with name ', data_row[1])
        comment = make_comment(
            comment_text=data_row[3],
            user=users[data_row[1]],
            article=repo.get_article(int(data_row[2])),
            timestamp=datetime.fromisoformat(data_row[4])
        )
        repo.add_comment(comment)


def make_repo(data_path: str):
    # Create the repository.
    repo = MemoryRepository()

    # Load articles and tags into the repository.
    load_articles_and_tags(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_comments(data_path, repo, users)

    return repo
