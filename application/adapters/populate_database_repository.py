import csv
import sqlite3
import os
from dotenv import load_dotenv


from application.adapters.orm import metadata
from sqlalchemy import create_engine

tags = dict()


def article_record_generator():
    with open('../data/news_articles.csv') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            article_data = row
            article_key = article_data[0]

            # Strip any leading/trailing white space from data read.
            article_data = [item.strip() for item in article_data]

            number_of_tags = len(article_data) - 6
            article_tags = article_data[-number_of_tags:]

            # Add and new tags; associate the current article with tags.
            for tag in article_tags:
                if tag not in tags.keys():
                    tags[tag] = list()
                tags[tag].append(article_key)

            del article_data[-number_of_tags:]

            yield article_data


def get_tag_records():
    tag_records = list()
    tag_key = 0

    for tag in tags.keys():
        tag_key = tag_key + 1
        tag_records.append((tag_key, tag))
    return tag_records


def article_tags_generator():
    article_tags_key = 0
    tag_key = 0

    for tag in tags.keys():
        tag_key = tag_key + 1
        for article_key in tags[tag]:
            article_tags_key = article_tags_key + 1
            yield article_tags_key, article_key, tag_key


def generic_generator(filename):
    with open(filename) as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            print(row)
            yield row


def main():
    load_dotenv(dotenv_path='..\\..\\.env')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    COVID_INSTALL_PATH = os.getenv('COVID_INSTALL_PATH')

    DATABASE_URI = os.path.join(COVID_INSTALL_PATH, SQLALCHEMY_DATABASE_URI)
    print("Loaded vars", DATABASE_URI)


    # Read URI from
    engine = create_engine('sqlite://../data/covid-19.db')

    # Create tables.
    metadata.create_all(engine)

    conn = sqlite3.connect('foo2.db')
    cursor = conn.cursor()

    insert_articles = """
        INSERT INTO articles (
        id, date, title, first_para, hyperlink, image_hyperlink)
        VALUES (?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_articles, article_record_generator())

    insert_tags = """
        INSERT INTO tags (
        id, name)
        VALUES (?, ?)"""
    cursor.executemany(insert_tags, get_tag_records())

    insert_article_tags = """
        INSERT INTO article_tags (
        id, article_id, tag_id)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_article_tags, article_tags_generator())

    insert_users = """
        INSERT INTO users (
        id, username, password)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_users, generic_generator('../data/users.csv'))

    insert_comments = """
        INSERT INTO comments (
        id, user_id, article_id, comment, timestamp)
        VALUES (?, ?, ?, ?, ?)"""
    cursor.executemany(insert_comments, generic_generator('../data/comments.csv'))

    conn.commit()
    conn.close()


main()
