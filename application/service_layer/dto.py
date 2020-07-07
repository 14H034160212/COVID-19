from typing import List

from application.domain.model import Article, Comment, Tag, User


# DTO might be thr wrong term - they're not transferred over the network ??

# ===========================================
# Functions to convert model entities to DTOs
# ===========================================

def article_to_dto(article: Article):
    article_dto = {
        'id': article.id,
        'date': article.date,
        'title': article.title,
        'first_para': article.first_para,
        'hyperlink': article.hyperlink,
        'image_hyperlink': article.image_hyperlink,
        'comments': comments_to_dto(article.comments),
        'tags': tags_to_dto(article.tags)
    }
    return article_dto


def articles_to_dto(articles: List[Article]):
    return [article_to_dto(article) for article in articles]


def comment_to_dto(comment: Comment):
    comment_dto = {
        'username': comment.user.username,
        'article_id': comment.article.id,
        'comment_text': comment.comment,
        'timestamp': comment.timestamp
    }
    return comment_dto


def comments_to_dto(comments: List[Comment]):
    return [comment_to_dto(comment) for comment in comments]


def tag_to_dto(tag: Tag):
    tag_dto = {
        'name': tag.tag_name,
        'tagged_articles': [article.id for article in tag.tagged_articles]
    }
    return tag_dto


def tags_to_dto(tags: List[Tag]):
    return [tag_to_dto(tag) for tag in tags]


def user_to_dto(user: User):
    user_dto = {
        'username': user.username,
        'password': user.password
    }


# ===========================================
# Functions to convert DTOs to model entities
# ===========================================

def dto_to_article(dto):
    article = Article(dto.id, dto.date, dto.title, dto.first_para, dto.hyperlink)
    # Note there's no comments or tags.
    return article
