"""Application routes."""
from flask import request, render_template, make_response, redirect, url_for, flash
from flask import current_app as app

from datetime import date

from application import uow
from application.forms.forms import CommentForm
from application.service_layer.services import add_user, NameNotUniqueException, get_articles_by_date, \
    get_first_article, get_last_article, get_article, add_comment


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', title="COVID!!!")


@app.route('/articles', methods=['GET'])
def articles_for_date():
    # Read query parameters.
    target_date = request.args.get('date')
    article_to_show_comments = request.args.get('view_comments_for')

    # Fetch the first and last articles in the series.
    first_article = get_first_article(uow)
    last_article = get_last_article(uow)

    if target_date is None:
        # No date query parameter, so return articles from day 1 of the series.
        target_date = first_article['date']
    else:
        # Convert target_date from string to date.
        target_date = date.fromisoformat(target_date)

    if article_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent article id.
        article_to_show_comments = -1
    else:
        # Convert article_to_show_comments from string to int.
        article_to_show_comments = int(article_to_show_comments)

    # Fetch article(s) for the target date. This call also returns the previous and next dates for articles immediately
    # before and after the target date.
    articles, previous_date, next_date = get_articles_by_date(target_date, uow)

    first_article_url = None
    last_article_url = None
    next_article_url = None
    prev_article_url = None

    if len(articles) > 0:
        # There's at least one article for the target date.
        if previous_date is not None:
            # There are articles on a previous date, so generate URLs for the 'previous' and 'first' navigation buttons.
            prev_article_url = url_for('articles_for_date', date=previous_date.isoformat())
            first_article_url = url_for('articles_for_date', date=first_article['date'].isoformat())

        # There are articles on a subsequent date, so generate URLs for the 'next' and 'last' navigation buttons.
        if next_date is not None:
            next_article_url = url_for('articles_for_date', date=next_date.isoformat())
            last_article_url = url_for('articles_for_date', date=last_article['date'].isoformat())

        # Construct urls for viewing article comments and adding comments.
        for article in articles:
            article['view_comment_url'] = url_for('articles_for_date', date=target_date, view_comments_for=article['id'])
            article['add_comment_url'] = url_for('comment_on_article', article=article['id'])

        # Generate the webpage to display the articles.
        return render_template(
            'articles_by_time.html',
            title='Articles',
            date=target_date.strftime('%A %B %e %Y'),
            articles=articles,
            first_article_url=first_article_url,
            last_article_url=last_article_url,
            prev_article_url=prev_article_url,
            next_article_url=next_article_url,
            show_comments_for_article=article_to_show_comments
        )

    # No articles to show, so return the homepage.
    return render_template('home.html', title="COVID!!!")


@app.route('/comment', methods=['GET', 'POST'])
def comment_on_article():
    # will be from a session eventually ...
    USERNAME = 'thorke'

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an article id, when subsequently called with a HTTP POST request, the article id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the article id, representing the commented article, from the form.
        article_id = int(form.article_id.data)

        # Use the service layer to store the new comment.
        add_comment(article_id, form.comment.data, USERNAME, uow)

        # Retrieve the article in dict form.
        article = get_article(article_id, uow)

        # Cause the web browser to display the page of all articles that have the same date as the commented article,
        # and display all comments, including the new comment.
        return redirect(url_for('articles_for_date', date=article['date'], view_comments_for=article_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the article id, representing the article to comment, from a query parameter of the GET request.
        article_id = int(request.args.get('article'))

        # Store the article id in the form.
        form.article_id.data = article_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the article id of the article being commented from the form.
        article_id = form.article_id.data

    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    article = get_article(article_id, uow)
    return render_template(
        'comment_on_article.html',
        title='Edit article',
        article=article,
        form=form,
        handler_url=url_for('comment_on_article')
    )
